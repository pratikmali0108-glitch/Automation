#zales
import re
import pandas as pd
from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts raw text content across all pages in a PDF file."""
    reader = PdfReader(pdf_path)
    full_text = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            full_text.append(page_text)

    return "\n".join(full_text)


def parse_zales_po_pdf(pdf_path: str) -> pd.DataFrame:
    """Extracts PO Number, Style Number, and Qty from a Zales PO PDF."""
    raw_text = extract_text_from_pdf(pdf_path)

    # 1. Extract Purchase Order Number
    po_match = re.search(r"PURCHASE ORDER NUMBER\s*\n\s*(\d+)", raw_text)
    po_number = po_match.group(1) if po_match else "NOT_FOUND"

    # 2. Isolate table section between headers and 'Total Qty:'
    start_match = re.search(r"Extension\(\$\)\s+Dept/Class\s+SKU", raw_text)
    end_match = re.search(r"Total Qty:", raw_text)

    if start_match and end_match:
        table_text = raw_text[start_match.end() : end_match.start()]
    else:
        table_text = raw_text

    # 3. Match line items:
    # Captures Style Number (e.g. ABR03465LE-YGGDLGD) and Order Qty before unit cost
    pattern = r"([A-Z0-9]+-[A-Z0-9]+)\s+[\s\S]*?\s+(\d+)\s+[\d,]+\.\d{2}\s+[\d,]+\.\d{2}"
    matches = re.findall(pattern, table_text)

    records = []
    for style_no, qty in matches:
        records.append(
            {
                "PO Number": po_number,
                "Style Number": style_no.strip(),
                "Qty": int(qty),
            }
        )

    return pd.DataFrame(records)


# --- Example Usage ---
# Install dependencies if needed: pip install pypdf pandas
pdf_file_path = r"D:\automate\Automation\input_pdfs\ZALES - ZL4 145836.pdf"# Replace with actual PDF path
df = parse_zales_po_pdf(pdf_file_path)

print(df)