import openai
import requests
from flask import Flask, request
from azure.identity import DefaultAzureCredential
from azure.mgmt.costmanagement import CostManagementClient
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
import asyncio
import os

app = Flask(__name__)

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv('your_openai_api_key')

# Set your Azure subscription ID from environment variable
subscription_id = os.getenv('your_subscription')

# Authenticate using DefaultAzureCredential
credential = DefaultAzureCredential()
cost_client = CostManagementClient(credential)

# Create Bot Framework Adapter with settings
settings = BotFrameworkAdapterSettings(
    app_id=os.getenv('your_appid'),
    app_password=os.getenv('your_app_password')
)
adapter = BotFrameworkAdapter(settings)

@app.route('/', methods=['GET'])
def home():
    return 'Welcome to the Bot Service!'

@app.route('/api/messages', methods=['POST'])
def messages():
    body = request.json
    activity = Activity().deserialize(body)
    auth_header = request.headers.get('Authorization', '')
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
    try:
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
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def chat_with_openai(user_input):
    try:
        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=user_input,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
