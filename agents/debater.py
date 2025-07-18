# /agents/debater.py

import os
from dotenv import load_dotenv

# Core LangChain agent components
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage

# Our tools and new agent prompt
from utils.prompts import debator_agent_with_tools_template
from tools.search import web_search
from tools.knowledge_base import knowledge_base_search  # Import the new tool

load_dotenv()

class DebaterAgent:
    """
    Represents a tool-using debater agent. It can reason, use tools like
    web search and knowledge base search, and then formulate an argument.
    """
    def __init__(self, topic: str, stance: str, agent_name: str):
        self.topic = topic
        self.stance = stance
        self.name = agent_name
        
        # Initialize the LLM
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
        
        # Define ALL the tools the agent has access to
        tools = [web_search, knowledge_base_search]  # Add knowledge_base_search

        # Partially format the prompt with the agent's specific persona.
        # This is an advanced technique for creating specialized agents from a common template.
        prompt = debator_agent_with_tools_template.partial(
            stance=self.stance,
            topic=self.topic
        )

        # Create the agent by bundling the LLM, tools, and prompt.
        agent = create_tool_calling_agent(llm, tools, prompt)

        # The AgentExecutor is the runtime that powers the agent.
        self.executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,  # Set to True to see the agent's thought process
            handle_parsing_errors=True # Gracefully handles LLM output errors
        )
        print(f"--- Multi-Tool Debater Agent '{self.name}' Initialized ---")

    def generate_argument(self, conversation_history: list) -> str:
        """
        Generates the next argument by invoking the agent executor.
        The agent can decide to use tools or respond directly.

        Args:
            conversation_history: A list of message objects (HumanMessage, AIMessage).

        Returns:
            A string containing the agent's final argument.
        """
        print(f"\n--- {self.name}'s Turn (Stance: {self.stance[:60]}...) ---")
        
        input_prompt = (
            "Based on the conversation so far and your stance, what is your next argument? "
            "Use your tools if you need to find new information or specific details from the knowledge base."
        )

        response = self.executor.invoke({
            "input": input_prompt,
            "chat_history": conversation_history
        })
        
        return response['output']

# --- Test Block ---
if __name__ == '__main__':
    print("--- Running Multi-Tool Debater Agent Test ---")
    
    test_topic = "The ethics of AI in military, particularly regarding algorithmic bias and data privacy."
    test_stance = "AI is essential for modern military, offering unparalleled efficiency, but strict ethical frameworks must be in place to prevent bias."
    
    # Mock history for a scenario where the agent might use the knowledge base
    mock_history = [
        HumanMessage(content="Moderator: Let's discuss AI in urban planning."),
        AIMessage(content="Agent Beta (Opponent): AI in urban planning is inherently biased and dangerous. Algorithms simply amplify existing societal inequalities."),
        HumanMessage(content="Moderator: Can you cite any specific ethical concerns from the provided report on AI ethics in urban planning?")
    ]
    
    try:
        agent_alpha = DebaterAgent(
            topic=test_topic, 
            stance=test_stance, 
            agent_name="Agent Alpha"
        )
        
        # This interaction is designed to encourage the agent to use the knowledge_base_search tool.
        new_argument = agent_alpha.generate_argument(mock_history)
        
        print("\n\n✅ --- Test Successful --- ✅")
        print(f"Agent Name: {agent_alpha.name}")
        print("\n--- Agent's Final Generated Argument ---")
        print(new_argument)
        print("-----------------------------------")
        print("\nReview the verbose output above to see if the 'web_search' or 'knowledge_base_search' tool was called.")
        
    except Exception as e:
        print(f"\n❌ --- An error occurred during testing: {e} --- ❌")
        import traceback
        traceback.print_exc()

