from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import pandas as pd
import io
import os
import google.generativeai as genai

# Set Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "OK"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        # Validate columns
        if 'Category' not in df.columns or 'Amount' not in df.columns:
            return JSONResponse(status_code=400, content={
                "error": "CSV must contain 'Category' and 'Amount' columns."
            })

        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)

        top_expenses = (
            df.groupby("Category")["Amount"]
            .sum()
            .sort_values(ascending=False)
            .head(3)
        )

        summary = "\n".join([f"{cat}: ${amt:.2f}" for cat, amt in top_expenses.items()])
        prompt = f"""Here is a financial summary of top spending categories:\n\n{summary}\n\nWhat insights or trends can you share?"""

        # FIX: Use latest Gemini Pro generation
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)

        return {
            "top_expenses": top_expenses.to_dict(),
            "ai_summary": response.text
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
