import pandas as pd
import streamlit as st
from azure.identity import DefaultAzureCredential
import requests
from datetime import datetime
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes
from flask import Flask, request
import asyncio

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

# Chatbot conversation
user_input = st.text_input("Ask me about Azure costs:")

if user_input:
    # Extract dates from user input (assuming a specific format for simplicity)
    try:
        start_date_str, end_date_str = user_input.split(" to ")
        start_date = datetime.strptime(start_date_str.strip(), '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str.strip(), '%Y-%m-%d')

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
    except ValueError:
        st.write("Please enter dates in the format 'YYYY-MM-DD to YYYY-MM-DD'.")

# Bot Framework integration
class CostBot:
    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == ActivityTypes.message:
            user_input = turn_context.activity.text
            try:
                start_date_str, end_date_str = user_input.split(" to ")
                start_date = datetime.strptime(start_date_str.strip(), '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str.strip(), '%Y-%m-%d')

                cost_data = get_cost_data(start_date, end_date)

                # Extract relevant data and create a response message
                data = []
                for item in cost_data['properties']['rows']:
                    data.append(f"Resource Group: {item[2]}, Date: {item[1]}, Cost: {item[0]}")

                response_message = "\n".join(data)
                await turn_context.send_activity(response_message)
            except ValueError:
                await turn_context.send_activity("Please enter dates in the format 'YYYY-MM-DD to YYYY-MM-DD'.")

# Create the bot instance
bot = CostBot()

# Adapter settings
settings = BotFrameworkAdapterSettings("", "")
adapter = BotFrameworkAdapter(settings)

# Flask app to handle incoming requests
app = Flask(__name__)

@app.route('/api/messages', methods=['POST'])
async def messages():
    body = await request.json
    activity = Activity().deserialize(body)
    auth_header = request.headers['Authorization'] if 'Authorization' in request.headers else ''
    response = await adapter.process_activity(activity, auth_header, bot.on_turn)
    if response:
        return response.body
    return 'OK'

if __name__ == '__main__':
    if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
