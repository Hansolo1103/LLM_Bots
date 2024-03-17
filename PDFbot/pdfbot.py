import os


from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain import (
    OpenAI,
    PromptTemplate
)
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv, find_dotenv



from slack_sdk import WebClient





load_dotenv(find_dotenv())

app = App(token=os.environ["SLACK_BOT_TOKEN"])
client = WebClient(os.environ["SLACK_BOT_TOKEN"])



reader = PdfReader('stm32f446ve.pdf')


raw_text = ''
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    if text:
        raw_text += text


text_splitter = CharacterTextSplitter(        
    separator = "\n",
    chunk_size = 1000,
    chunk_overlap  = 200,
    length_function = len,
)


texts = text_splitter.split_text(raw_text)

embeddings = OpenAIEmbeddings()
# docsearch = FAISS.from_texts(texts, embeddings)

docsearch = FAISS.from_texts(texts, embeddings, metadatas=[{"source": i} for i in range(len(texts))])

@app.message('.*')
def template_query(message,say):
    
    print(message)
    
    template = """You are an extremely intelligent
    
    AI assistant. Answer questions respectfully by extracting meaningful
    
    information only from the document.
    
    Answer in detail with examples.
    
    {context}
    
    {chat_history}
    
    Human: {human_input}
    
    assistant:
    
    """
    prompt = PromptTemplate(
    input_variables=["chat_history", "human_input", "context"], 
    template=template
    )
    
    memory = ConversationBufferMemory(memory_key="chat_history", input_key="human_input")
    
    chatgpt_chain = load_qa_chain(OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0),
    chain_type="stuff", memory=memory, prompt=prompt)
    
    
    docs = docsearch.similarity_search(message["text"])
    chatgpt_chain({"input_documents": docs, "human_input": message["text"]}, return_only_outputs=True)
    response = chatgpt_chain.memory.buffer
    say(response.split("AI:",1)[1])


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()