import os
from dotenv import load_dotenv
load_dotenv()
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

google_api_key=os.getenv('google_api_key')
if not google_api_key:
    raise ValueError("Google API key is not set in the environment variables.")
llm=ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7
)
print("Gemini initiated")

class Stance(BaseModel):
    """"define a single debating stance with a name and core arguement"""
    agent_name:str=Field(description="a creatinve public-facing name for the debating agent ")
    stance_brief:str=Field(description="A concise, one-sentence summary of the agent's core argument or viewpoint.")
    
class DebateSetup(BaseModel):
    """the complete setup for the debate containing a list of all stances"""
    stances: list[Stance]=Field(description="A list of 2 or 3 distinct and polarizing stances for the debate")
    
orchestrator_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a Debate Topic Analyst. Your role is to analyze a given topic and generate 2 or 3 distinct, polarizing stances for a multi-agent debate. Provide a creative name and a concise brief for each agent's stance. Ensure the stances are genuinely different and create potential for interesting arguments."),
    ("human", "Generate the debate stances for the topic: {topic}")
])

orchestrator_chain=orchestrator_prompt | llm.with_structured_output(DebateSetup)
print("orchestrator chain created")

#debater agents prompt for giving it a personality

debater_prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are a debater in a multi-agent debate.
Your Name: {agent_name}
Your Stance: {stance_brief}

Your goal is to argue your stance persuasively. Respond to the conversation history provided.
Keep your responses concise and to the point.

**Conversation History:**
{conversation_history}

**IMPORTANT:** If you have nothing new or relevant to add to the conversation at this turn, you MUST respond with only the word "PASS" and nothing else.
"""),
    ("human", "Based on the history, what is your next statement or argument?"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

if __name__ == "__main__":
    user_topic = "shoudl AI be used in the military?"
    debate_setup= orchestrator_chain.invoke({"topic": user_topic})
    for i, stance in enumerate(debate_setup.stances):
        print(f"Agent {i+1} Name: {stance.agent_name}")
        print(f"Stance Brief: {stance.stance_brief}\n")

    