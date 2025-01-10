from flask import Flask, request
from botbuilder.schema import Activity
from bot import bot, adapter

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
    app.run(host='0.0.0.0', port=80)