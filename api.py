# /api.py

import asyncio
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import our backend logic
from agents.orchestrator import generate_debate_stances
from agents.debater import DebaterAgent
from langchain_core.messages import HumanMessage, AIMessage

# --- FastAPI App Initialization ---
app = FastAPI()

# Configure CORS to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Pydantic Model for Request Body ---
class DebateRequest(BaseModel):
    topic: str
    num_turns: int = 3

# --- Asynchronous Generator for Streaming the Debate ---
async def run_debate_stream(topic: str, num_turns: int):
    """
    This function runs the debate and yields each turn as a JSON string.
    """
    # 1. Generate stances
    yield f"data: {json.dumps({'type': 'status', 'content': 'Orchestrator is generating stances...'})}\n\n"
    try:
        stances = generate_debate_stances(topic)
        if len(stances) < 2:
            yield f"data: {json.dumps({'type': 'error', 'content': 'Failed: Orchestrator did not generate enough stances.'})}\n\n"
            return
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'content': f'Error during stance generation: {e}'})}\n\n"
        return

    # 2. Initialize Debater Agents
    agent_names = [f"Agent {chr(65+i)}" for i in range(len(stances))]
    debaters = [
        DebaterAgent(topic=topic, stance=stance, agent_name=name)
        for name, stance in zip(agent_names, stances)
    ]
    
    for agent in debaters:
        yield f"data: {json.dumps({'type': 'agent_stance', 'name': agent.name, 'stance': agent.stance})}\n\n"
    
    # 3. Run the Debate Loop
    conversation_history = [HumanMessage(content=f"The debate on '{topic}' has begun.")]
    total_exchanges = len(debaters) * num_turns

    for i in range(total_exchanges):
        current_debater = debaters[i % len(debaters)]
        
        yield f"data: {json.dumps({'type': 'status', 'content': f'{current_debater.name} is thinking...'})}\n\n"
        
        argument = current_debater.generate_argument(conversation_history)
        agent_message = AIMessage(content=argument, name=current_debater.name)
        conversation_history.append(agent_message)
        
        # Yield the argument
        yield f"data: {json.dumps({'type': 'argument', 'name': current_debater.name, 'content': argument})}\n\n"
        await asyncio.sleep(1) # Small delay for better UX

    yield f"data: {json.dumps({'type': 'status', 'content': 'Debate concluded.'})}\n\n"

# --- FastAPI Endpoint ---
@app.post("/debate")
async def debate_endpoint(request: DebateRequest):
    """
    This endpoint streams a debate on a given topic.
    """
    return StreamingResponse(
        run_debate_stream(request.topic, request.num_turns),
        media_type="text/event-stream"
    )

