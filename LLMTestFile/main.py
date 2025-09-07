## Test file for testing LLM API's

import google.generativeai as genai
from dotenv import load_dotenv
import os


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')


prompt = "What is the meainig of AI"
response = model.generate_content(prompt)

print(response.text)