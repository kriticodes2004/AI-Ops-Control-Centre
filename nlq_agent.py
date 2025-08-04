import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_ollama import OllamaLLM


df = pd.read_csv("predictions_cache.csv")
print(f"✅ Loaded {len(df)} predictions for NLQ queries")


tickets = pd.read_csv("jira_tickets.csv")

if "Created" not in tickets.columns:
    raise KeyError("⚠️ 'Created' column missing in jira_tickets.csv")

tickets["Created"] = pd.to_datetime(tickets["Created"], errors='coerce')

# Handle missing Resolved column safely
if "Resolved" not in tickets.columns:
    tickets["Resolved"] = pd.NaT
else:
    tickets["Resolved"] = pd.to_datetime(tickets["Resolved"], errors='coerce')

# Fill missing resolved dates with current time
tickets["Resolved"] = tickets["Resolved"].fillna(pd.Timestamp.now())

# ---- Force timezone-naive for both columns ----
tickets["Created"] = tickets["Created"].dt.tz_localize(None)
tickets["Resolved"] = tickets["Resolved"].dt.tz_localize(None)

# Calculate SLA time (hours)
tickets["Time_To_Resolve_Hours"] = (
    (tickets["Resolved"] - tickets["Created"]).dt.total_seconds() / 3600
)

# SLA breach column (SLA = 4 hours)
tickets["Breach_Status"] = tickets["Time_To_Resolve_Hours"].apply(
    lambda x: "Breached SLA" if x > 4 else "Within SLA"
)

# Detect ticket ID columns
ticket_id_col_tickets = next((col for col in tickets.columns if "ticket" in col.lower() or "key" in col.lower()), None)
ticket_id_col_preds = next((col for col in df.columns if "ticket" in col.lower() or "key" in col.lower()), None)

if not ticket_id_col_tickets or not ticket_id_col_preds:
    raise KeyError("⚠️ Could not detect Ticket ID column in one of the files.")

merged = pd.merge(
    tickets,
    df[[ticket_id_col_preds, "Prediction"]],
    left_on=ticket_id_col_tickets,
    right_on=ticket_id_col_preds,
    how="left"
)


llm = OllamaLLM(model="llama2:7b-chat")
agent = create_pandas_dataframe_agent(
    llm, merged, verbose=False, allow_dangerous_code=True
)

print("\n🤖 NLQ Agent ready! Type 'exit' to quit.\n")

def show_graph(chart_type="sla"):
    plt.figure(figsize=(8, 5))
    if chart_type == "sla":
        plot_df = merged.groupby("Breach_Status").size()
        plot_df.plot(kind="bar", color=["green", "red"])
        plt.title("SLA Breach vs Within SLA")
        plt.ylabel("Number of Tickets")
    else:
        col = next((c for c in merged.columns if "group" in c.lower()), None)
        if col:
            plot_df = merged.groupby(col).size().sort_values(ascending=False)
            plot_df.plot(kind="bar", color="blue")
            plt.title("Tickets by Assignment Group")
            plt.ylabel("Count")
    plt.tight_layout()
    plt.show()


while True:
    query = input("\n🔎 Query: ").strip().lower()
    if query in ["exit", "quit"]:
        print("👋 Exiting NLQ agent.")
        break

    if query.startswith("what is"):
        ticket_id = query.replace("what is", "").strip().upper()
        result = merged[merged[ticket_id_col_preds].astype(str).str.upper() == ticket_id]
        if not result.empty:
            print(result[[ticket_id_col_preds, "Prediction", "Breach_Status"]])
        else:
            print("⚠️ Ticket not found.")

    elif "sla" in query and ("breach" in query or "breached" in query):
        breached_count = (merged["Breach_Status"] == "Breached SLA").sum()
        print(f"📌 SLA breached tickets: {breached_count}")

    elif "graph" in query or "chart" in query:
        if "sla" in query:
            show_graph("sla")
        else:
            show_graph("group")

   
    else:
        try:
            response = agent.invoke({"input": query})
            print("\n🤖 AI Summary:\n", response["output"], "\n")
        except Exception as e:
            print("⚠️ LLM could not process this query:", e)
