import streamlit as st
from PyPDF2 import PdfReader
import docx
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import random

# Tải dữ liệu tokenizer
nltk.download('punkt')

st.set_page_config(page_title="Quiz Maker", layout="wide")

st.title("🧠 Quiz Maker từ tài liệu PDF / Word / Text")

# Hàm đọc nội dung từ các loại file
def read_file(file):
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages])
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return file.read().decode("utf-8")

# Tóm tắt văn bản
def summarize_text(text, sentence_count=5):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    return " ".join(str(sentence) for sentence in summary)

# Tạo câu hỏi từ đoạn tóm tắt
def generate_questions(summary, num_questions=5):
    sentences = summary.split(". ")
    questions = []
    for i in range(min(num_questions, len(sentences))):
        sentence = sentences[i].strip()
        if len(sentence.split()) < 5:
            continue
        words = sentence.split()
        if len(words) < 4:
            continue
        keyword = random.choice(words)
        question = sentence.replace(keyword, "_____")
        distractors = random.sample([w for w in words if w != keyword], k=min(3, len(words)-1))
        options = distractors + [keyword]
        random.shuffle(options)
        questions.append({
            "question": question,
            "options": options,
            "answer": keyword
        })
    return questions

# Tải file
uploaded_file = st.file_uploader("Tải file PDF, DOCX hoặc TXT", type=["pdf", "docx", "txt"])

if uploaded_file:
    text = read_file(uploaded_file)
    st.subheader("📄 Nội dung gốc:")
    st.text_area("Văn bản", text, height=200)

    summary = summarize_text(text)
    st.subheader("✍️ Tóm tắt:")
    st.write(summary)

    questions = generate_questions(summary)
    st.subheader("📝 Bộ câu hỏi trắc nghiệm:")

    for i, q in enumerate(questions):
        st.markdown(f"**Câu {i+1}:** {q['question']}")
        answer = st.radio("Chọn đáp án:", q["options"], key=f"q{i}")
        if answer == q["answer"]:
            st.success("✅ Chính xác!")
        else:
            st.error(f"❌ Sai. Đáp án đúng là: **{q['answer']}**")
        st.markdown("---")
