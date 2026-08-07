import re
import pandas as pd
from pypdf import PdfReader

# Path to the PDF file
pdf_path = r"D:\automate\Automation\input_pdfs\sterling M145901.pdf"

# Extract text from PDF
reader = PdfReader(pdf_path)
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

# Extract style number and ordered quantity from line items
lines = text.split('\n')
extracted_data = []

for line in lines:
    # Look for line items with format: LN QTY Each $PRICE ... STYLE
    # Example: "1 38 Each$472.92Quoted0 941028502ZR10567H-WGGD"
    # Capture both the quantity (38) and style (ZR10567H-WGGD)
    match = re.search(r'^(\d+)\s+(\d+)\s+Each\s*\$?[\d,]+\.\d{2}(?:Quoted)?\d+\s+\d+([A-Z0-9-]+)', line, re.IGNORECASE)
    
    if match:
        ln_num = match.group(1)
        ordered_qty = match.group(2)
        style = match.group(3)
        
        extracted_data.append({
            'Style Number': style,
            'Ordered Qty': ordered_qty
        })

# Create and display DataFrame
if extracted_data:
    df = pd.DataFrame(extracted_data)
    
    print("=" * 60)
    print("EXTRACTED STYLE NUMBERS WITH ORDERED QUANTITIES")
    print("=" * 60)
    print()
    print(df.to_string(index=False))
    print()
    print("=" * 60)
    print(f"Total items extracted: {len(df)}")
    print("=" * 60)
    
else:
    print("=" * 60)
    print("No data found.")
    print("=" * 60)
    print("\nDebug - searching for line item patterns:")
    for line in lines:
        if 'Each' in line and '$' in line:
            print(f"  > {line[:120]}")
    print("=" * 60)
