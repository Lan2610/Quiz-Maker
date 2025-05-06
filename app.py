import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from transformers import pipeline
import random

st.set_page_config(page_title="Quiz Maker", layout="centered")
st.title("AI Quiz Generator")

# AI pipelines
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
qa_generator = pipeline("text2text-generation", model="iarfmoose/t5-base-question-generator")

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

def summarize_text(text):
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    summary = ""
    for chunk in chunks:
        result = summarizer(chunk, max_length=150, min_length=30, do_sample=False)
        summary += result[0]["summary_text"] + " "
    return summary.strip()

def generate_mcq(text, n_questions=5):
    questions = []
    generated = qa_generator(f"generate questions: {text}", max_length=256, num_return_sequences=n_questions)
    for item in generated:
        q_and_a = item['generated_text']
        if "?" in q_and_a:
            q_split = q_and_a.split("?")
            question = q_split[0].strip() + "?"
            answer = q_split[1].strip().split("\n")[0]
            distractors = [answer[::-1], answer.upper(), answer.lower()]
            options = distractors[:2] + [answer]
            random.shuffle(options)
            questions.append({"question": question, "options": options, "answer": answer})
    return questions

uploaded_file = st.file_uploader("Tải lên tài liệu", type=["pdf", "docx", "txt"])

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        text = read_pdf(uploaded_file)
    elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
        text = read_docx(uploaded_file)
    else:
        text = read_txt(uploaded_file)

    with st.spinner("Đang tóm tắt nội dung..."):
        summary = summarize_text(text)
        st.subheader("Tóm tắt nội dung")
        st.write(summary)

    with st.spinner("Đang tạo câu hỏi trắc nghiệm..."):
        questions = generate_mcq(summary)

    st.subheader("Câu hỏi trắc nghiệm")
    for idx, q in enumerate(questions):
        st.markdown(f"**Câu {idx + 1}:** {q['question']}")
        user_ans = st.radio("Chọn đáp án:", q['options'], key=f"q_{idx}")
        if st.button(f"Kiểm tra câu {idx + 1}"):
            if user_ans == q['answer']:
                st.success("Đúng!")
            else:
                st.error(f"Sai. Đáp án đúng là: {q['answer']}")
