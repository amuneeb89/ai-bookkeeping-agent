from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import pandas as pd
import io
import os
import google.generativeai as genai

# ✅ Load your actual Gemini API key (should be set in Render's env vars)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ Use supported model properly
model = genai.GenerativeModel("gemini-pro")

app = FastAPI()

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        # Validate columns
        if "Category" not in df.columns or "Amount" not in df.columns:
            return JSONResponse(status_code=400, content={
                "error": "CSV must include 'Category' and 'Amount' columns."
            })

        # Coerce Amount to numeric
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)

        # Top 3 categories
        top_expenses = df.groupby("Category")["Amount"].sum().sort_values(ascending=False).head(3)
        summary = "\n".join([f"{cat}: ${amt:.2f}" for cat, amt in top_expenses.items()])

        # Gemini prompt
        prompt = f"""Here is a summary of top spending:
{summary}

Please generate insights based on this breakdown.
"""

        response = model.generate_content(prompt)

        return JSONResponse({
            "top_expenses": top_expenses.to_dict(),
            "ai_summary": response.text
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
