import streamlit as st
import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.costmanagement import CostManagementClient

st.title("Azure Subscription Cost Chatbot")

if st.button("Get Cost Details"):
    credential = DefaultAzureCredential()
    subscription_id = os.environ["8830f69d-e241-40f9-83fc-5a79c12adcac"]
    cost_management_url = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.CostManagement/query?api-version=2021-10-01"

    headers = {
        'Authorization': f'Bearer {credential.get_token("https://management.azure.com/.default").token}',
        'Content-Type': 'application/json'
    }
    time_period = {"timeframe": "MonthToDate"}
    cost_details = requests.post(cost_management_url, headers=headers, json=time_period)
    st.write(cost_details.as_dict())