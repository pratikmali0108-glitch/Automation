#Helzberg PO PDF
import re
import pandas as pd
from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text content across all pages in a PDF file."""
    reader = PdfReader(pdf_path)
    text_pages = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_pages.append(page_text)
    return "\n".join(text_pages)


def parse_helzberg_po_pdf(pdf_path: str) -> pd.DataFrame:
    """Extracts PO Number, Style Number, and Qty from a Helzberg/DIcentral PO PDF."""
    raw_text = extract_text_from_pdf(pdf_path)

    # 1. Extract PO Number (handles formats like 'PO No 5010778' or 'PO # 5010778')
    po_match = re.search(r"PO\s*(?:No|#)\s*(\d+)", raw_text, re.IGNORECASE)
    po_number = po_match.group(1) if po_match else "NOT_FOUND"

    # 2. Extract Line Items (Qty and Vendor Style Number)
    # Splitting into line item blocks starting with Qty + Each
    blocks = re.split(r"(?=\n\s*\d+(?:\s+\d+)?\s+Each)", raw_text)

    records = []
    for idx, block in enumerate(blocks[1:], start=1):
        # Match Qty (e.g. ' 92 Each' -> 92, or '1 11 Each' -> 11)
        qty_match = re.search(r"^\s*(\d+(?:\s+\d+)?)\s+Each", block)

        # Match VendorItemNumber (captures the style number line right below)
        style_match = re.search(
            r"VendorItemNumber\s*\n\s*([^\n]+?)\s*(?:BuyerSizeCode|BuyerItemNumber|\n|$)",
            block,
        )

        if qty_match and style_match:
            raw_qty_lead = qty_match.group(1).strip()
            parts = raw_qty_lead.split()

            # Handles spaced line item numbers vs concatenated numbers
            if len(parts) == 2:
                qty = int(parts[1])
            else:
                raw_val = parts[0]
                line_str = str(idx)
                if raw_val.startswith(line_str) and len(raw_val) > len(
                    line_str
                ):
                    qty = int(raw_val[len(line_str) :])
                else:
                    qty = int(raw_val)

            records.append(
                {
                    "PO Number": po_number,
                    "Style Number": style_match.group(1).strip(),
                    "Qty": qty,
                }
            )

    return pd.DataFrame(records)


# --- Example Usage ---
# Ensure pypdf and pandas are installed: pip install pypdf pandas
pdf_file_path = r"D:\automate\Automation\input_pdfs\helzberg 5010778-MEMO.pdf"
df = parse_helzberg_po_pdf(pdf_file_path)

print(df)