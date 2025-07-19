from typing import Annotated
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import tool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variable
serper_api_key = os.getenv("SERPER_API_KEY")
search = None

# Initialize the Google Serper API wrapper only if API key is available
if serper_api_key and serper_api_key != "your_serper_api_key_here":
    search = GoogleSerperAPIWrapper(serper_api_key=serper_api_key)

@tool
def google_search(query: Annotated[str, "The search query to look up"]) -> str:
    """Search the web for information related to a query.

    Args:
        query: The search query to look up

    Returns:
        Search results as text
    """
    if not search:
        return "Google search is not available. Please set up your SERPER_API_KEY in the .env file to enable web search functionality."
    
    try:
        result = search.run(query)
        return result
    except Exception as e:
        return f"I couldn't perform the search due to a technical issue: {str(e)}" 