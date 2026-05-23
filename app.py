import json
import streamlit as st

from src.pdf_viewer import render_pdf_page_as_image
from src.pdf_utils import extract_pages_from_pdf, split_text_into_chunks
from src.rag_engine import build_vector_store, retrieve_relevant_chunks
from src.llm_utils import generate_answer, generate_summary, generate_quiz

from src.predictor import (
    predict_exam_score,
    generate_prediction_feedback
)

from src.ui_components import (
    apply_custom_css,
    render_header,
    render_sidebar,
    render_document_card,
    render_footer,
)


st.set_page_config(
    page_title="StudyRAG AI",
    page_icon="📚",
    layout="wide"
)

apply_custom_css()
render_header()


# ---------------------------------------------------
# Session State
# ---------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processed_file_name" not in st.session_state:
    st.session_state.processed_file_name = None

if "chunk_data" not in st.session_state:
    st.session_state.chunk_data = []

if "input_counter" not in st.session_state:
    st.session_state.input_counter = 0

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "quiz_part_1" not in st.session_state:
    st.session_state.quiz_part_1 = []

if "quiz_part_2" not in st.session_state:
    st.session_state.quiz_part_2 = []

if "quiz_count" not in st.session_state:
    st.session_state.quiz_count = 0

if "quiz_checked" not in st.session_state:
    st.session_state.quiz_checked = {}

if "quiz_metrics" not in st.session_state:
    st.session_state.quiz_metrics = {
        "correct": 0,
        "wrong": 0,
        "checked": 0,
        "score_percent": 0,
        "completion_percent": 0,
        "document_pages": 0,
        "document_chunks": 0
    }


# ---------------------------------------------------
# Helper Functions
# ---------------------------------------------------

def get_all_quiz_questions():
    return st.session_state.quiz_part_1 + st.session_state.quiz_part_2


def clean_quiz_questions(quiz_data):
    valid_answers = ["A", "B", "C", "D"]
    valid_questions = []

    for question in quiz_data:
        if question.get("correct_answer") in valid_answers:
            valid_questions.append(question)

    return valid_questions


def show_pdf_page_button(page_number, button_key):
    if st.button(f"View Page {page_number}", key=button_key):
        page_image = render_pdf_page_as_image(
            uploaded_file,
            page_number
        )

        if page_image:
            st.image(
                page_image,
                caption=f"PDF Page {page_number}",
                use_container_width=True
            )
        else:
            st.warning("Could not render this page.")


# ---------------------------------------------------
# Interactive Quiz
# ---------------------------------------------------

def render_interactive_quiz():
    all_questions = get_all_quiz_questions()

    if not all_questions:
        return

    correct_count = 0
    checked_count = 0

    st.markdown(
        f"### Interactive Quiz ({len(all_questions)}/20 questions)"
    )

    st.caption(
        "Choose an answer, then click Check Answer. "
        "Correct answers and explanations stay hidden until you check."
    )

    for index, question_data in enumerate(all_questions, start=1):
        question_number = question_data.get("question_number", index)
        question_id = f"q_{question_number}"

        question_text = question_data.get("question", "")
        options = question_data.get("options", {})
        correct_answer = question_data.get("correct_answer", "")
        explanation = question_data.get("explanation", "")

        with st.container():
            st.markdown(f"#### Question {question_number}")
            st.markdown(question_text)

            selected_answer = st.radio(
                "Choose your answer:",
                options=["A", "B", "C", "D"],
                format_func=lambda option: (
                    f"{option}. {options.get(option, '')}"
                ),
                key=f"answer_{question_id}"
            )

            if st.button("Check Answer", key=f"check_{question_id}"):
                st.session_state.quiz_checked[question_id] = selected_answer

            if question_id in st.session_state.quiz_checked:
                checked_count += 1
                user_answer = st.session_state.quiz_checked[question_id]

                if user_answer == correct_answer:
                    correct_count += 1
                    st.success(
                        f"Correct! The answer is {correct_answer}."
                    )
                else:
                    st.error(
                        f"Not quite. You chose {user_answer}. "
                        f"The correct answer is {correct_answer}."
                    )

                with st.expander("Show explanation"):
                    st.write(explanation)

            st.markdown("---")

    if checked_count > 0:
        score_percent = round(
            (correct_count / checked_count) * 100,
            1
        )

        total_questions = len(all_questions)

        completion_percent = round(
            (checked_count / total_questions) * 100,
            1
        )

        document_pages = len(
            set(
                chunk["page"]
                for chunk in st.session_state.chunk_data
            )
        )

        document_chunks = len(st.session_state.chunk_data)

        st.session_state.quiz_metrics = {
            "correct": correct_count,
            "wrong": checked_count - correct_count,
            "checked": checked_count,
            "score_percent": score_percent,
            "completion_percent": completion_percent,
            "document_pages": document_pages,
            "document_chunks": document_chunks
        }

        st.info(
            f"Current checked score: "
            f"{correct_count}/{checked_count} "
            f"({score_percent}%)"
        )


