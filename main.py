import os
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import requests
from io import StringIO

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables (Render)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent"

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode("utf-8")))

        summary = df.describe(include="all").to_string()

        prompt = f"Here is a financial summary of top spending categories:\n\n{summary}\n\nWhat insights can you provide?"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_API_KEY
        }

        response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
        response.raise_for_status()

        gemini_reply = response.json()
        ai_response = gemini_reply.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

        return JSONResponse(content={"insights": ai_response})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
