
import hashlib

import streamlit as st

from src.pdf_processor import process_pdf
from src.retriever import HybridRetriever
from src.generator import generate_answer

st.set_page_config(
    page_title="ScholarRAG",
    page_icon="📚",
    layout="wide"
)

st.title("📚 ScholarRAG")
st.caption("Research Paper Assistant with Hybrid Retrieval")

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "document_id" not in st.session_state:
    st.session_state.document_id = None

with st.sidebar:
    st.header("Documents")

    uploaded_files = st.file_uploader(
        "Upload research papers",
        type=["pdf"],
        accept_multiple_files=True
    )

    method = st.selectbox(
        "Retrieval method",
        ["Hybrid", "Dense", "BM25"]
    )

    top_k = st.slider(
        "Retrieved chunks",
        min_value=1,
        max_value=10,
        value=5
    )

    if uploaded_files:
        fingerprint = hashlib.sha256()

        for file in uploaded_files:
            fingerprint.update(file.name.encode())
            fingerprint.update(file.getvalue())

        current_id = fingerprint.hexdigest()

        if current_id != st.session_state.document_id:
            with st.spinner("Processing and indexing papers..."):
                all_chunks = []

                for file in uploaded_files:
                    chunks = process_pdf(
                        file.getvalue(),
                        file.name
                    )
                    all_chunks.extend(chunks)

                if all_chunks:
                    st.session_state.retriever = (
                        HybridRetriever(all_chunks)
                    )
                else:
                    st.session_state.retriever = None
                    st.warning("No extractable text found.")

                st.session_state.document_id = current_id

        if st.session_state.retriever:
            st.success("Documents indexed successfully!")
    else:
        st.session_state.retriever = None
        st.session_state.document_id = None

question = st.text_input(
    "Ask a question about your research papers",
    placeholder="What are the limitations of this method?"
)

if st.button("Generate Answer", type="primary"):
    if not question.strip():
        st.warning("Please enter a question.")

    elif st.session_state.retriever is None:
        st.warning("Please upload a PDF first.")

    else:
        with st.spinner("Retrieving evidence..."):
            results = st.session_state.retriever.search(
                question,
                method=method,
                top_k=top_k
            )

        try:
            with st.spinner("Generating answer..."):
                answer = generate_answer(question, results)

            st.subheader("Answer")
            st.write(answer)

            st.subheader("Retrieved Evidence")

            for i, chunk in enumerate(results, start=1):
                with st.expander(
                    f"[{i}] {chunk['source']} "
                    f"— Page {chunk['page']}"
                ):
                    st.write(chunk["text"])

        except Exception as error:
            st.error(f"Generation failed: {error}")
