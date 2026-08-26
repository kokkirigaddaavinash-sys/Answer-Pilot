from pypdf import PdfReader


def extract_text_from_pdf(file_path):
    """
    Extract all readable text from a PDF file.
    """

    reader = PdfReader(file_path)

    text_parts = []

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text_parts.append(page_text.strip())

    return "\n\n".join(text_parts).strip()