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

load_dotenv()

class DebaterAgent:
    """
    Represents a tool-using debater agent. It can reason, use tools like
    web search, and then formulate an argument.
    """
    def __init__(self, topic: str, stance: str, agent_name: str):
        self.topic = topic
        self.stance = stance
        self.name = agent_name
        
        # Initialize the LLM
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.7)
        
        # Define the tools the agent has access to
        tools = [web_search]

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
        print(f"--- Tool-Using Debater Agent '{self.name}' Initialized ---")

    def generate_argument(self, conversation_history: list) -> str:
        """
        Generates the next argument by streaming the agent executor response.
        Shows real-time tool usage and thinking process.

        Args:
            conversation_history: A list of message objects (HumanMessage, AIMessage).

        Returns:
            A string containing the agent's final argument.
        """
        print(f"\n--- {self.name}'s Turn (Stance: {self.stance[:60]}...) ---")

        input_prompt = "Based on the conversation so far and your stance, what is your next argument? Use your tools if you need to find new information."

        response_chunks = []
        final_output = ""

        print(f"\n💭 {self.name} is analyzing the situation...\n")

        try:
            for chunk in self.executor.stream({
                "input": input_prompt,
                "chat_history": conversation_history
            }):
                # Handle different types of chunks
                if 'agent' in chunk:
                    # Agent's reasoning
                    agent_output = chunk['agent']['messages'][0].content
                    print(f"🧠 Thinking: {agent_output}")

                elif 'actions' in chunk:
                    # Tool calls
                    actions = chunk['actions']
                    for action in actions:
                        print(f"\n🔍 Using {action.tool}: {action.tool_input}")

                elif 'steps' in chunk:
                    # Tool results
                    steps = chunk['steps']
                    for step in steps:
                        print(f"📊 Found: {step.observation[:150]}...")

                elif 'output' in chunk:
                    # Final output
                    content = chunk['output']
                    response_chunks.append(content)
                    final_output = content
                    print(f"\n💬 {self.name}: {content}")

            print(f"\n--- {self.name} finished responding ---")
            return final_output if final_output else "".join(response_chunks)

        except Exception as e:
            print(f"\n❌ Streaming error: {e}")
            # Fallback to regular invoke
            response = self.executor.invoke({
                "input": input_prompt,
                "chat_history": conversation_history
            })
            return response['output']

# --- Test Block ---
if __name__ == '__main__':
    print("--- Running Tool-Using Debater Agent Test ---")
    
    test_topic = "The viability of colonizing Mars."
    test_stance = "Colonizing Mars is a critical next step for humanity, ensuring the long-term survival of our species and driving technological innovation."
    
    # Mock history must be a list of HumanMessage/AIMessage objects
    mock_history = [
        HumanMessage(content="Moderator: Let's begin the debate on Mars colonization."),
        AIMessage(content="Agent Beta (Opponent): It's an irresponsible waste of resources. We should solve Earth's problems like climate change first.")
    ]
    
    try:
        agent_alpha = DebaterAgent(
            topic=test_topic, 
            stance=test_stance, 
            agent_name="Agent Alpha"
        )
        
        # The agent should now reason that it needs facts to counter the "waste of resources" argument.
        # It will likely use the web_search tool.
        new_argument = agent_alpha.generate_argument(mock_history)
        
        print("\n\n✅ --- Test Successful --- ✅")
        print(f"Agent Name: {agent_alpha.name}")
        print("\n--- Agent's Final Generated Argument ---")
        print(new_argument)
        print("-----------------------------------")
        print("\nReview the verbose output above to see if the 'web_search' tool was called.")
        
    except Exception as e:
        print(f"\n❌ --- An error occurred during testing: {e} --- ❌")
        import traceback
        traceback.print_exc()

