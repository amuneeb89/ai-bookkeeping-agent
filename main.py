import os
import csv
import json
import tempfile
import requests
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enable CORS (open access for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

@app.get("/")
def read_root():
    return {"status": "AI Bookkeeping Agent is live!"}

@app.get("/analyze/health")
def health_check():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze_csv(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        with open(tmp_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            header = rows[0]
            sample = rows[1:6]

        formatted_sample = "\n".join([", ".join(row) for row in sample])
        prompt = (
            f"You're an AI Bookkeeping Assistant.\n\n"
            f"Here is a sample of the bookkeeping data:\n\n"
            f"{', '.join(header)}\n{formatted_sample}\n\n"
            f"Please provide a few insights from this data and suggest what a business owner should know."
        )

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GOOGLE_API_KEY,
        }

        body = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        response = requests.post(GEMINI_API_URL, headers=headers, json=body)
        response.raise_for_status()
        result = response.json()
        ai_text = result["candidates"][0]["content"]["parts"][0]["text"]

        return JSONResponse(content={"insights": ai_text})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
