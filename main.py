import asyncio
from agents.orchestrator import generate_debate_stances
from agents.debater import DebaterAgent

debate_topic="impact of social media on mental health"
num_turns=4

def format_history(history:list[str]) -> str:
    """Formats the conversation history from the agent's scratchpad."""
    if not history:
        return "No conversation history yet."
    return "\n".join(history)
async def main():
    print("starting debate on : ",debate_topic)
    try:
        stances=generate_debate_stances(debate_topic)
        if not stances:
            print("No stances generated. Exiting debate.")
            return
    except Exception as e:
        print(f"Error generating stances: {e}")
        return
    
    agent_names=[f"Agent {chr(65+i)}" for i in range(len(stances))]
    debaters=[
        DebaterAgent(topic=debate_topic, stance=stance, agent_name=name)
        for stance, name in zip(stances, agent_names)
    ]
    print("Debaters initialized:")
    for debater in debaters:
        print(f"{debater.agent_name} - Stance: {debater.stance}")
    
    conversation_history = [f"Moderator: The debate on '{debate_topic}' will now begin. We have {len(debaters)} participants. Let's hear the opening statements."]
    
    total_exchanges = len(debaters) * num_turns
    
    for i in range(total_exchanges):
        current_debater = debaters[i % len(debaters)]
        
        history_str=format_history(conversation_history)
        
        argument = current_debater.generate_arguments(history_str)
        
        turn_text=f"**{current_debater.agent_name}**: {argument}"
        print(turn_text)
        conversation_history.append(turn_text)
if __name__ == "__main__":
    print("Starting debate simulation...")
    asyncio.run(main())
    print("Debate simulation completed.")