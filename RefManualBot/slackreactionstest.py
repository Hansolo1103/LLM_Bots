from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import os
from slack import WebClient
from slack.errors import SlackApiError
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


app = App(token=os.environ["SLACK_BOT_TOKEN"])


token = os.environ["SLACK_BOT_TOKEN"]
if not token:
    raise ValueError("Please set SLACK_API_TOKEN")

client = WebClient(token=token)


async def list_channels():
    try:
        response = await client.channels_list()
        return response['channels']
    except SlackApiError as e:
        print(f"Error listing channels: {e.response['error']}")


async def get_reactions(timestamp, channel_id):
    try:
        response = await client.reactions_get(channel=channel_id, timestamp=timestamp)
        return response['message']['reactions']
    except SlackApiError as e:
        print(f"Error getting reactions: {e.response['error']}")


async def list_users():
    try:
        response = await client.users_list()
        return response['members']
    except SlackApiError as e:
        print(f"Error listing users: {e.response['error']}")


async def get_channel(name):
    channels = await list_channels()
    for channel in channels:
        if channel['name'] == name:
            return channel


async def get_reactions_for(timestamp, channel_id):
    reactions = await get_reactions(timestamp, channel_id)
    return reactions


async def get_users_by_id():
    users = await list_users()
    users_by_id = {}
    for user in users:
        users_by_id[user['id']] = user
    return users_by_id


async def print_reactions(timestamp, channel_id):
    reactions = await get_reactions_for(timestamp, channel_id)
    users_by_id = await get_users_by_id()

    for reaction in reactions:
        print(f"{reaction['name']}:")
        for user_id in reaction['users']:
            user = users_by_id[user_id]
            print(f"  {user['profile']['email']}")
import asyncio

@app.message('.*')
async def template_query(message):
    
    print(message)
    await print_reactions(message["channel"], message['id'])
    asyncio.run(template_query(message))




if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
