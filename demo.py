import pandas as pd
import streamlit as st
from azure.identity import DefaultAzureCredential
import requests
from datetime import datetime


# Function to fetch cost data
def get_cost_data(start_date, end_date):
    credential = DefaultAzureCredential()
    subscription_id = '7b9338d2-e8dc-405b-91d7-ef8fe30b97b6'
    cost_management_url = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.CostManagement/query?api-version=2021-10-01"

    headers = {
        'Authorization': f'Bearer {credential.get_token("https://management.azure.com/.default").token}',
        'Content-Type': 'application/json'
    }

    # Convert date objects to strings
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    query = {
        "type": "Usage",
        "timeframe": "Custom",
        "timePeriod": {
            "from": start_date_str,
            "to": end_date_str
        },
        "dataset": {
            "granularity": "Daily",
            "aggregation": {
                "totalCost": {
                    "name": "Cost",
                    "function": "Sum"
                }
            },
            "grouping": [
                {
                    "type": "Dimension",
                    "name": "ResourceGroupName"
                }
            ]
        }
    }

    response = requests.post(cost_management_url, headers=headers, json=query)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()


# Streamlit UI
st.title("Azure Subscription Cost Chatbot")

start_date = st.date_input("Start Date", datetime(2023, 1, 1))
end_date = st.date_input("End Date", datetime(2023, 1, 31))

if st.button("Get Cost Data"):
    cost_data = get_cost_data(start_date, end_date)

    # Extract relevant data and create a DataFrame
    data = []
    for item in cost_data['properties']['rows']:
        data.append({
            'Resource Group': item[2],
            'Date': item[1],
            'Cost': item[0]
        })

    df = pd.DataFrame(data)

    # Display the DataFrame in tabular format using Streamlit
    st.write(df)