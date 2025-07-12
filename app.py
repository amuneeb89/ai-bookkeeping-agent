import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Gemini model
model = genai.GenerativeModel("gemini-pro")

# App layout
st.set_page_config(page_title="Swift Figures - AI Bookkeeping Insights", layout="centered")
st.markdown("## 📊 Swift Figures - AI Bookkeeping Insights Agent")
st.markdown("Upload your bookkeeping CSV file to generate instant insights.")

uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.markdown("### 🔍 Preview of Uploaded Data")
    st.dataframe(df)

    # Format CSV as text
    csv_text = df.to_csv(index=False)

    with st.spinner("Generating insights..."):
        prompt = f"""You are a financial analysis assistant. Analyze the following bookkeeping data in CSV format and provide:
        1. Summary of the period covered, revenue, expenses, and net income
        2. Any anomalies, dependencies, or missing info
        3. Suggested questions for the business owner

        Here is the CSV data:
        {csv_text}
        """

        response = model.generate_content(prompt)
        insights = response.text

    st.markdown("### 📌 Key Insights")
    st.markdown(insights)

    # Optional download or feedback
    st.divider()
    st.markdown("✅ **Done reviewing?**")
    st.download_button("Download Raw CSV", csv_text, file_name="uploaded_data.csv")
