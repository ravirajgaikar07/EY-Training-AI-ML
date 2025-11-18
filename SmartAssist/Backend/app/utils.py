import re

def clean_text(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    text = re.sub(r"[\r\t\f\v]", " ", text)
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"([!.?])\1+", r"\1", text)
    text = text.strip()
    return text
def chunk_text(text: str, max_tokens=300, overlap=50):
    text = clean_text(text)
    words = text.split()
    chunks = []
    start = 0
    end = max_tokens
    while start < len(words):
        chunk_words = words[start:end]
        chunk_texts = " ".join(chunk_words)

        chunks.append({"chunk": chunk_texts})

        start = end - overlap
        if start < 0:
            start = 0
        end = start + max_tokens

    # assign IDs
    for i, c in enumerate(chunks):
        c["id"] = i

    return chunks
