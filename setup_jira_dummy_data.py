import requests
import pandas as pd
import random
import time
from requests.auth import HTTPBasicAuth

# config
EMAIL = "*****"        
API_TOKEN = "ATATT3xFfGF0FdsECzdrFfykpKxZ2hjpp2pP6E7bhznYD7FB7udxgEh_hhI8OnFYZYGHyiAgWh08nIlnzIg52ZSehYYDTfWKM215109I0BJcWBUhNSk3JdkjnZrV2hr_s9pzVWsTHVjAuNyjRg1EkRqhLGUjYWU9INcw_H0Jw-WdsNjxAlX_Vrk=A8568A23"
DOMAIN = "igdtuw-team-lznfyyiz.atlassian.net"
PROJECT_KEY = "KAN"
TOTAL_TICKETS = 50

CREATE_URL = f"https://{DOMAIN}/rest/api/3/issue"
SEARCH_URL = f"https://{DOMAIN}/rest/api/3/search"
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

summaries = [
    "Database connection failure in server cluster",
    "High memory usage alert in microservice A",
    "Login API returns 500 error on customer login",
    "Payment gateway timeout for user transactions",
    "Disk space running low on production server",
    "Email notifications not sent to customers",
    "Service latency increased beyond SLA threshold",
    "Load balancer health check failed for instance B",
    "Unauthorized access attempt detected from IP range",
    "Application crashes during high traffic hours",
    "Configuration mismatch between staging and prod",
    "Network packet loss detected in region EU-West",
    "SSL certificate expired for service endpoint",
    "Data sync failed between microservices A and B",
    "Service deployment rollback due to errors"
]

priorities = ["Highest", "High", "Medium", "Low"]
descriptions = [
    "Auto-generated ticket for AI-Ops project testing.",
    "This ticket is created for simulating incident triage.",
    "Dummy incident to test priority classification.",
    "Generated for machine learning model training dataset."
]
#test connection
print("🔄 Testing Jira API connection...")
test_url = f"https://{DOMAIN}/rest/api/3/myself"
test_response = requests.get(test_url, auth=HTTPBasicAuth(EMAIL, API_TOKEN))
if test_response.status_code != 200:
    print(" Jira connection failed. Check your EMAIL, API_TOKEN, or DOMAIN.")
    print(test_response.status_code, test_response.text)
    exit()
print("Jira connection successful.\n")

# ticket creation

print(f"Creating {TOTAL_TICKETS} dummy tickets in Jira project {PROJECT_KEY}...")
for i in range(TOTAL_TICKETS):
    issue_data = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": random.choice(summaries),
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "text": random.choice(descriptions),
                                "type": "text"
                            }
                        ]
                    }
                ]
            },
            "issuetype": {"name": "Task"},
            "priority": {"name": random.choice(priorities)}
        }
    }
    response = requests.post(CREATE_URL, headers=HEADERS,
                             auth=HTTPBasicAuth(EMAIL, API_TOKEN),
                             json=issue_data)
    if response.status_code == 201:
        print(f"✅ Created ticket {i+1}")
    else:
        print(f"❌ Failed to create ticket {i+1}: {response.text}")
    time.sleep(0.2)  # delay to avoid rate limit

print("\n✅ Ticket creation complete.\n")

