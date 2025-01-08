import streamlit as st
import requests
from azure.identity import DefaultAzureCredential

def get_azure_costs():
    credential = DefaultAzureCredential()
    subscription_id = '8830f69d-e241-40f9-83fc-5a79c12adcac'
    cost_management_url = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.CostManagement/query?api-version=2021-10-01"

    headers = {
        'Authorization': f'Bearer {credential.get_token("https://management.azure.com/.default").token}',
        'Content-Type': 'application/json'
    }

    # Define the query parameters (adjust as needed)
    query = {
        "type": "ActualCost",
        "timeframe": "MonthToDate",
        "dataset": {
            "granularity": "Daily",
            "aggregation": {
                "totalCost": {
                    "name": "Cost",
                    "function": "Sum"
                }
            }
        }
    }

    response = requests.post(cost_management_url, headers=headers, json=query)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()

# Streamlit UI
st.title("Azure Subscription Cost Chatbot")

if st.button("Get Cost Data"):
    cost_data = get_azure_costs()
    for item in cost_data:
        st.write(f"Cost: {item['totalCost']}")


