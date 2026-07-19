import os
from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Load the hidden variables from .env
load_dotenv(find_dotenv(), override=True)
my_key = os.getenv("GOOGLE_API_KEY")

# 2. Initialize the AI Brain
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0.7,
    api_key=my_key
)

print("🚀 Sending a study question to Gemini...")

# 3. Ask a real study question
response = llm.invoke("Explain photosynthesis in exactly one short sentence.")

# 4. Extract JUST the clean text (to avoid that giant data block you saw last time)
if isinstance(response.content, list):
    # Sometimes Gemini sends a list of data blocks, so we grab just the text part
    clean_text = response.content[0].get('text', '')
else:
    # Otherwise, it's already a clean string
    clean_text = response.content

# 5. Print the beautifully clean response
print("🤖 AI says:", clean_text)