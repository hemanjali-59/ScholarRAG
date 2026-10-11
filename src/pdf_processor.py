import fitz


def process_pdf(file_bytes, filename, chunk_size=900, overlap=150):
    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")

    chunks = []

    with fitz.open(stream=file_bytes, filetype="pdf") as document:
        for page_number, page in enumerate(document, start=1):
            text = " ".join(page.get_text().split())

            if not text:
                continue

            step = chunk_size - overlap

            for start in range(0, len(text), step):
                content = text[start:start + chunk_size]

                if not content.strip():
                    continue

                chunks.append({
                    "text": content,
                    "source": filename,
                    "page": page_number
                })

                if start + chunk_size >= len(text):
                    break

    return chunks
