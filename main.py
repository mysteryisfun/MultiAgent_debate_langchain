# /main.py

import asyncio
from agents.orchestrator import generate_debate_stances
from agents.debater import DebaterAgent
from langchain_core.messages import HumanMessage, AIMessage

# --- Configuration ---
DEBATE_TOPIC = "The feasibility and ethics of widespread drone delivery in urban areas."
NUM_TURNS = 3 # Each agent speaks this many times.

async def main():
    """
    Main function to run the multi-agent debate with tool-using agents.
    """
    print(f"--- Starting Debate on: {DEBATE_TOPIC} ---")

    # 1. Generate stances
    try:
        stances = generate_debate_stances(DEBATE_TOPIC)
        if len(stances) < 2:
            print("\n❌ --- Debate Failed: Orchestrator needs at least 2 stances. --- ❌")
            return
    except Exception as e:
        print(f"\n❌ --- Debate Failed during stance generation: {e} --- ❌")
        return

    # 2. Initialize Debater Agents
    agent_names = [f"Agent {chr(65+i)}" for i in range(len(stances))] # Agent A, B, etc.
    debaters = [
        DebaterAgent(topic=DEBATE_TOPIC, stance=stance, agent_name=name)
        for name, stance in zip(agent_names, stances)
    ]

    print("\n--- The Debaters Have Assembled ---")
    for agent in debaters:
        print(f"- {agent.name}: {agent.stance}")
    print("----------------------------------\n")

    # 3. Run the Debate Loop
    # The history now uses LangChain message objects, which is required by the agent executor.
    conversation_history = [
        HumanMessage(content=f"The debate on '{DEBATE_TOPIC}' will now begin. We have {len(debaters)} participants. Let's hear the opening statements.")
    ]
    
    total_exchanges = len(debaters) * NUM_TURNS

    for i in range(total_exchanges):
        current_debater = debaters[i % len(debaters)]
        
        # The agent's generate_argument method now takes the list of messages directly.
        argument = current_debater.generate_argument(conversation_history)
        
        # The agent's response is now an AIMessage.
        # We assign the agent's name to the message for clarity in the transcript.
        agent_message = AIMessage(content=argument, name=current_debater.name)
        
        # Add the agent's response to the history
        conversation_history.append(agent_message)
        
        # Print the turn to the console
        print(f"\n**{current_debater.name}:** {argument}")

    # 4. Print the final transcript
    print("\n\n--- ✅ Debate Concluded ---")
    print("--- Final Transcript ---")
    for message in conversation_history:
        if isinstance(message, HumanMessage):
            # The initial moderator message
            print(f"Moderator: {message.content}")
        elif isinstance(message, AIMessage):
            # Agent messages, using the name we assigned
            print(f"**{message.name}:** {message.content}")
    print("--------------------------")


# --- Run the application ---
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ --- A critical error occurred in the main loop: {e} --- ❌")
        import traceback
        traceback.print_exc()
