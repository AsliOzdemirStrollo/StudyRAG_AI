from pypdf import PdfReader


def extract_pages_from_pdf(file):
    reader = PdfReader(file)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()

        if page_text:
            pages.append(
                {
                    "page": page_number,
                    "text": page_text
                }
            )

    return pages


def split_text_into_chunks(pages, chunk_size=1200, overlap=250):
    chunk_data = []

    for page in pages:
        text = page["text"]
        page_number = page["page"]
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]

            chunk_data.append(
                {
                    "text": chunk_text,
                    "page": page_number
                }
            )

            start += chunk_size - overlap

    return chunk_data