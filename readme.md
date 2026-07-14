AI Chatbot with LangGraph, Persistent Memory & Tool Calling

A production-ready AI Chatbot built with LangGraph, FastAPI, and React, featuring tool calling, persistent short-term & long-term memory, and a modern chat interface.

🚀 Features
💬 Natural conversational AI powered by Google Gemini
🧠 Short-Term Memory (Conversation History)
💾 Long-Term Persistent Memory
🗂️ Multi-thread Chat Support
🔍 Tavily Search Tool for real-time web search
🧮 Calculator Tool for mathematical calculations
⚡ LangGraph Agent Workflow
📝 Automatic Chat Title Generation
🎯 React Chat Interface
🚀 FastAPI Backend
🐘 PostgreSQL Persistence
🔄 Thread-based Conversation History
🛠️ Modular Agent Architecture

🛠 Tech Stack
Frontend
React.js
Tailwind CSS
Axios
Backend
FastAPI
LangGraph
LangChain
Google Gemini API
PostgreSQL
Pydantic
Tools
Tavily Search API
Calculator Tool


                  User
                    │
                    ▼
              React Frontend
                    │
                    ▼
                FastAPI API
                    │
                    ▼
             LangGraph Agent
        ┌───────────┼────────────┐
        │           │            │
        ▼           ▼            ▼
 Calculator     Tavily Tool   Memory
                                │
                ┌───────────────┴──────────────┐
                ▼                              ▼
      Short-Term Memory              Long-Term Memory
      (Conversation State)        (Persistent Storage)
                │                              │
                └───────────────┬──────────────┘
                                ▼
                          Google Gemini
                                │
                                ▼
                           Final Response


🧠 Memory System
1. Short-Term Memory

The chatbot maintains conversation context during an active chat session using LangGraph state.

Features:

Maintains recent messages
Preserves conversational flow
Thread-specific context
Automatically updated after every interaction
2. Long-Term Memory

Important user information is stored permanently.

Examples:

User preferences
Frequently mentioned information
Personal details (when appropriate)
Previous conversations
Custom memories

Persistent storage allows the chatbot to remember information across different sessions.

🔧 Tool Calling

The chatbot dynamically decides whether a tool is needed.

Calculator Tool

Used for:

Arithmetic
Percentages
Unit calculations
Mathematical expressions

Example:

User:
What's 15% of 850?

↓

Calculator Tool

↓

127.5
Tavily Search Tool

Used whenever the chatbot needs fresh information.

Examples:

Latest AI news
Sports
Weather
Current events
Recent technology updates

Example:

User:
Latest OpenAI news

↓

Tavily Search

↓

Summarized Response
🗂 Multi-Thread Conversations

Every chat has its own unique thread.

User
 ├── Thread 1
 │      ├── Memory
 │      └── Messages
 │
 ├── Thread 2
 │      ├── Memory
 │      └── Messages
 │
 └── Thread 3
        ├── Memory
        └── Messages

Each thread maintains an independent conversation history.

🚀 API Endpoints
Chat
POST /chat

Request

{
    "user_id":"user_1",
    "thread_id":"thread_123",
    "message":"Hello!"
}

Response

{
    "thread_id":"thread_123",
    "response":"Hello! How can I help you today?"
}
Get Threads
GET /threads/{user_id}

Returns all chat threads for a user.

Get Messages
GET /messages/{thread_id}

Returns the complete conversation history of a thread.

🔄 LangGraph Workflow
User Input
     │
     ▼
Update Memory
     │
     ▼
Reasoning
     │
     ▼
Need Tool?
 ┌────┴────┐
 │         │
Yes        No
 │         │
 ▼         ▼
Run Tool  Generate Response
 │         │
 └────┬────┘
      ▼
Store Memory
      │
      ▼
Return Response
⚙️ Environment Variables

Create a .env file inside the backend directory.

GOOGLE_API_KEY=your_google_api_key

TAVILY_API_KEY=your_tavily_api_key

DATABASE_URL=postgresql://username:password@localhost:5432/chatbot
🐘 PostgreSQL

Create a PostgreSQL database.

Example:

chatbot

Run migrations (if applicable), then start the FastAPI server.

▶️ Installation
Clone Repository
git clone https://github.com/your-username/AI-Chatbot.git

cd AI-Chatbot
Backend
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements

uvicorn main:app --reload
Frontend
cd frontend

npm install

npm run dev
💻 Screenshots

Add screenshots here.

Home Page

Chat Window

Memory Demonstration

Tool Calling

Multiple Threads
📌 Future Improvements
Voice Chat
Image Understanding
Streaming Responses
Authentication
User Profiles
Docker Deployment
Multi-Agent Workflow
MCP Integration
Additional Tools (Email, Calendar, Weather, etc.)
🤝 Contributing

Contributions are welcome!

Fork the repository
Create a new feature branch
Commit your changes
Push the branch
Open a Pull Request
📄 License                        