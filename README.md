# TAHO AI Chatbot Backend Setup Guide


This guide provides step-by-step instructions to set up the chatbot backend using FastAPI, PostgreSQL, and LangChain.

## 1. Create a PostgreSQL Database

Open PostgreSQL and create the database "TAHO" manually or use this command 

### `CREATE DATABASE TAHO;`

## 2. Create the chat_history table:

run this command in postgres to create the table chat_history

###  `CREATE TABLE chat_history ( id SERIAL PRIMARY KEY, user_id VARCHAR NULL, sender VARCHAR NOT NULL,message TEXT NOT NULL,timestamp TIMESTAMP DEFAULT URRENT_TIMESTAMP);`

## 3. Clone the repository 

## 4. Set Up the Project 

### Create and activate a virtual environment (for Linux user : ubuntu)

python -m venv venv
source venv/bin/activate  

### Create and activate a virtual environment (for Windows)

python -m venv venv
venv\Scripts\activate 

###  Install dependencies

pip install fastapi[all] uvicorn sqlalchemy psycopg2-binary python-dotenv langchain langchain-groq

###  Configure Environment Variables

Create a .env file in the project root and add the following and replace your_password and your_groq_api_key with actual values:

DATABASE_URL=postgresql://postgres:your_password@localhost:5432/TAHO
GROQ_API_KEY=your_groq_api_key

### Start the FastAPI server 

run  `uvicorn main:app --reload`



 


# taho-chatbot-backend
