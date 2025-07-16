from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import pandas as pd
import io
import os
import google.generativeai as genai

# Configure Gemini with your API key from the environment
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        # Read file contents
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        # Ensure required columns exist
        if 'Category' not in df.columns or 'Amount' not in df.columns:
            return JSONResponse(status_code=400, content={
                "error": "CSV must include 'Category' and 'Amount' columns."
            })

        # Convert 'Amount' to numeric
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)

        # Perform top 3 expense analysis
        top_expenses = (
            df.groupby("Category")["Amount"]
            .sum()
            .sort_values(ascending=False)
            .head(3)
        )

        summary_text = "\n".join([f"{cat}: ${amt:.2f}" for cat, amt in top_expenses.items()])

        # Use Gemini Pro model
        model = genai.GenerativeModel("gemini-pro")

        gemini_response = model.generate_content(
            f"Here is a financial summary of top spending categories:\n\n{summ
