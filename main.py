from typing import List
from langchain_core.output_parsers import StrOutputParser

from config import llm, orchestrator_chain, debater_prompt_template, Stance, DebateSetup

def format_history(conversation_history: List[str]) -> str:
    """helper function to format the conversation into string for LLM"""
    if not conversation_history:
        return "No conversation history yet, you the first to speak."
    history_str=""
    for entry in conversation_history:
        history_str += f"{entry['agent_name']}:{entry['message']}\n"
        
    return history_str

def run_debate(debate_details:DebateSetup, max_turns=10):
    """runs main debate loop"""
    conversation_history = []
    debater_chains = [] #store debator chains from each agent
    
    for stance in debate_details.stances:
        bound_promt= debater_prompt_template.partial(
            agent_name=stance.agent_name,
            stance_brief=stance.stance_brief,
        )
        chain=bound_promt | llm | StrOutputParser()
        debater_chains.append({"name": stance.agent_name, "chain": chain})
    print("Debater agents created")
    print("Starting debate...")
    
    for turn in range(max_turns):
        agent_index = turn % len(debater_chains)  # Cycle through agents
        current_agent = debater_chains[agent_index]
        print(f"\nTurn {turn + 1}: {current_agent['name']}'s turn")
        
        formatted_history = format_history(conversation_history)
        response = current_agent['chain'].invoke({
            "agent_scarchpad": [],  # Empty list for scratchpad
            "conversation_history": formatted_history#becoz the agent name and stance have been passed with partial while chain creation
        })
        if response.strip().upper() == "PASS":
            print(f"{current_agent['name']}has nothing to add this turn.")
            continue
        print(f"{current_agent['name']}: {response}")
        conversation_history.append({
            "agent_name": current_agent['name'],
            "message": response
        })
    print("\nDebate ended.")
    return conversation_history
if __name__ == "__main__":
    user_topic = "Should AI be used in the military?"
    debate_setup = orchestrator_chain.invoke({"topic": user_topic}) #return the stances list
    
    for i, stance in enumerate(debate_setup.stances):
        print(f"Agent {i+1} Name: {stance.agent_name}")
        print(f"Stance Brief: {stance.stance_brief}\n")
    
    # Run the debate
    conversation_history = run_debate(debate_setup)
    
    print("\nFinal Conversation History:")
    for entry in conversation_history:
        print(f"{entry['agent_name']}: {entry['message']}")