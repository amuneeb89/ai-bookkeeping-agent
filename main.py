from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import pandas as pd
import io
import os
import google.generativeai as genai

# Load Gemini API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        if "Description" not in df.columns or "Amount" not in df.columns:
            return JSONResponse(
                status_code=400,
                content={"error": "CSV must contain 'Description' and 'Amount' columns."}
            )

        # Simple analysis
        top_expenses = df.groupby("Description")["Amount"].sum().sort_values(ascending=True).head(3)
        summary = "\n".join([f"{k}: ${v:.2f}" for k, v in top_expenses.items()])

        # AI call
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"Analyze the following:\n{summary}")

        return JSONResponse({
            "top_expenses": top_expenses.to_dict(),
            "ai_summary": response.text
        })

    except Exception as e:
        print("❌ ERROR:", str(e))  # <--- This will print to Render logs
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error. Check server logs."}
        )
