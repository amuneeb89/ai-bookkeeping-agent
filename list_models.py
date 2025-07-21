# list_models.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()  # loads GOOGLE_API_KEY from .env
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("Models available to your key:\n")
for m in genai.list_models():   # directly iterate the generator
    print(" •", m.name)
