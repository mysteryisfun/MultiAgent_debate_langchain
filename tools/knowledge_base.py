from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
import os
_retriever = None
from dotenv import load_dotenv
load_dotenv()

def _initialize_retriever():
    """Loads the document, splits it, creates embeddings, and builds retriever"""
    
    global _retriever
    if _retriever is not None:
        return _retriever
    print("Initializing Knowledge Base Retriever...")
    
    # Load the PDF file instead of a text file
    loader = PyPDFLoader("docs/ai_military.pdf")
    documents = loader.load()
    
    text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)
    
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001", google_api_key=os.getenv("google_api_key"))
    
    db = Chroma.from_documents(docs, embeddings, persist_directory="chroma_db")
    _retriever = db.as_retriever(search_kwargs={"k": 1})
    return _retriever

@tool
def knowledge_base_search(query: str) -> str:
    """
    Searches the knowledge base document (a report on AI ethics in urban planning)
    to find specific information, definitions, or arguments related to the report.
    Use this tool when you need to cite specific details from the official report.

    Args:
        query: The specific question or topic to look up in the knowledge base.
    """
    print(f"\033[32m--- Executing Knowledge Base Search with query: '{query}' ---\033[0m")
    retriever = _initialize_retriever()
    
    docs = retriever.invoke(query)
    unique_docs = list({doc.page_content for doc in docs})  # Remove duplicates
    return "\n\n".join(unique_docs)

if __name__ == "__main__":
    print("testing KB")
    _initialize_retriever()
    query = "What are the main ethical concerns regarding AI in military applications"
    print(knowledge_base_search(query))