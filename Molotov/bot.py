import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain import (
    OpenAI,
    ConversationChain,
    LLMChain,
    PromptTemplate,
)
from langchain.memory import ConversationBufferWindowMemory
from dotenv import load_dotenv, find_dotenv
import openai


from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv(find_dotenv())


from collections import deque

# Initialize a deque to store the conversation history
conversation_history = deque(maxlen=30)


app = App(token=os.environ["SLACK_BOT_TOKEN"])
client = WebClient(os.environ["SLACK_BOT_TOKEN"])

# Langchain implementation
template = """Assistant is a large language model trained by OpenAI.

    Assistant is designed to provide long code solutions to the user.

    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

    Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.

    {history}
    Human: {human_input}
    Assistant:"""

prompt = PromptTemplate(input_variables=["history", "human_input"], template=template)


chatgpt_chain = LLMChain(
    llm=OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0),
    prompt=prompt,
    verbose=True,
    memory=ConversationBufferWindowMemory(k=30),
)


def get_bot_user_id():
    """
    Get the bot user ID using the Slack API.
    Returns:
        str: The bot user ID.
    """
    try:
        # Initialize the Slack client with your bot token
        slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        response = slack_client.auth_test()
        return response["user_id"]
    except SlackApiError as e:
        print(f"Error: {e}")


SLACK_BOT_USER_ID = get_bot_user_id()


# Message handler for Slack
@app.message(".*")
def message_handler(message, say, logger):
    # message = request.form.get("message")
    print(message)
    conversation_history.append(message["text"])

    # Construct the input dictionary with the conversation history and the user's message
    input_dict = {
        "history": "\n".join(conversation_history),
        "human_input": message["text"],
    }

    response = chatgpt_chain.predict(**input_dict)

    say(response)


@app.event("app_mention")
def handle_message_events(body, logger):
    # Log message
    print(str(body["event"]["text"]).split(">")[1])

    # Create prompt for ChatGPT
    prompt = str(body["event"]["text"]).split(">")[1]

    conversation_history.append(prompt)

    # Construct the input dictionary with the conversation history and the user's message
    input_dict = {
        "history": "\n".join(conversation_history),
        "human_input": prompt,
    }

    # Let thre user know that we are busy with the request
    # response = client.chat_postMessage(channel=body["event"]["channel"],
    #                                    thread_ts=body["event"]["event_ts"],
    #                                    text=f"Hello from your bot! :robot_face: \nThanks for your request, I'm on it!")

    # Check ChatGPT

    response = chatgpt_chain.predict(**input_dict)

    # Reply to thread
    response = client.chat_postMessage(
        channel=body["event"]["channel"],
        thread_ts=body["event"]["event_ts"],
        text=f"{response}",
    )


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
