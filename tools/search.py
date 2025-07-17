import os
from dotenv import load_dotenv
load_dotenv()
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool

@tool
def web_search(query: str) -> str:
    """
    Performs a web search using the Tavily search engine to find real-time,
    up-to-date information on a given topic, event, or question.

    This tool is best used when you need current information or facts that
    are not part of your existing knowledge.

    Args:
        query: The specific search query or question to look up.
    """
    print(f"\033[32mPerforming web search for: {query}\033[0m")
    
    tavil_search = TavilySearchResults(
        max_results=1
    )
    
    results= tavil_search.invoke(query)
    return results

if __name__ == "__main__":
    print("testing web search tool...")
    query = "What is the role of AI in modern military?"
    results = web_search(query)
    print("Web search results:")
    for result in results:
        print(f" - {result}")
