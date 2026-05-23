import streamlit as st


def apply_custom_css():
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1150px;
        }

        .title-card {
            background: linear-gradient(135deg, #2F4F4F, #4C6A6A);
            padding: 2rem;
            border-radius: 22px;
            border: 1px solid #E5E7EB;
            margin-bottom: 1.5rem;
        }

        .title-card h1 {
            margin-bottom: 0.3rem;
            font-size: 2.4rem;
            color: #FFFFFF;
        }

        .subtitle {
            color: #E5E7EB;
            font-size: 1.05rem;
        }

        .info-card {
            background-color: #FFFFFF;
            padding: 1rem 1.2rem;
            border-radius: 16px;
            border: 1px solid #E5E7EB;
            margin-bottom: 1rem;
        }

        .small-muted {
            color: #6B7280;
            font-size: 0.9rem;
        }

        section[data-testid="stSidebar"] {
            background-color: #2E4A4A;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p {
            color: #F9FAFB;
        }

        section[data-testid="stSidebar"] 
        [data-testid="stFileUploaderFileName"] {
            color: #F9FAFB !important;
        }

        section[data-testid="stSidebar"] .stButton button {
            color: #111827 !important;
            background-color: #F9FAFB !important;
        }

        section[data-testid="stSidebar"] .stButton button * {
            color: #111827 !important;
        }

        section[data-testid="stSidebar"] .stButton button:hover {
            color: #111827 !important;
            background-color: #E5E7EB !important;
        }

        .footer {
            text-align: center;
            color: #6B7280;
            font-size: 0.9rem;
            margin-top: 3rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_header():
    st.markdown(
        """
        <div class="title-card">
            <h1>📚 StudyRAG AI</h1>
            <p style="
            font-size: 1.15rem;
            font-weight: 600;
            color: #D1D5DB;
            margin-bottom: 0.7rem;
        ">
            Interactive Study Assistant
            </p>
            <p class="subtitle">
            Upload study materials, generate intelligent summaries and quizzes,
            interact with documents through Retrieval-Augmented Generation (RAG),
            and receive context-aware AI assistance for adaptive learning.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_sidebar():
    with st.sidebar:
        st.header("⚙️ StudyRAG Controls")

        uploaded_file = st.file_uploader(
            "Upload your PDF",
            type=["pdf"],
            key="pdf_uploader"
        )

        st.caption(
            "Recommended PDF size: under 30MB. "
            "Files over 100MB will not be processed."
        )

        st.markdown("---")

        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.success("Chat history cleared.")

    return uploaded_file


def render_document_card(uploaded_file, chunk_data):
    page_count = len(set(chunk["page"] for chunk in chunk_data))

    st.markdown(
        f"""
        <div class="info-card">
            <strong>📄 Current document:</strong> {uploaded_file.name}<br>
            <span class="small-muted">
                Pages processed: {page_count} • Chunks created: {len(chunk_data)} • Retrieval: embeddings + reranking
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_footer():
    st.markdown(
        """
        <div class="footer">
            StudyRAG AI • Built by Asli Özdemir Strollo using Streamlit, Gemini API, ChromaDB, and Sentence Transformers
        </div>
        """,
        unsafe_allow_html=True
    )