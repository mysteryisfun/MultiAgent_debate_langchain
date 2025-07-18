# Live AI Debate Stage: A Multi-Agent System with LangChain

This project showcases a sophisticated multi-agent system built with Python and LangChain that simulates a live debate between AI agents on any given topic. The agents are equipped with tools for web search and knowledge base retrieval, allowing them to formulate dynamic, fact-based arguments. The entire debate is streamed in real-time to a modern, responsive web interface.

![Live Debate Screenshot](https://user-images.githubusercontent.com/16162937/226891931-372b2268-5223-4457-b8a1-88c24845f733.png)
*(Note: This is a representative image. Your UI will look like the one we styled.)*

---

## ✨ Features

- **Dynamic Stance Generation**: An "Orchestrator" agent analyzes the debate topic and generates distinct, polarizing stances for the debaters.
- **Tool-Augmented Agents**: Debater agents can autonomously use tools to:
    - **`web_search`**: Access real-time information from the internet.
    - **`knowledge_base_search`**: Retrieve specific information from a local PDF document using a vector database (ChromaDB).
- **Sequential Debate Loop**: Agents take turns to present their arguments, building upon the conversation history.
- **Real-time Web Interface**: A sleek frontend built with HTML, CSS, and JavaScript that streams the debate live.
    - Displays agent profiles, their assigned stances, and their "thinking" status.
    - Renders the conversation transcript as it happens.
- **Asynchronous Backend**: Built with FastAPI to handle concurrent requests and stream updates efficiently using Server-Sent Events (SSE).
- **Modular Architecture**: The code is organized into distinct modules for agents, tools, prompts, and the web server, making it easy to extend.

---

## 🛠️ Tech Stack

- **Backend**: Python, LangChain, FastAPI, Uvicorn
- **LLM**: Google Gemini
- **Vector Database**: ChromaDB
- **Frontend**: HTML, CSS, JavaScript
- **Core Libraries**: `langchain`, `langchain-google-genai`, `fastapi`, `uvicorn`, `pypdf`, `chromadb`, `beautifulsoup4`, `python-dotenv`

---

## 📂 Project Structure

```
MultiAgent_debate_langchain/
│
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py   # Generates debate stances
│   └── debater.py        # Defines the debater agent logic
│
├── docs/
│   └── ai_military.pdf   # Example PDF for the knowledge base
│
├── frontend/
│   ├── index.html        # Main HTML file
│   ├── script.js         # Frontend logic for SSE and UI updates
│   └── styles.css        # Styling for the web interface
│
├── tools/
│   ├── __init__.py
│   ├── knowledge_base.py # Tool for searching the local PDF
│   └── search.py         # Tool for web search
│
├── utils/
│   ├── __init__.py
│   └── prompts.py        # Contains all LangChain prompt templates
│
├── .env                  # Environment variables (API keys)
├── .gitignore            # Git ignore file
├── main.py               # FastAPI server and main debate logic
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.9+
- A Google API Key with the Gemini API enabled.

### 2. Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/MultiAgent_debate_langchain.git
    cd MultiAgent_debate_langchain
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuration

1.  **Create a `.env` file** in the root directory by copying the example:
    ```bash
    # For Windows
    copy .env.example .env

    # For macOS/Linux
    cp .env.example .env
    ```

2.  **Add your Google API Key** to the `.env` file:
    ```env
    # .env
    google_api_key="YOUR_GOOGLE_API_KEY"
    TAVILY_API_KEY="tavily_api_key"
    ```

3.  **Add a Knowledge Base Document:**
    Place a PDF file you want the agents to be able to reference into the `docs/` directory. The default is `ai_military.pdf`, but you can change the filename in `tools/knowledge_base.py`.

---

## ▶️ How to Run

1.  **Start the backend server:**
    Run the `main.py` file using Uvicorn from the root directory.
    ```bash
    uvicorn main:app --reload
    ```
    The server will start, typically on `http://127.0.0.1:8000`.

2.  **Launch the frontend:**
    Open the `frontend/index.html` file directly in your web browser.

3.  **Start a Debate:**
    In the web interface, type a topic into the input box and click the "Start" button. Watch the debate unfold in real time!

---

## ⚙️ How It Works

1.  **Initiation**: The user provides a topic via the frontend. This hits the `/start-debate` endpoint on the FastAPI server.
2.  **Stance Generation**: The `Orchestrator` agent receives the topic and generates 2-3 distinct stances.
3.  **Agent Initialization**: A `DebaterAgent` instance is created for each stance. Each agent is equipped with the `web_search` and `knowledge_base_search` tools.
4.  **Debate Loop**: The server iterates through a set number of turns. In each turn:
    - The current agent receives the full conversation history.
    - The agent's `AgentExecutor` decides whether to respond directly or use a tool based on the prompt and history.
    - If a tool is used, its output is fed back into the agent's context.
    - The agent generates its final argument.
5.  **Real-time Streaming**: The server uses **Server-Sent Events (SSE)** to push updates to the frontend. It sends messages for:
    - The generated stances and agent profiles.
    - The "thinking" status of the current agent.
    - The final argument from the agent.
    - Any errors that occur.
6.  **UI Updates**: The frontend JavaScript listens for these events and dynamically updates the HTML to display the agent profiles and the debate transcript.

---

## 💡 Future Improvements

- **Moderator Agent**: Introduce a third agent role to guide the conversation, ask follow-up questions, and enforce rules.
- **Fact-Checking**: Add a dedicated fact-checking step or agent to verify claims made during the debate.
- **User Interaction**: Allow the user to vote for a winner or inject questions into the debate.
- **Advanced Memory**: Implement a more sophisticated memory system (e.g., `ConversationSummaryBufferMemory`) to handle very long conversations.
- **More Tools**: Add more tools, such as a calculator or a code