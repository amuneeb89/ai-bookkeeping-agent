from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import pandas as pd
import io
import os
import google.generativeai as genai

# Load Gemini API Key from environment variable
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ This must exist!
app = FastAPI()

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))

    # Simple analysis
    top_expenses = df.groupby("Category")["Amount"].sum().sort_values(ascending=False).head(3)
    summary = "\n".join([f"{k}: ${v:.2f}" for k, v in top_expenses.items()])

    # Use Gemini to generate insights
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(f"Analyze this:\n{summary}")

    return JSONResponse({
        "top_expenses": top_expenses.to_dict(),
        "ai_summary": response.text
    })
