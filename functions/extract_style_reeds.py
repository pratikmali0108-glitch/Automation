#REEDS JEWELLERY

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


def parse_po_pdf(pdf_path: str) -> pd.DataFrame:
    """Extracts PO Number, Style Number, and Qty into a structured DataFrame from a PDF path."""
    text = extract_text_from_pdf(pdf_path)

    # 1. Extract PO Number (matches pure numeric POs after 'PO #')
    po_match = re.search(r"PO\s*#\s*(\d+)", text, re.IGNORECASE)
    po_number = po_match.group(1) if po_match else "NOT_FOUND"

    # 2. Pattern to capture line blocks containing quantity lead-in & Vendor Style Number
    # Matches line digit combinations + Each + VendorStyleNumber + style ID
    pattern = r"(\d+(?:\s+\d+)?)\s*Each[^\n]*VendorStyleNumber\s*\n\s*([^\s]+)\s*BuyerStyleNumber"
    matches = re.findall(pattern, text, re.IGNORECASE)

    records = []
    for line_idx, (raw_qty_lead, style_no) in enumerate(matches, start=1):
        parts = raw_qty_lead.strip().split()

        # Handle '1 11 Each' (separate line # and qty) vs '103 Each' (merged line #10 and qty 3)
        if len(parts) == 2:
            qty = int(parts[1])
        else:
            raw_val = parts[0]
            line_str = str(line_idx)
            if raw_val.startswith(line_str) and len(raw_val) > len(line_str):
                qty = int(raw_val[len(line_str) :])
            else:
                qty = int(raw_val)

        records.append(
            {
                "PO Number": po_number,
                "Style Number": style_no.strip(),
                "Qty": qty,
            }
        )

    return pd.DataFrame(records)


# --- Example Usage ---
# Install pypdf if not available: pip install pypdf
pdf_file_path = r"D:\automate\Automation\input_pdfs\Reds476982-MEMO.pdf"  # Replace with your actual file path
df = parse_po_pdf(pdf_file_path)

print(df)