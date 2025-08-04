import pandas as pd
from langchain_ollama import OllamaLLM
from tqdm import tqdm
import os

# -----------------------------
# 1️⃣ Load tickets
# -----------------------------
csv_file = "jira_tickets.csv"
df = pd.read_csv(csv_file)
print(f"✅ Loaded {len(df)} tickets from {csv_file}")

# Auto-detect ticket ID column
ticket_id_col = next((col for col in df.columns if "ticket" in col.lower()), None)
if ticket_id_col is None:
    raise KeyError("No Ticket ID column found in CSV!")
print(f"🔹 Detected Ticket ID column: {ticket_id_col}")

# -----------------------------
# 2️⃣ Load cache (if exists)
# -----------------------------
cache_file = "predictions_cache.csv"
cache = {}
if os.path.exists(cache_file):
    cached_df = pd.read_csv(cache_file)
    cached_id_col = next((col for col in cached_df.columns if "ticket" in col.lower()), None)
    if cached_id_col:
        cache = dict(zip(cached_df[cached_id_col], cached_df["Prediction"]))
        print(f"⚡ Found {len(cache)} cached predictions, skipping those tickets...")

# -----------------------------
# 3️⃣ Initialize LLM
# -----------------------------
llm = llm = OllamaLLM(model="llama2:7b-chat")


# -----------------------------
# 4️⃣ Batch process tickets
# -----------------------------
BATCH_SIZE = 10
new_predictions = []

print("Columns:", df.columns.tolist())
print(df.head())

for i in tqdm(range(0, len(df), BATCH_SIZE), desc="🤖 Processing tickets"):
    batch = df.iloc[i:i+BATCH_SIZE]
    prompt = "You are an AI Ops assistant. Analyze these Jira tickets and suggest:\n" \
             "1) Assignment group (team to handle)\n" \
             "2) Root cause guess\n" \
             "3) Suggested fix\n\n"

    has_new_ticket = False
    for _, row in batch.iterrows():
        ticket_id = str(row[ticket_id_col])
        if ticket_id in cache:
            continue
        desc = str(row["Description"])
        prompt += f"\nTicket {ticket_id}: {desc}"
        has_new_ticket = True

    if not has_new_ticket:
        continue

    prompt += "\n\nRespond in this format:\nTicket ID | Assignment Group | Root Cause | Fix Suggestion"

    try:
        response = llm.invoke(prompt)
        if not response.strip():
            continue
        for line in response.split("\n"):
            if "|" in line:
                new_predictions.append(line.strip())
    except Exception as e:
        print(f"⚠️ LLM Error: {e}")
        continue

# -----------------------------
# 5️⃣ Save results (merge cache)
# -----------------------------
for pred in new_predictions:
    try:
        tid, group, cause, fix = [x.strip() for x in pred.split("|", 3)]
        cache[tid] = pred
    except Exception as e:
        print(f"⚠️ Skipping malformed prediction: {pred} ({e})")
        continue

final_df = pd.DataFrame(list(cache.values()), columns=["Prediction"])
final_df.insert(0, "Ticket_ID", [x.split("|")[0].strip() for x in final_df["Prediction"]])
final_df.to_csv(cache_file, index=False)

print("✅ Predictions saved to", cache_file)
