from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import pandas as pd
import io
import os
import google.generativeai as genai

# Correct configuration
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")  # ✅ No "models/" prefix

app = FastAPI()

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        # Validation
        if 'Category' not in df.columns or 'Amount' not in df.columns:
            return JSONResponse(status_code=400, content={
                "error": "CSV must include 'Category' and 'Amount' columns."
            })

        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        top_expenses = df.groupby("Category")["Amount"].sum().sort_values(ascending=False).head(3)
        summary = "\n".join([f"{cat}: ${amt:.2f}" for cat, amt in top_expenses.items()])

        # Generate response using Gemini
        response = model.generate_content(
            f"Here is a financial summary of the top spending categories:\n{summary}\n\nPlease provide insights or trends based on this data."
        )

        return JSONResponse({
            "top_expenses": top_expenses.to_dict(),
            "ai_summary": response.text
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
