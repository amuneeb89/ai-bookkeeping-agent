import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import AnalyzeDocumentChain

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini Pro LLM from LangChain
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)
qa_chain = AnalyzeDocumentChain(combine_docs_chain=llm)

# Streamlit UI
st.set_page_config(page_title="AI Bookkeeping Insights", page_icon=":bar_chart:")
st.markdown("<h1 style='text-align: center;'>📊 Swift Figures – AI Bookkeeping Insights Agent</h1>", unsafe_allow_html=True)
st.write("Upload your CSV file")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        # Display DataFrame preview
        st.subheader("📄 CSV Preview")
        st.dataframe(df.head(10))

        # Convert CSV to plain text for LLM input
        csv_text = df.to_csv(index=False)

        with st.spinner("Analyzing with AI..."):
            response = qa_chain.run(csv_text)

        st.subheader("🧠 AI Insights")
        st.success(response)

    except Exception as e:
        st.error(f"Something went wrong: {e}")