# ---------------------------------------------------
# Sidebar Upload
# ---------------------------------------------------

uploaded_file = render_sidebar()

MAX_FILE_SIZE_MB = 100
WARNING_FILE_SIZE_MB = 30

if uploaded_file:
    file_size_mb = uploaded_file.size / (1024 * 1024)

    if file_size_mb > MAX_FILE_SIZE_MB:
        st.error(
            f"⚠️ File too large. Maximum supported size is "
            f"{MAX_FILE_SIZE_MB} MB. Please upload a smaller PDF."
        )
        st.stop()

    elif file_size_mb > WARNING_FILE_SIZE_MB:
        st.warning(
            "⚠️ Large PDF detected. Processing may take longer than usual."
        )


# ---------------------------------------------------
# Main App
# ---------------------------------------------------

if uploaded_file:
    if st.session_state.processed_file_name != uploaded_file.name:
        with st.spinner(
            "Processing PDF and preparing your study assistant..."
        ):
            pages = extract_pages_from_pdf(uploaded_file)
            chunk_data = split_text_into_chunks(pages)

            if chunk_data:
                build_vector_store(chunk_data)

                st.session_state.chunk_data = chunk_data
                st.session_state.processed_file_name = uploaded_file.name

                st.session_state.messages = []
                st.session_state.summary = ""
                st.session_state.quiz_part_1 = []
                st.session_state.quiz_part_2 = []
                st.session_state.quiz_count = 0
                st.session_state.quiz_checked = {}

                st.session_state.quiz_metrics = {
                    "correct": 0,
                    "wrong": 0,
                    "checked": 0,
                    "score_percent": 0,
                    "completion_percent": 0,
                    "document_pages": 0,
                    "document_chunks": 0
                }

    chunk_data = st.session_state.chunk_data

    if not chunk_data:
        st.warning("No readable text found in this PDF.")

    else:
        render_document_card(uploaded_file, chunk_data)

        st.subheader("📘 Study Tools")

        col1, col2 = st.columns(2)

        # ---------------------------------------------------
        # Summary
        # ---------------------------------------------------

        with col1:
            st.markdown("### 📄 Summary")

            st.caption(
                "Generate a concise study summary "
                "from the uploaded PDF."
            )

            if st.button("Generate Summary"):
                with st.spinner("Creating summary..."):
                    new_summary = generate_summary(chunk_data)

                if (
                    isinstance(new_summary, str)
                    and new_summary.startswith("⚠️ Error")
                ):
                    st.error(new_summary)
                else:
                    st.session_state.summary = new_summary

            if st.session_state.summary:
                st.text_area(
                    "Document Summary",
                    st.session_state.summary,
                    height=500
                )

        # ---------------------------------------------------
        # Quiz
        # ---------------------------------------------------

        with col2:
            st.markdown("### 📝 Quiz")

            st.caption(
                "Generate up to 20 interactive "
                "multiple choice questions."
            )

            if not st.session_state.quiz_part_1:
                if st.button("Generate 10 Quiz Questions"):
                    with st.spinner(
                        "Creating first 10 quiz questions..."
                    ):
                        new_quiz = generate_quiz(
                            chunk_data,
                            number_of_questions=10,
                            batch_number=1
                        )

                    if (
                        isinstance(new_quiz, str)
                        and new_quiz.startswith("⚠️ Error")
                    ):
                        st.error(new_quiz)

                    elif isinstance(new_quiz, list):
                        valid_quiz = clean_quiz_questions(new_quiz)

                        if not valid_quiz:
                            st.error(
                                "Quiz generation failed because "
                                "no valid A-D answers were returned."
                            )
                        else:
                            st.session_state.quiz_part_1 = valid_quiz
                            st.session_state.quiz_count = len(valid_quiz)
                            st.rerun()

            elif (
                st.session_state.quiz_part_1
                and not st.session_state.quiz_part_2
            ):
                if st.button("Generate Other 10 Questions"):
                    with st.spinner(
                        "Creating 10 more different questions..."
                    ):
                        existing_quiz_text = json.dumps(
                            st.session_state.quiz_part_1,
                            ensure_ascii=False
                        )

                        new_quiz = generate_quiz(
                            chunk_data,
                            number_of_questions=10,
                            existing_quiz=existing_quiz_text,
                            batch_number=2
                        )

                    if (
                        isinstance(new_quiz, str)
                        and new_quiz.startswith("⚠️ Error")
                    ):
                        st.error(new_quiz)

                    elif isinstance(new_quiz, list):
                        valid_quiz = clean_quiz_questions(new_quiz)

                        if not valid_quiz:
                            st.error(
                                "Quiz generation failed because "
                                "no valid A-D answers were returned."
                            )
                        else:
                            st.session_state.quiz_part_2 = valid_quiz
                            st.session_state.quiz_count = (
                                len(st.session_state.quiz_part_1)
                                + len(st.session_state.quiz_part_2)
                            )
                            st.rerun()

            else:
                st.info(
                    "You have generated the maximum "
                    "of 20 quiz questions for this PDF."
                )

        # ---------------------------------------------------
        # Interactive Quiz Render
        # ---------------------------------------------------

        if st.session_state.quiz_part_1:
            st.markdown("---")
            render_interactive_quiz()

        # ---------------------------------------------------
        # Chatbot
        # ---------------------------------------------------

        st.markdown("---")

        st.subheader("💬 Chat with your PDF")

        st.caption(
            "Ask questions, use follow-ups like "
            "“what about China?”, and check the "
            "source pages below each answer."
        )

        for msg_index, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

                if msg["role"] == "assistant" and "pages" in msg:
                    referenced_pages = msg["pages"]

                    if referenced_pages:
                        st.markdown("**Referenced pages:**")

                        for page_number in referenced_pages:
                            show_pdf_page_button(
                                page_number,
                                button_key=(
                                    f"history_page_"
                                    f"{msg_index}_"
                                    f"{page_number}"
                                )
                            )

        with st.form("chat_form"):
            user_question = st.text_input(
                "Your question",
                placeholder="Ask something about the PDF...",
                key=f"user_input_{st.session_state.input_counter}"
            )

            send_button = st.form_submit_button("Send")

        if send_button and user_question.strip():
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": user_question
                }
            )

            relevant_chunks = retrieve_relevant_chunks(user_question)

            with st.chat_message("user"):
                st.markdown(user_question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = generate_answer(
                        user_question,
                        relevant_chunks,
                        st.session_state.messages
                    )

                    referenced_pages = sorted(
                        set(chunk["page"] for chunk in relevant_chunks)
                    )

                    st.markdown(answer)

                    if referenced_pages:
                        st.markdown("**Referenced pages:**")

                        for page_number in referenced_pages:
                            show_pdf_page_button(
                                page_number,
                                button_key=(
                                    f"answer_page_"
                                    f"{page_number}_"
                                    f"{st.session_state.input_counter}"
                                )
                            )

                with st.expander("📚 View source text used"):
                    for i, chunk in enumerate(
                        relevant_chunks,
                        start=1
                    ):
                        relevance = "High"

                        if chunk["score"] < 0.25:
                            relevance = "Medium"

                        if chunk["score"] < 0.15:
                            relevance = "Low"

                        page_number = chunk["page"]

                        st.markdown(
                            f"**Source {i} — "
                            f"Page {page_number} "
                            f"| Relevance: "
                            f"{relevance}**"
                        )

                        show_pdf_page_button(
                            page_number,
                            button_key=(
                                f"source_page_"
                                f"{i}_"
                                f"{page_number}_"
                                f"{st.session_state.input_counter}"
                            )
                        )

                        st.write(chunk["text"][:900] + "...")

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "pages": referenced_pages
                }
            )

            st.session_state.input_counter += 1
            # st.rerun()

        # ---------------------------------------------------
        # Performance Prediction
        # ---------------------------------------------------

        st.markdown("---")

        st.subheader("📈 Performance Prediction")

        st.caption(
            "Predict your next exam score using your previous mark, "
            "available study time, quiz performance, and document length."
        )

        prediction_col1, prediction_col2, prediction_col3 = st.columns(3)

        with prediction_col1:
            previous_score = st.number_input(
                "Previous exam score (%)",
                min_value=0,
                max_value=100,
                value=70
            )

        with prediction_col2:
            days_left = st.number_input(
                "Days left until exam",
                min_value=0,
                max_value=365,
                value=7
            )

        with prediction_col3:
            study_hours = st.number_input(
                "Planned study hours",
                min_value=0,
                max_value=200,
                value=10
            )

        quiz_metrics = st.session_state.quiz_metrics

        if quiz_metrics["checked"] == 0:
            st.warning(
                "⚠️ Complete quiz questions to improve prediction accuracy."
            )

        elif quiz_metrics["completion_percent"] < 50:
            st.info(
                "ℹ️ Prediction reliability improves when more quiz "
                "questions are completed."
            )

        elif quiz_metrics["completion_percent"] < 100:
            st.success(
                "✅ Good quiz coverage. Completing all questions "
                "can further improve prediction reliability."
            )

        else:
            st.success(
                "🎯 Full quiz completed. Prediction confidence is high."
            )

        if st.button("Predict Exam Score"):
            predicted_score = predict_exam_score(
                previous_score=previous_score,
                days_left=days_left,
                study_hours=study_hours,
                quiz_score=quiz_metrics["score_percent"],
                completion_percent=quiz_metrics["completion_percent"],
                document_pages=quiz_metrics["document_pages"],
                document_chunks=quiz_metrics["document_chunks"]
            )

            st.success(
                f"Predicted next exam score: "
                f"{predicted_score}%"
            )

            feedback_list = generate_prediction_feedback(
                predicted_score=predicted_score,
                quiz_score=quiz_metrics["score_percent"],
                days_left=days_left,
                study_hours=study_hours,
                document_pages=quiz_metrics["document_pages"]
            )

            st.markdown("### Prediction Factors")

            for item in feedback_list:
                st.write(item)

            st.caption(
                f"Based on quiz score: "
                f"{quiz_metrics['score_percent']}%, "
                f"completion: "
                f"{quiz_metrics['completion_percent']}%, "
                f"document pages: "
                f"{quiz_metrics['document_pages']}, "
                f"chunks: "
                f"{quiz_metrics['document_chunks']}."
            )

else:
    st.info(
        "Upload a PDF from the sidebar "
        "to start using StudyRAG AI."
    )


render_footer()