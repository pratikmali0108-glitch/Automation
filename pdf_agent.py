import os
import time
import subprocess
import pdfplumber
import win32com.client
import pythoncom
import pyautogui
import pygetwindow as gw
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCHED_FOLDER = os.path.abspath("./input_pdfs")

# Set fail-safe for PyAutoGUI (move mouse to top-left corner to stop manually)
pyautogui.FAILSAFE = False

def extract_pdf_data(pdf_path):
    """Extract words or structured data from the PDF."""
    data_rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        data_rows.append(row)
            else:
                text = page.extract_text()
                if text:
                    for line in text.split("\n"):
                        # Split line into words or tokens
                        data_rows.append(line.split())
    return data_rows

def arrange_windows_side_by_side(pdf_path):
    """Opens PDF and Excel side by side on screen."""
    screen_width, screen_height = pyautogui.size()
    half_width = screen_width // 2

    # 1. Open PDF using default system viewer
    os.startfile(pdf_path)
    time.sleep(2)  # Wait for viewer to open

    # Try to resize/position the PDF window on the LEFT side
    try:
        active_win = gw.getActiveWindow()
        if active_win:
            active_win.moveTo(0, 0)
            active_win.resizeTo(half_width, screen_height)
    except Exception as e:
        print(f"[!] Could not resize PDF window: {e}")

    # 2. Launch Excel and position on the RIGHT side
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = True
    excel.DisplayAlerts = False
    
    workbook = excel.Workbooks.Add()
    sheet = workbook.ActiveSheet

    time.sleep(1)
    
    # Try to position Excel on the RIGHT side
    try:
        excel_wins = [w for w in gw.getWindowsWithTitle('Excel') if w.visible]
        if excel_wins:
            excel_win = excel_wins[0]
            excel_win.moveTo(half_width, 0)
            excel_win.resizeTo(half_width, screen_height)
            excel_win.activate()
    except Exception as e:
        print(f"[!] Could not resize Excel window: {e}")

    return excel, sheet

def type_data_into_excel(sheet, data_rows):
    """Navigates through cells and types out each word live via PyAutoGUI."""
    time.sleep(1)  # Give focus time to adjust

    for row_idx, row in enumerate(data_rows, start=1):
        for col_idx, item in enumerate(row, start=1):
            if item is None:
                continue

            # Select cell in Excel
            cell = sheet.Cells(row_idx, col_idx)
            cell.Select()

            # Convert item to string
            text_to_type = str(item)

            # Simulate literal character-by-character typing
            pyautogui.write(text_to_type, interval=0.03)  # Adjust typing speed here
            pyautogui.press('tab')  # Move focus across columns

        pyautogui.press('enter')  # Move focus down to next row

def process_pdf(pdf_path):
    pythoncom.CoInitialize()
    try:
        data = extract_pdf_data(pdf_path)
        if not data:
            print("[-] No text or table data found in PDF.")
            return

        print("[+] Arranging windows side-by-side...")
        excel, sheet = arrange_windows_side_by_side(pdf_path)

        print("[+] Starting live typing into Excel...")
        type_data_into_excel(sheet, data)
        print("[+] Typing complete!")

    finally:
        pythoncom.CoUninitialize()

class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.lower().endswith(".pdf"):
            return
        
        print(f"\n[+] New PDF Detected: {os.path.basename(event.src_path)}")
        time.sleep(2)  # Wait for file write to finalize
        
        try:
            process_pdf(event.src_path)
        except Exception as e:
            print(f"[-] Error processing PDF: {e}")

if __name__ == "__main__":
    if not os.path.exists(WATCHED_FOLDER):
        os.makedirs(WATCHED_FOLDER)

    event_handler = PDFHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCHED_FOLDER, recursive=False)
    observer.start()
    
    print(f"==================================================")
    print(f"[*] Agent listening for PDFs in: {WATCHED_FOLDER}")
    print(f"[*] Move mouse to top-left corner to trigger FAILSAFE")
    print(f"==================================================")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[*] Agent stopped.")
    observer.join()