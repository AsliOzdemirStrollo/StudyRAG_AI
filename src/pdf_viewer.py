import fitz
from PIL import Image
import io


def render_pdf_page_as_image(uploaded_file, page_number):
    pdf_bytes = uploaded_file.getvalue()

    pdf_document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    page_index = page_number - 1

    if page_index < 0 or page_index >= len(pdf_document):
        return None

    page = pdf_document.load_page(page_index)

    pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))

    image_bytes = pixmap.tobytes("png")

    image = Image.open(io.BytesIO(image_bytes))

    return image