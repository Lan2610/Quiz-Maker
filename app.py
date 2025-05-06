import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import PyPDF2
import docx
import io

# Dùng mô hình T5 tiếng Việt từ VietAI
model_name = "VietAI/vietnamese-t5"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

def read_file(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return file.read().decode("utf-8")

def summarize_text(text):
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    summaries = []
    for chunk in chunks:
        inputs = tokenizer("Tóm tắt: " + chunk, return_tensors="pt", max_length=512, truncation=True)
        summary_ids = model.generate(inputs["input_ids"], max_length=150, min_length=30, length_penalty=2.0, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        summaries.append(summary)
    return " ".join(summaries)

def generate_quiz(summary):
    sentences = summary.split(".")
    sentences = [s.strip() for s in sentences if s.strip()]
    questions = []
    max_questions = min(len(sentences), 10)

    for i, sentence in enumerate(sentences[:max_questions]):
        if len(sentence.split()) > 5:
            q = f"Câu {i+1}: {sentence.strip()} đúng hay sai?"
            questions.append({"question": q, "options": ["Đúng", "Sai"], "answer": "Đúng"})

    if len(questions) < 5:
        for i, sentence in enumerate(sentences[:max_questions]):
            if len(sentence.split()) <= 5:
                q = f"Câu {i+1}: {sentence.strip()} là đúng hay sai?"
                questions.append({"question": q, "options": ["Đúng", "Sai"], "answer": "Đúng"})
    
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

            quiz = generate_quiz(summary)
            st.subheader("🧠 Trắc nghiệm:")
            for i, q in enumerate(quiz):
                user_answer = st.radio(q["question"], q["options"], key=i)
                if user_answer == q["answer"]:
                    st.success("✅ Chính xác!")
                else:
                    st.error(f"❌ Sai. Đáp án đúng là: {q['answer']}")

if __name__ == "__main__":
    main()
