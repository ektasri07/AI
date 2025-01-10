import openai
import requests
from flask import Flask, request
from azure.identity import DefaultAzureCredential
from azure.mgmt.costmanagement import CostManagementClient
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
import asyncio

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = 'your_openai_api_key'

# Set your Azure subscription ID
subscription_id = '7b9338d2-e8dc-405b-91d7-ef8fe30b97b6'

# Authenticate using DefaultAzureCredential
credential = DefaultAzureCredential()
cost_client = CostManagementClient(credential)

# Create Bot Framework Adapter with settings
settings = BotFrameworkAdapterSettings(app_id='ee2d8235-77e7-4e46-84dd-7fbf44ffe95f', app_password='your_app_password')
adapter = BotFrameworkAdapter(settings)

@app.route('/api/messages', methods=['POST'])
def messages():
    body = request.json
    activity = Activity().deserialize(body)
    auth_header = request.headers['Authorization'] if 'Authorization' in request.headers else ''
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(adapter.process_activity(activity, auth_header, bot_logic))
    return 'OK'

async def bot_logic(turn_context: TurnContext):
    user_input = turn_context.activity.text
    if 'cost' in user_input.lower():
        cost_data = get_cost()
        await turn_context.send_activity(f"Azure subscription cost data: {cost_data}")
    else:
        response = chat_with_openai(user_input)
        await turn_context.send_activity(response)

def get_cost():
    headers = {
        'Authorization': f'Bearer {credential.get_token("https://management.azure.com/.default").token}',
        'Content-Type': 'application/json'
    }
    url = f'https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.CostManagement/query?api-version=2024-08-01'
    body = {
        "type": "Usage",
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
    response = requests.post(url, headers=headers, json=body)
    return response.json()

def chat_with_openai(user_input):
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=user_input,
        max_tokens=150
    )
    return response.choices[0].text.strip()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
