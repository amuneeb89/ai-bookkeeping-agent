import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

# ─── Load config ───────────────────────────────────────────────────────────
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ─── Init Gemini LLM ──────────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)

# ─── Streamlit UI ─────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Bookkeeping Insights")
st.title("📊 Swift Figures – AI Bookkeeping Insights")

uploaded_file = st.file_uploader("Upload your CSV file", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("CSV Preview")
    st.dataframe(df.head())

    # Convert CSV to plain text
    csv_text = df.to_csv(index=False)

    prompt = (
        "You are a bookkeeping assistant. Look at this CSV data and give me key financial "
        "insights, flags, and next-step recommendations:\n\n" + csv_text
    )
    with st.spinner("Analyzing with AI…"):
        # wrap your prompt in a HumanMessage
        message = HumanMessage(content=prompt)
        resp = llm.predict_messages([message])

    st.subheader("✍️ AI Insights")
    st.success(resp.content)
