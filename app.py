import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import random

st.set_page_config(page_title="AI Quiz Maker", layout="centered")
st.title("🧠 AI Tóm tắt & Tạo câu hỏi trắc nghiệm")

def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"
    return text

def read_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def read_txt(file):
    return file.read().decode("utf-8")

def summarize_text(text, sentence_count=5):
    # Tóm tắt thủ công bằng cách chọn ra những câu dài nhất
    sentences = text.split(".")
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    sentences.sort(key=lambda s: len(s), reverse=True)
    summary = sentences[:sentence_count]
    return ". ".join(summary) + "."

def generate_questions(summary_text, num_questions=3):
    sentences = summary_text.split(". ")
    questions = []
    for i in range(min(num_questions, len(sentences))):
        sentence = sentences[i].strip()
        if len(sentence.split()) < 4:
            continue
        answer = sentence.split()[-1].strip(".")
        question = sentence.replace(answer, "______")
        options = [answer, answer[::-1], answer.upper()]
        random.shuffle(options)
        questions.append({
            "question": question,
            "options": options,
            "answer": answer
        })
    return questions

uploaded_file = st.file_uploader("📄 Tải tài liệu (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        text = read_pdf(uploaded_file)
    elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
        text = read_docx(uploaded_file)
    else:
        text = read_txt(uploaded_file)

    st.subheader("📌 Tóm tắt nội dung:")
    summary = summarize_text(text)
    st.write(summary)

    st.subheader("❓ Câu hỏi trắc nghiệm")
    quiz = generate_questions(summary)

    for idx, q in enumerate(quiz):
        st.markdown(f"**Câu {idx+1}:** {q['question']}")
        ans = st.radio("Chọn đáp án:", q['options'], key=f"q_{idx}")
        if st.button(f"Kiểm tra câu {idx+1}"):
            if ans == q["answer"]:
                st.success("✅ Chính xác!")
            else:
                st.error(f"❌ Sai rồi. Đáp án đúng: {q['answer']}")
