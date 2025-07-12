import os
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load CSV
def load_csv(file_path):
    df = pd.read_csv(file_path)
    print("✅ CSV loaded successfully.")
    return df

# Generate insights
def get_insights(prompt):
    model = genai.GenerativeModel("gemini-1.5-pro")  # ✅ Correct model
    response = model.generate_content([prompt])  # ✅ Prompt must be a list
    return response.text

# Main execution
if __name__ == "__main__":
    csv_file = "data/input.csv"
    df = load_csv(csv_file)

    prompt = (
        "You are a bookkeeping assistant. Provide insights from this financial data:\n\n"
        + df.head(10).to_string()
    )

    print("📤 Sending data to Gemini...")
    insights = get_insights(prompt)
    print("\n📊 Insights Generated:\n")
    print(insights)
