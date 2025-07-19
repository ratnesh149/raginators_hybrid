from langchain_openai import ChatOpenAI
import os

# Load environment variables from the .env file
from dotenv import load_dotenv
load_dotenv()

# Check if the OPENAI_API_KEY is set
if 'OPENAI_API_KEY' not in os.environ:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables. Please set it in the .env file.")

llm = ChatOpenAI(model_name="gpt-4o", api_key=os.environ['OPENAI_API_KEY'])
