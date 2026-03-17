from dotenv import load_dotenv
import os

load_dotenv()

print("OPENAI configurada:", bool(os.getenv("OPENAI_API_KEY")))
print("NEWS configurada:", bool(os.getenv("NEWS_API_KEY")))