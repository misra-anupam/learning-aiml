from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
load_dotenv()

model = ChatOpenRouter(
    model = "openai/gpt-5-nano"
)