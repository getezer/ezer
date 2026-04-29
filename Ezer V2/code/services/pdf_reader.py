import pdfplumber

# This function reads PDF and returns text with page numbers
def extract_text_with_pages(file):
    pages = []

    with pdfplumber.open(file) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""

            pages.append({
                "page": i + 1,
                "text": text
            })

    return pages