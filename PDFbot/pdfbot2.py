import os, requests



from langchain.chains.question_answering import load_qa_chain

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from dotenv import load_dotenv, find_dotenv



from slack_sdk import WebClient





load_dotenv(find_dotenv())

app = App(token=os.environ["SLACK_BOT_TOKEN"])
client = WebClient(os.environ["SLACK_BOT_TOKEN"])
FIXED_API_ENDPOINT = os.environ["API_ENDPOINT"]


@app.message('.*')
def template_query(message,say):
    
    print(message)
    
    response = requests.get(FIXED_API_ENDPOINT + message["text"])
    response_text = response.json(
    )['response'] if response.status_code == 200 else f"Request failed with status code {response.status_code}"
    say(response_text)

    
    

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()