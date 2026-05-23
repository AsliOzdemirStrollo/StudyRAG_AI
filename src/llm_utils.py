import os
import json
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

MODEL_NAME = "gemini-2.5-flash"
# MODEL_NAME = "gemini-2.5-flash-lite"
# MODEL_NAME = "gemini-flash-lite-latest"


def generate_with_retry(prompt, max_retries=3, wait_seconds=3):
    last_error = None

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            return response.text

        except Exception as e:
            last_error = e

            if "503" in str(e) and attempt < max_retries - 1:
                time.sleep(wait_seconds)
                continue

            raise last_error


def generate_answer(question, relevant_chunks, messages):
    context = "\n\n".join(
        [
            f"[Page {chunk['page']}]\n{chunk['text']}"
            for chunk in relevant_chunks
        ]
    )

    history_text = ""

    for msg in messages[-6:]:
        history_text += f"{msg['role']}: {msg['content']}\n"

    prompt = f"""
You are StudyRAG AI, a helpful study assistant.

Answer the user's question using the document context below.

Use the chat history to understand follow-up questions like:
- "what about that?"
- "and in China?"
- "can you explain more?"

If the question has spelling mistakes,
correct the meaning silently.

If the answer is not in the document,
say that clearly.

Chat history:
{history_text}

Document context:
{context}

User question:
{question}

Give a clear, helpful answer in simple language.

When possible, mention the relevant page numbers
from the document using this format:

(Page X)
"""

    try:
        return generate_with_retry(prompt)

    except Exception as e:
        return f"⚠️ Error generating answer:\n\n{str(e)}"


def generate_summary(chunk_data):
    context = "\n\n".join(
        [
            chunk["text"]
            for chunk in chunk_data[:10]
        ]
    )

    prompt = f"""
You are StudyRAG AI, a helpful study assistant.

Create a clear study summary based ONLY
on the document context below.

The summary should:
- explain the main ideas
- highlight important findings
- use headings and bullet points
- be easy for students to study from

Document context:
{context}
"""

    try:
        return generate_with_retry(prompt)

    except Exception as e:
        return f"⚠️ Error generating summary:\n\n{str(e)}"


def generate_quiz(
    chunk_data,
    number_of_questions=10,
    existing_quiz="",
    batch_number=1
):
    context = "\n\n".join(
        [
            chunk["text"]
            for chunk in chunk_data[:14]
        ]
    )

    avoid_text = ""

    if existing_quiz:
        avoid_text = f"""
Existing quiz questions already generated:
{existing_quiz}

IMPORTANT:
Create {number_of_questions} completely NEW questions.
Do NOT repeat the same questions.
Do NOT repeat the same answer options.
Do NOT only rephrase the previous questions.

Focus on different concepts, pages,
pollutants, findings, mechanisms,
risk factors, study results,
or protective measures from the document.
"""

    prompt = f"""
You are StudyRAG AI,
a helpful study assistant.

Create Quiz Batch {batch_number}.

Question numbering instructions:
- If batch_number is 1,
number questions from 1 to 10.
- If batch_number is 2,
number questions from 11 to 20.

Create exactly {number_of_questions}
exam-style multiple choice questions
based ONLY on the document context below.

Return ONLY valid JSON.

The JSON format must look EXACTLY like this:

[
    {{
        "question_number": 1,
        "question": "Question text",
        "options": {{
            "A": "Option A",
            "B": "Option B",
            "C": "Option C",
            "D": "Option D"
        }},
        "correct_answer": "A",
        "explanation": "Explanation text"
    }}
]

The correct_answer field MUST ONLY be one of:
"A", "B", "C", or "D".

Never return E or any other value.

Correct answers must be balanced across A, B, C, and D.
Do not use only B or C.
For 10 questions, use a clear mix of A, B, C, and D as correct answers.
Avoid repeating the same correct answer letter too many times.

Do NOT include markdown.
Do NOT include ```json.
Return ONLY raw JSON.

Questions should:
- be useful for studying
- cover different parts of the document
- avoid repeating concepts
- avoid inventing facts outside the document

{avoid_text}

Document context:
{context}
"""

    try:
        raw_text = generate_with_retry(prompt)

        raw_text = raw_text.strip()

        raw_text = raw_text.replace(
            "```json",
            ""
        )

        raw_text = raw_text.replace(
            "```",
            ""
        )

        quiz_data = json.loads(raw_text)

        return quiz_data

    except Exception as e:
        return f"⚠️ Error generating quiz:\n\n{str(e)}"