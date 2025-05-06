import streamlit as st
from transformers import pipeline
import os
from io import StringIO
from docx import Document
import PyPDF2

# Kiểm tra nếu mô hình đã được tải về cục bộ
model_name = "t5-small"

if not os.path.exists(f"./{model_name}"):
    # Nếu chưa có mô hình, tải từ Hugging Face Hub
    summarizer = pipeline("summarization", model=model_name, tokenizer=model_name)
else:
    # Nếu mô hình đã có, sử dụng mô hình từ thư mục cục bộ
    summarizer = pipeline("summarization", model=f"./{model_name}", tokenizer=f"./{model_name}")

def summarize_text(text):
    # Chia văn bản thành các đoạn nhỏ hơn để xử lý
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    summaries = []
    
    # Tạo tóm tắt cho từng đoạn
    for chunk in chunks:
        result = summarizer(chunk, max_length=120, min_length=30, do_sample=False)
        summaries.append(result[0]['summary_text'])
    
    return " ".join(summaries)

def extract_text_from_pdf(file):
    # Mở file PDF và trích xuất văn bản
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

def extract_text_from_docx(file):
    # Mở file DOCX và trích xuất văn bản
    doc = Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def extract_text_from_txt(file):
    # Mở file TXT và trích xuất văn bản
    text = file.read().decode("utf-8")
    return text

st.title("Ứng dụng Tóm tắt và Tạo câu hỏi Quiz")
st.write("Tải lên một tệp PDF, DOCX hoặc TXT để tạo tóm tắt và câu hỏi quiz!")

# Cho phép người dùng tải lên file
uploaded_file = st.file_uploader("Tải lên file", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    # Xác định loại tệp người dùng tải lên và trích xuất văn bản
    if uploaded_file.type == "application/pdf":
        text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = extract_text_from_docx(uploaded_file)
    elif uploaded_file.type == "text/plain":
        text = extract_text_from_txt(uploaded_file)

    # Hiển thị văn bản đã tải lên
    st.subheader("Văn bản đã tải lên:")
    st.write(text)

    # Tóm tắt văn bản
    st.subheader("Tóm tắt:")
    summary = summarize_text(text)
    st.write(summary)

    # Tạo câu hỏi quiz từ tóm tắt
    st.subheader("Câu hỏi Quiz:")
    # Bạn có thể áp dụng logic tạo câu hỏi tại đây (giả lập hoặc sử dụng mô hình để tạo câu hỏi từ tóm tắt)
    questions = [
        {"question": "Câu hỏi 1: Tóm tắt nội dung chính của văn bản trên là gì?", "options": ["Tóm tắt 1", "Tóm tắt 2", "Tóm tắt 3"], "answer": "Tóm tắt 1"},
        {"question": "Câu hỏi 2: Nội dung của phần này nói về cái gì?", "options": ["Phần 1", "Phần 2", "Phần 3"], "answer": "Phần 1"},
    ]

    # Hiển thị câu hỏi quiz
    for q in questions:
        st.write(q["question"])
        st.radio("Chọn đáp án", q["options"], index=0)
