import os
import re
import time
from pathlib import Path
import pyautogui
import psutil
import pygetwindow as gw
from pdf2image import convert_from_path
import pytesseract

# Configure Tesseract OCR path (update this path after installing Tesseract)
# Common installation paths:
# Windows 64-bit: r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Windows 32-bit: r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Set Tesseract command path if file exists
try:
    if os.path.exists(TESSERACT_CMD):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
        print(f"Tesseract configured: {TESSERACT_CMD}")
    else:
        print(f"WARNING: Tesseract not found at {TESSERACT_CMD}")
        print("Please install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki")
except Exception as e:
    print(f"Error configuring Tesseract: {e}")

# Global pause setting for UI actions
pyautogui.PAUSE = 0.5

# Configuration Constants
TARGET_APP_NAME = "SJE PLUS"             # Application title / search name
TARGET_PROCESS_NAME = "SJE PLUS.exe"     # Task manager process name
SEARCH_TEXT = "Jasani Order"             # Menu item to search

def extract_po_number_from_pdf(pdf_path):
    """
    Converts a scanned PDF page into an image and uses Tesseract OCR
    to extract the 'PO #' value using regular expressions.
    """
    print(f"Reading scanned PDF with OCR: {pdf_path}")
    try:
        # Check if Tesseract is configured
        try:
            tesseract_cmd = pytesseract.pytesseract.tesseract_cmd
            if not os.path.exists(tesseract_cmd):
                print(f"ERROR: Tesseract not found at: {tesseract_cmd}")
                print("Please install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki")
                return None
        except AttributeError:
            print("ERROR: Tesseract command path not configured")
            return None
        
        # Convert first page of PDF to image
        print("Converting PDF to image...")
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        if not images:
            print("ERROR: Failed to convert PDF to image (no images returned)")
            return None
        
        print(f"Successfully converted PDF to image. Performing OCR...")
        
        # Perform OCR on the image
        text = pytesseract.image_to_string(images[0])
        
        print(f"OCR completed. Extracted {len(text)} characters of text.")
        print("--- OCR Text Preview (first 500 chars) ---")
        print(text[:500] if text else "(empty)")
        print("--- End Preview ---")
        
        # Regex to capture patterns like 'PO # M145901' or 'PO# M145901'
        match = re.search(r'PO\s*#?\s*([A-Z0-9]+)', text, re.IGNORECASE)
        if match:
            po_number = match.group(1).strip()
            print(f"SUCCESS: Extracted PO #: {po_number}")
            return po_number
        else:
            print("WARNING: PO # pattern not found in OCR text")
            # Try to find any pattern with M followed by digits (common format)
            alt_match = re.search(r'M\d+', text)
            if alt_match:
                print(f"Found alternative pattern: {alt_match.group()}")
            return None
    except Exception as e:
        print(f"ERROR reading PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_valid_customer_data():
    """
    Scans the 'customers' folder.
    For each customer subfolder:
      1. Checks if the 'new' folder contains a .pdf file.
      2. If YES, extracts the PO # from the PDF using OCR.
      3. Gets the .txt file directly inside the customer folder for the Client Name.
    Returns: (client_name, po_number)
    """
    base_dir = Path(__file__).parent / "customers"

    if not base_dir.exists():
        print(f"Warning: Folder '{base_dir}' does not exist.")
        return None, None

    for customer_folder in base_dir.iterdir():
        if customer_folder.is_dir():
            new_folder = customer_folder / "new"

            # Look for a PDF file inside 'new'
            pdf_files = list(new_folder.glob("*.pdf")) if new_folder.exists() else []

            if pdf_files:
                target_pdf = pdf_files[0]
                print(f"Found PDF: {target_pdf.name} in 'new' for customer: {customer_folder.name}")
                
                # Fetch text file name from customer root
                txt_files = [f for f in customer_folder.glob("*.txt") if f.parent == customer_folder]
                if txt_files:
                    client_name = txt_files[0].stem
                    po_number = extract_po_number_from_pdf(target_pdf)
                    return client_name, po_number
                else:
                    print(f"No .txt file found in customer root: {customer_folder.name}")
            else:
                print(f"Skipping {customer_folder.name}: No PDF found in 'new' folder.")

    return None, None

def is_app_running(process_name):
    """Checks background processes to see if the app is already open."""
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def activate_app_window(app_keyword):
    """Brings the application window to focus and maximizes it."""
    windows = gw.getWindowsWithTitle(app_keyword)
    if windows:
        window = windows[0]
        if window.isMinimized:
            window.restore()
        window.activate()
        if not window.isMaximized:
            window.maximize()
        time.sleep(1)
        return True
    return False

def open_via_search(app_name):
    """Opens the app via the Windows taskbar search bar."""
    screen_width, screen_height = pyautogui.size()

    search_x = int(screen_width * 0.41)
    search_y = screen_height - 35

    print(f"Moving to Windows Search at ({search_x}, {search_y})...")
    pyautogui.moveTo(search_x, search_y, duration=0.8, tween=pyautogui.easeInOutQuad)
    pyautogui.click()
    time.sleep(1)

    print(f"Typing '{app_name}'...")
    pyautogui.write(app_name, interval=0.1)
    pyautogui.press("enter")
    
    print("Waiting for application to load...")
    time.sleep(5)

def search_menu_item(menu_query):
    """Types query into the top search menu, moves down, and selects it."""
    screen_width, screen_height = pyautogui.size()

    menu_search_x = int(screen_width * 0.51)
    menu_search_y = 28

    print(f"Moving mouse to menu search bar at ({menu_search_x}, {menu_search_y})...")
    pyautogui.moveTo(menu_search_x, menu_search_y, duration=0.8, tween=pyautogui.easeInOutQuad)
    pyautogui.click()
    time.sleep(0.3)

    print(f"Typing '{menu_query}'...")
    pyautogui.typewrite(menu_query, interval=0.08)
    time.sleep(0.3)

    print("Selecting item...")
    pyautogui.press('down')
    time.sleep(0.2)
    pyautogui.press('enter')
    time.sleep(2)

def click_new_transaction():
    """Smoothly moves to 'New Transaction' on the left sidebar and clicks it."""
    screen_width, screen_height = pyautogui.size()

    new_trans_x = int(screen_width * 0.023)
    new_trans_y = int(screen_height * 0.146)

    print(f"Hovering to 'New Transaction' at ({new_trans_x}, {new_trans_y})...")
    pyautogui.moveTo(new_trans_x, new_trans_y, duration=0.8, tween=pyautogui.easeInOutQuad)
    time.sleep(0.2)
    
    print("Clicking 'New Transaction'...")
    pyautogui.click()
    time.sleep(1.5)

def enter_client_name(client_name):
    """Types client name into the Client field, selects from dropdown."""
    screen_width, screen_height = pyautogui.size()

    # Relative coordinates for 'Client' box (~23.5% X, ~18.2% Y)
    client_field_x = int(screen_width * 0.235)
    client_field_y = int(screen_height * 0.182)

    print(f"Hovering to 'Client' input field at ({client_field_x}, {client_field_y})...")
    pyautogui.moveTo(client_field_x, client_field_y, duration=0.8, tween=pyautogui.easeInOutQuad)
    pyautogui.click()
    time.sleep(0.3)

    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    time.sleep(0.2)

    print(f"Typing Client Name: '{client_name}'...")
    pyautogui.typewrite(client_name, interval=0.08)
    time.sleep(0.4)

    pyautogui.press('down')
    time.sleep(0.2)
    pyautogui.press('enter')
    time.sleep(0.5)

def enter_po_number_and_remarks(po_no, remarks_text="Added using AI"):
    """
    Enters PO Number into the 'Po No' input box and types remarks into the 'Remarks' text area.
    """
    screen_width, screen_height = pyautogui.size()

    # 1. Fill PO No Field (~31.2% X, ~15.8% Y)
    if po_no:
        po_x = int(screen_width * 0.312)
        po_y = int(screen_height * 0.158)

        print(f"Hovering to 'Po No' input box at ({po_x}, {po_y})...")
        pyautogui.moveTo(po_x, po_y, duration=0.8, tween=pyautogui.easeInOutQuad)
        pyautogui.click()
        time.sleep(0.2)

        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        
        print(f"Typing PO No: '{po_no}'...")
        pyautogui.typewrite(po_no, interval=0.08)
        time.sleep(0.3)

    # 2. Fill Remarks Field (~23.5% X, ~32.5% Y)
    remarks_x = int(screen_width * 0.235)
    remarks_y = int(screen_height * 0.305)

    print(f"Hovering to 'Remarks' area at ({remarks_x}, {remarks_y})...")
    pyautogui.moveTo(remarks_x, remarks_y, duration=0.8, tween=pyautogui.easeInOutQuad)
    pyautogui.click()
    time.sleep(0.2)

    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')

    print(f"Typing Remarks: '{remarks_text}'...")
    pyautogui.typewrite(remarks_text, interval=0.08)
    time.sleep(0.3)

def main():
    # 1. Find target client and extract PO # from scanned PDF via OCR
    client_name, po_number = get_valid_customer_data()

    if not client_name:
        print("No valid customer with pending PDF found. Exiting...")
        return

    print(f"\nExtracted Client: '{client_name}' | PO #: '{po_number}'")

    # 2. Open or Focus SJE PLUS application
    if is_app_running(TARGET_PROCESS_NAME):
        print(f"'{TARGET_APP_NAME}' is running. Activating window...")
        activate_app_window(TARGET_APP_NAME)
    else:
        open_via_search(TARGET_APP_NAME)
        activate_app_window(TARGET_APP_NAME)

    # 3. Navigate through UI menus
    search_menu_item(SEARCH_TEXT)
    click_new_transaction()

    # 4. Fill in order details
    enter_client_name(client_name)
    enter_po_number_and_remarks(po_number, "Added using AI")

    print("\nWorkflow completed successfully!")

if __name__ == "__main__":
    main()