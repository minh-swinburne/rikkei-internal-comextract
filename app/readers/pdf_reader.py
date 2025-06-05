import pymupdf  # PyMuPDF

class PDFPasswordError(Exception):
    pass

def read_pdf_pages(input_path: str, password: str = None, start_page: int = 0, end_page: int = -1) -> dict[int, str]:
    """
    Reads a PDF file and returns a dict mapping page numbers to extracted text.
    Supports password-protected PDFs.
    Args:
        input_path: Path to the PDF file.
        password: Password for the PDF (if protected).
        start_page: First page to read (0-based).
        end_page: Last page to read (inclusive, -1 for last page).
    Returns:
        dict[int, str]: {page_number: text}
    Raises:
        PDFPasswordError: If the PDF is password-protected and no/invalid password is provided.
    """
    doc = pymupdf.open(input_path)
    if doc.needs_pass:
        if not password:
            raise PDFPasswordError("PDF is password-protected. Please provide a password.")
        if not doc.authenticate(password):
            raise PDFPasswordError("Incorrect password for PDF.")
    num_pages = doc.page_count
    if end_page == -1 or end_page >= num_pages:
        end_page = num_pages - 1
    if start_page < 0 or start_page >= num_pages or end_page < start_page:
        raise ValueError(f"Invalid page range: {start_page} to {end_page} (PDF has {num_pages} pages)")
    result = {}
    for i in range(start_page, end_page + 1):
        page = doc.load_page(i)
        result[i] = page.get_text()
    return result
