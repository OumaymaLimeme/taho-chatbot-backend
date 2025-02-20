import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from langchain.chains import LLMChain   # LangChain processing chain
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory  # Conversation memory management : to conserve the previous chat  and see them 
from langchain_groq import ChatGroq  # Import Groq chat model
from dotenv import load_dotenv

from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Get Groq API Key from .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY. Check your .env file")

# Get the database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Missing DATABASE_URL. Check your .env file")    

# Initialize FastAPI application
app = FastAPI()

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Table model for chat history
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True) # Primary key
    user_id = Column(String, nullable=True)  # Optional: Track different users
    sender = Column(String, nullable=False)  # Indicates sender (user or TAHO bot)
    message = Column(Text, nullable=False)   # Stored message
    timestamp = Column(TIMESTAMP, server_default=func.now())

# Create the table in the database
Base.metadata.create_all(bind=engine)


# Initialize Groq chat model with LangChain  LLMChain
model_name = "llama3-8b-8192"
groq_chat = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=model_name)

# Conversation memory (remembers last 5 messages)
memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", return_messages=True)

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket for real-time chat communication with the chatbot.
    """
    await websocket.accept()
    print("TAHO AI Chatbot is connected")
    session = SessionLocal()  # Create a new DB session

    try:
        while True:
            # Wait for the user message
            user_question = await websocket.receive_text()
            print(f"User: {user_question}")
            
            # Ignore empty messages
            if not user_question.strip():
                continue  

            # Store user message in the database
            user_message = ChatHistory(sender="user", message=user_question)
            session.add(user_message)
            session.commit()    

            # Build the chatbot prompt
            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(content="You are a friendly chatbot."),
                    MessagesPlaceholder(variable_name="chat_history"),
                    HumanMessagePromptTemplate.from_template("{human_input}"),
                ]
            )

            # Initialize LangChain with the Groq model
            conversation = LLMChain(
                llm=groq_chat,
                prompt=prompt,
                verbose=False,
                memory=memory,
            )

            # Get chatbot response
            response = conversation.predict(human_input=user_question)

            # Store chatbot response in the database
            bot_message = ChatHistory(sender="TAHO bot", message=response)
            session.add(bot_message)
            session.commit()

            # Stream response word by word
            for word in response.split():
                await websocket.send_text(word + " ")
                await asyncio.sleep(0.05)  # Simulate streaming effect

    except WebSocketDisconnect:
        print("TAHO AI Chatbot is disconnected")
    finally:
        session.close()  # Close the DB session    
