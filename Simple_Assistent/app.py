from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM

import streamlit as st
import os
from dotenv import load_dotenv
import uuid

# -------------------------
# Load ENV (FIRST)
# -------------------------
load_dotenv()

LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
if not LANGCHAIN_API_KEY:
    raise ValueError("LANGCHAIN_API_KEY missing")

# Force tracing config
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "simple-assistant"

st.sidebar.write("API KEY:", os.getenv("LANGCHAIN_API_KEY"))
st.sidebar.write("TRACING:", os.getenv("LANGCHAIN_TRACING_V2"))
st.sidebar.write("PROJECT:", os.getenv("LANGCHAIN_PROJECT"))

# -------------------------
# Debug (REMOVE in prod)
# -------------------------
st.sidebar.write("Tracing:", os.getenv("LANGCHAIN_TRACING_V2"))
st.sidebar.write("Project:", os.getenv("LANGCHAIN_PROJECT"))

# -------------------------
# Session (for observability)
# -------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# -------------------------
# Prompt
# -------------------------
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a concise and helpful assistant."),
        ("user", "Question: {question}")
    ]
)

# -------------------------
# LLM (add timeout control)
# -------------------------
llm = OllamaLLM(
    model="llama3",
    timeout=60  # avoid infinite wait
)

# -------------------------
# Chain
# -------------------------
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# -------------------------
# Streamlit UI
# -------------------------
st.title("LangChain + Ollama + LangSmith")

input_text = st.text_input("Ask something")

# -------------------------
# Execution (with tracing context)
# -------------------------
if input_text:
    try:
        with st.spinner("Thinking..."):
            response = chain.invoke(
                {"question": input_text},
                config={
                    "metadata": {
                        "session_id": st.session_state.session_id,
                        "source": "streamlit"
                    },
                    "tags": ["ollama", "local-llm"]
                }
            )

        st.write(response)

    except Exception as e:
        st.error(f"Error: {str(e)}")