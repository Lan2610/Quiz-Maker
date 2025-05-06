from transformers import pipeline

# Nếu bạn đã tải mô hình t5-small từ Hugging Face, bạn có thể lưu vào thư mục cục bộ và sử dụng lại
summarizer = pipeline("summarization", model="/path/to/your/local/t5-small", tokenizer="/path/to/your/local/t5-small")

def summarize_text(text):
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    summaries = []
    for chunk in chunks:
        result = summarizer(chunk, max_length=120, min_length=30, do_sample=False)
        summaries.append(result[0]['summary_text'])
    return " ".join(summaries)
