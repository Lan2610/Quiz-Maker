import streamlit as st
import tempfile
import os
from PyPDF2 import PdfReader
import docx
from transformers import pipeline

# Load summarizer and QA generator
summarizer = pipeline("summarization")
qa_generator = pipeline("text2text-generation", model="valhalla/t5-small-e2e-qg")

st.title("AI Quiz Generator from Document")
st.write("Tải lên file PDF, DOCX hoặc văn bản để tạo tóm tắt và câu hỏi trắc nghiệm.")

uploaded_file = st.file_uploader("Chọn tài liệu", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    # Đọc nội dung
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
    else:
        text = uploaded_file.read().decode("utf-8")

    st.subheader("Tóm tắt nội dung")
    summary = summarizer(text[:1000])[0]['summary_text']  # giới hạn để tránh quá tải
    st.write(summary)

    st.subheader("Câu hỏi trắc nghiệm (có đáp án)")
    generated = qa_generator("generate questions: " + summary, max_length=256, do_sample=False)[0]['generated_text']
    questions = generated.split("\n")

    quiz_data = []

    for q in questions:
        if q.strip():
            parts = q.split("?")
            if len(parts) >= 2:
                question = parts[0].strip() + "?"
                options = parts[1].strip().split(";")
                if len(options) >= 2:
                    correct = options[0].strip()
                    distractors = options[1:]
                    all_options = [correct] + distractors
                    all_options = list(set(all_options))[:4]  # Giới hạn 4 lựa chọn
                    quiz_data.append({
                        "question": question,
                        "options": all_options,
                        "answer": correct
                    })

    if not quiz_data:
        st.warning("Không thể tạo được câu hỏi có định dạng chuẩn. Vui lòng thử với tài liệu khác hoặc nội dung khác.")

    else:
        st.subheader("Mini Quiz Game")
        for idx, item in enumerate(quiz_data):
            st.write(f"*Câu {idx+1}: {item['question']}*")
            choice = st.radio("Chọn đáp án:", item['options'], key=f"q{idx}")
            if st.button(f"Kiểm tra câu {idx+1}", key=f"check{idx}"):
                if choice == item['answer']:
                    st.success("Đúng!")
                else:
                    st.error(f"Sai. Đáp án đúng là: {item['answer']}")
