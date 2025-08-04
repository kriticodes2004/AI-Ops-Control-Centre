import requests
import pandas as pd
from requests.auth import HTTPBasicAuth

# ----------------- CONFIG -----------------
EMAIL = 
API_TOKEN = 
DOMAIN = "igdtuw-team-lznfyyiz.atlassian.net"
PROJECT_KEY = "KAN"

SEARCH_URL = f"https://{DOMAIN}/rest/api/3/search"
HEADERS = {"Accept": "application/json"}

# ----------------- FUNCTION TO PARSE DESCRIPTION -----------------
def extract_description(desc_obj):
    """Extract plain text description from Atlassian Document Format"""
    if isinstance(desc_obj, dict):
        content = desc_obj.get("content", [])
        if content and "content" in content[0]:
            inner = content[0].get("content", [])
            if inner and "text" in inner[0]:
                return inner[0]["text"]
    elif isinstance(desc_obj, str):
        return desc_obj
    return ""

# ----------------- FETCH TICKETS -----------------
print("🔄 Fetching tickets from Jira...")

query = {
    'jql': f'project = {PROJECT_KEY} ORDER BY created DESC',
    'maxResults': 100
}

response = requests.get(SEARCH_URL, headers=HEADERS, params=query,
                        auth=HTTPBasicAuth(EMAIL, API_TOKEN))

if response.status_code == 200:
    data = response.json()
    issues = data.get("issues", [])
    
    rows = []
    for issue in issues:
        fields = issue.get("fields", {})
        assignee_info = fields.get("assignee")
        assignee_name = assignee_info.get("displayName") if isinstance(assignee_info, dict) else "Unassigned"

        rows.append({
            "Ticket_ID": issue.get("key", ""),
            "Summary": fields.get("summary", ""),
            "Description": extract_description(fields.get("description", "")),
            "Priority": fields.get("priority", {}).get("name", "None"),
            "Status": fields.get("status", {}).get("name", "None"),
            "Assignee": assignee_name,
            "Created": fields.get("created", "")
        })
    
    df = pd.DataFrame(rows)
    df.to_csv("jira_tickets.csv", index=False)
    print(f"✅ Successfully saved {len(df)} tickets to jira_tickets.csv")
else:
    print("❌ Error fetching tickets:", response.status_code, response.text)
