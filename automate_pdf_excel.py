import os
import sys
import glob
import time
import random
import pyautogui
import pdfplumber
import keyboard

# Enable PyAutoGUI fail-safe (move mouse to top-left corner to abort)
pyautogui.FAILSAFE = True

# ------------------------------------------------------------------
# Kill Switch Trigger
# ------------------------------------------------------------------
def trigger_kill_switch():
    """Immediately stops the script when the Esc key is pressed."""
    print("\n\n[!] EMERGENCY STOP: 'Esc' key pressed. Terminating script immediately!")
    os._exit(0)

# Register Esc hotkey
keyboard.add_hotkey('esc', trigger_kill_switch)

# ------------------------------------------------------------------
# Speed & Cursor Helpers
# ------------------------------------------------------------------
def human_type(text, min_delay=0.01, max_delay=0.03):
    """Types text character by character at 3x human speed."""
    for char in str(text):
        if char == '\n':
            pyautogui.hotkey('alt', 'enter')
        else:
            pyautogui.write(char)
        time.sleep(random.uniform(min_delay, max_delay))

def human_move_to(x, y, duration=0.8):
    """Moves mouse smoothly using an ease-out curve."""
    pyautogui.moveTo(
        x, y, 
        duration=duration, 
        tween=pyautogui.easeOutQuad
    )

# ------------------------------------------------------------------
# PDF Data Extraction
# ------------------------------------------------------------------
def extract_pdf_matrix():
    """Extracts data from any PDF as a raw 2D matrix (list of lists)."""
    pdf_files = glob.glob("*.pdf")
    
    if not pdf_files:
        raise FileNotFoundError("No PDF files found in the current directory.")
    
    pdf_path = pdf_files[0]
    print(f"[*] Reading PDF file: {pdf_path}")
    
    matrix = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        cleaned_row = [cell.replace('\n', ' ').strip() if cell else "" for cell in row]
                        if any(cleaned_row):
                            matrix.append(cleaned_row)
            else:
                text = page.extract_text()
                if text:
                    for line in text.split('\n'):
                        parts = [p.strip() for p in line.split() if p.strip()]
                        if parts:
                            matrix.append(parts)

    if not matrix:
        raise ValueError("No readable data could be extracted from the PDF.")

    print(f"[*] Extracted {len(matrix)} rows of data.")
    return pdf_path, matrix

# ------------------------------------------------------------------
# Main Workflow
# ------------------------------------------------------------------
def main():
    try:
        pdf_path, data_matrix = extract_pdf_matrix()
    except Exception as e:
        print(f"[!] PDF Read Error: {e}")
        return

    screen_width, screen_height = pyautogui.size()

    print("[*] Starting automation in 2 seconds...")
    print("[*] ---> PRESS 'ESC' AT ANY TIME TO KILL THE SCRIPT <---")
    time.sleep(2)

    # -------------------------------------------------------------
    # Step 1: Open PDF and Force Snap to LEFT Half
    # -------------------------------------------------------------
    print("[*] Opening PDF viewer on the LEFT side...")
    os.startfile(pdf_path)
    time.sleep(2.5)

    # Click the top-left area of screen to ensure PDF window receives focus
    pyautogui.click(int(screen_width * 0.25), int(screen_height * 0.1))
    time.sleep(0.3)

    # Snap PDF viewer to LEFT half
    pyautogui.hotkey('win', 'left')
    time.sleep(0.5)
    pyautogui.press('escape')  # Dismiss Windows Snap Assist preview grid
    time.sleep(0.5)

    # -------------------------------------------------------------
    # Step 2: Hover to Search Bar & Launch Excel
    # -------------------------------------------------------------
    search_x = int(screen_width * 0.42)
    search_y = screen_height - 18

    print("[*] Hovering mouse to Windows Search Bar...")
    human_move_to(search_x, search_y, duration=0.8)
    
    pyautogui.hotkey('win', 's')
    time.sleep(0.4)

    print("[*] Searching for Excel...")
    human_type("excel")
    time.sleep(0.5)

    pyautogui.press('enter')
    print("[*] Waiting for Excel to open...")
    time.sleep(4.5)

    # Create Blank Workbook
    pyautogui.press('enter')
    time.sleep(1.5)

    # -------------------------------------------------------------
    # Step 3: Snap Excel to RIGHT Half & Force Focus to Cell A1
    # -------------------------------------------------------------
    print("[*] Snapping Excel to the RIGHT side...")
    pyautogui.hotkey('win', 'right')
    time.sleep(0.5)
    pyautogui.press('escape')  # Dismiss Snap Assist menu
    time.sleep(0.5)

    # Click top ribbon bar on RIGHT half to focus Excel without selecting wrong cells
    excel_ribbon_x = int(screen_width * 0.75)
    excel_ribbon_y = int(screen_height * 0.1)
    pyautogui.click(excel_ribbon_x, excel_ribbon_y)
    time.sleep(0.3)

    # Instantly navigate selection cursor back to Cell A1
    pyautogui.hotkey('ctrl', 'home')
    time.sleep(0.3)

    # -------------------------------------------------------------
    # Step 4: Type PDF Data Live into Excel Starting at Cell A1
    # -------------------------------------------------------------
    print("[*] Live typing PDF data into Excel starting at cell A1...")
    
    header_row = data_matrix[0]
    data_rows = data_matrix[1:]

    # Type Header Row starting at A1
    for col_idx, cell in enumerate(header_row):
        human_type(cell)
        if col_idx < len(header_row) - 1:
            pyautogui.press('tab')
            time.sleep(0.05)

    # Bold Header Row
    if len(header_row) > 1:
        for _ in range(len(header_row) - 1):
            pyautogui.hotkey('shift', 'left')
            time.sleep(0.05)
    pyautogui.hotkey('ctrl', 'b')
    time.sleep(0.2)

    # Move to Row 2, Column A
    pyautogui.press('enter')
    pyautogui.press('home')
    time.sleep(0.15)

    # Type Data Rows
    for row in data_rows:
        for col_idx, cell in enumerate(row):
            human_type(cell)
            if col_idx < len(row) - 1:
                pyautogui.press('tab')
                time.sleep(0.05)
        
        # Move to next row
        pyautogui.press('enter')
        pyautogui.press('home')
        time.sleep(0.1)

    print("\n[✓] Automation completed successfully!")

if __name__ == "__main__":
    main()