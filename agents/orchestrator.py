import os
from dotenv import load_dotenv
load_dotenv()
import re

from pydantic import BaseModel, Field

from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

from utils.prompts import orchestrator_template

class DebateStance(BaseModel):
    stances: list[str] = Field(description="A list of 2-3 distinct and polarizing debate stances.")
    
google_api_key = os.getenv("google_api_key")

def generate_debate_stances(topic:str) ->list[str]:
    """Uses an LLM to generate polarized stances for a given debate topic.
    This function demonstrates a simple LangChain Expression Language (LCEL) chain.

    Args:
        topic: The topic of the debate.

    Returns:
        A list of strings, where each string is a distinct debate stance.
    """
    print("Orchestrator initializing...")
    
    parser= PydanticOutputParser(pydantic_object=DebateStance)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.7,
        google_api_key=google_api_key
    )
    
    print("orchestrator chain initialized.")
    orchestrator_prompt = orchestrator_template.partial(
        format_instructions=parser.get_format_instructions(),
        messages=[]  # Initialize the agent's scratchpad as an empty list
    )
    orchestrator_chain = orchestrator_prompt | llm | parser
    
    response_object = orchestrator_chain.invoke({"topic": topic})
    print("Orchestrator response received :",response_object)
    return response_object.stances

if __name__ == "__main__":
    print("Starting Orchestrator...")
    test_topic="the role of ai in modern military"
    
    generated_stances=generate_debate_stances(test_topic)
    if generated_stances:
        print("Generated Stances:")
        for i, stance in enumerate(generated_stances, start=1):
            print(f"{i}. {stance}")
    
    
    
    
    