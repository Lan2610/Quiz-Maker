import streamlit as st
from transformers import pipeline
import PyPDF2
import docx
import re

# Tạo pipeline tóm tắt với mô hình nhẹ
summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")

# Đọc file PDF, DOCX và TXT
def read_file(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return file.read().decode("utf-8")

# Tóm tắt văn bản
def summarize_text(text):
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    summaries = []
    for chunk in chunks:
        result = summarizer(chunk, max_length=120, min_length=30, do_sample=False)
        summaries.append(result[0]['summary_text'])
    return " ".join(summaries)

# Tìm công thức toán học trong văn bản
def find_formulas(text):
    formulas = []
    # Tìm các công thức đơn giản với regex (Ví dụ: A = πr^2)
    pattern = r"([A-Za-z]+[ ]?=[ ]?[πA-Za-z0-9\^]+)"
    formulas = re.findall(pattern, text)
    return formulas

# Tạo câu hỏi vận dụng công thức
def generate_quiz(summary, formulas):
    sentences = summary.split(".")  # Tách câu bằng dấu chấm
    sentences = [s.strip() for s in sentences if s.strip()]
    
    questions = []
    max_questions = min(len(sentences), 5)  # Tạo tối đa 5 câu hỏi

    # Tạo câu hỏi từ tóm tắt văn bản
    for i, sentence in enumerate(sentences[:max_questions]):
        if len(sentence.split()) > 5:
            q = f"Câu {i+1}: {sentence.strip()} đúng hay sai?"
            questions.append({"question": q, "options": ["Đúng", "Sai"], "answer": "Đúng"})
    
    # Tạo câu hỏi từ công thức toán học
    for i, formula in enumerate(formulas):
        if 'π' in formula:
            q = f"Câu {len(questions)+1}: Nếu bán kính r = 5 cm, tính diện tích của hình tròn có công thức {formula}. (π = 3.14)"
            answer = 3.14 * 5 ** 2  # Áp dụng công thức tính diện tích hình tròn
            questions.append({
                "question": q,
                "options": [str(answer), "Chọn đáp án khác"],
                "answer": str(answer)
            })

    return questions

def main():
    st.title("📚 Quiz Maker - Tóm tắt & Trắc nghiệm từ văn bản")

    uploaded_file = st.file_uploader("Tải lên file PDF, Word hoặc TXT", type=["pdf", "docx", "txt"])

    if uploaded_file is not None:
        with st.spinner("📖 Đang đọc và xử lý nội dung..."):
            text = read_file(uploaded_file)
            summary = summarize_text(text)
            st.subheader("📝 Nội dung được tóm tắt:")
            st.write(summary)

            formulas = find_formulas(text)  # Tìm công thức trong văn bản
            quiz = generate_quiz(summary, formulas)  # Tạo câu hỏi

            st.subheader("🧠 Trắc nghiệm:")
            for i, q in enumerate(quiz):
                user_answer = st.radio(q["question"], q["options"], key=i)
                if user_answer == q["answer"]:
                    st.success("✅ Chính xác!")
                else:
                    st.error(f"❌ Sai. Đáp án đúng là: {q['answer']}")

if __name__ == "__main__":
    main()
