import os
import re
import time
from pathlib import Path
import pyautogui
import psutil
import pygetwindow as gw
import pyperclip
from pypdf import PdfReader

# Global pause setting for UI actions
pyautogui.PAUSE = 0.5

# Configuration Constants
TARGET_APP_NAME = "SJE PLUS"             # Application title / search name
TARGET_PROCESS_NAME = "SJE PLUS.exe"     # Task manager process name
SEARCH_TEXT = "Jasani Order"             # Menu item to search

def handle_metal_rate_popup():
    """
    Checks if the 'Jasani Order' / Daily Metal Rate dialog box is present
    and clicks 'No' (or presses 'N') to close it.
    """
    time.sleep(0.3)
    windows = gw.getWindowsWithTitle("Jasani Order")
    
    for win in windows:
        if win.visible and win.width < 600:
            print("Detected 'Daily Metal Rate' dialog. Clicking 'No'...")
            win.activate()
            time.sleep(0.2)
            pyautogui.press('n')
            time.sleep(0.3)
            return True
    return False

def clean_pdf_text(raw_text):
    """
    Cleans raw PDF text to handle text wrapped across line breaks.
    e.g. 'ZR10567H-\nWGGD' or 'ZR10567H\n-WGGD' -> 'ZR10567H-WGGD'
    """
    cleaned = re.sub(r'([A-Z0-9]+)-\s*\n\s*([A-Z0-9]+)', r'\1-\2', raw_text, flags=re.IGNORECASE)
    cleaned = re.sub(r'([A-Z0-9]+)\s*\n\s*-([A-Z0-9]+)', r'\1-\2', cleaned, flags=re.IGNORECASE)
    return cleaned

def extract_pdf_data(pdf_path):
    """
    Reads direct text from PDF, normalizes wrapped line-breaks,
    and extracts PO Number and Vendor Style Codes.
    """
    print(f"Reading direct text from PDF: {pdf_path}")
    po_number = None
    style_codes = []

    try:
        reader = PdfReader(pdf_path)
        if not reader.pages:
            return None, []
            
        raw_text = ""
        for page in reader.pages:
            raw_text += (page.extract_text() or "") + "\n"
        
        full_text = clean_pdf_text(raw_text)

        # 1. Extract PO Number
        po_match = re.search(r'\bPO\s*#\s*([A-Z][0-9]{5,8})\b', full_text)
        if not po_match:
            po_match = re.search(r'\bPO\s*#\s*([\w]+)', full_text)
            
        if po_match:
            po_number = po_match.group(1).strip()
            print(f"Extracted PO #: {po_number}")

        # 2. Extract Vendor Style codes (e.g. ZR10567H-WGGD)
        styles = re.findall(r'\b[A-Z0-9]{4,12}-[A-Z0-9]{3,8}\b', full_text)
        if styles:
            style_codes = list(dict.fromkeys([s.strip() for s in styles]))
            print(f"Extracted Style Code(s): {style_codes}")
        else:
            print("No vendor style codes found matching pattern.")

        return po_number, style_codes

    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None, []

def get_valid_customer_data():
    base_dir = Path(__file__).parent / "customers"

    if not base_dir.exists():
        print(f"Warning: Folder '{base_dir}' does not exist.")
        return None, None, []

    for customer_folder in base_dir.iterdir():
        if customer_folder.is_dir():
            new_folder = customer_folder / "new"
            pdf_files = list(new_folder.glob("*.pdf")) if new_folder.exists() else []

            if pdf_files:
                target_pdf = pdf_files[0]
                print(f"Found PDF: {target_pdf.name} in 'new' for customer: {customer_folder.name}")
                
                txt_files = [f for f in customer_folder.glob("*.txt") if f.parent == customer_folder]
                if txt_files:
                    client_name = txt_files[0].stem
                    po_number, style_codes = extract_pdf_data(target_pdf)
                    return client_name, po_number, style_codes
                else:
                    print(f"No .txt file found in customer root: {customer_folder.name}")
            else:
                print(f"Skipping {customer_folder.name}: No PDF found in 'new' folder.")

    return None, None, []

def is_app_running(process_name):
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def activate_app_window(app_keyword):
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
    
    handle_metal_rate_popup()

def click_new_transaction():
    screen_width, screen_height = pyautogui.size()
    new_trans_x = int(screen_width * 0.023)
    new_trans_y = int(screen_height * 0.146)

    print(f"Hovering to 'New Transaction' at ({new_trans_x}, {new_trans_y})...")
    pyautogui.moveTo(new_trans_x, new_trans_y, duration=0.8, tween=pyautogui.easeInOutQuad)
    time.sleep(0.2)
    
    print("Clicking 'New Transaction'...")
    pyautogui.click()
    time.sleep(1.5)
    
    handle_metal_rate_popup()

def enter_client_name(client_name):
    screen_width, screen_height = pyautogui.size()

    client_field_x = int(screen_width * 0.235)
    client_field_y = int(screen_height * 0.182)

    print(f"Hovering to 'Client' input field at ({client_field_x}, {client_field_y})...")
    pyautogui.moveTo(client_field_x, client_field_y, duration=0.8, tween=pyautogui.easeInOutQuad)
    pyautogui.click()
    time.sleep(0.5)

    handle_metal_rate_popup()

    pyautogui.click(client_field_x, client_field_y)
    time.sleep(0.2)

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

    handle_metal_rate_popup()

def enter_po_number_and_remarks(po_no, remarks_text="Added using AI"):
    screen_width, screen_height = pyautogui.size()

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

def click_order_items():
    screen_width, screen_height = pyautogui.size()

    order_items_x = int(screen_width * 0.023)
    order_items_y = int(screen_height * 0.148)

    print(f"Hovering to 'Order Items' at ({order_items_x}, {order_items_y})...")
    pyautogui.moveTo(order_items_x, order_items_y, duration=0.8, tween=pyautogui.easeInOutQuad)
    time.sleep(0.2)

    print("Clicking 'Order Items'...")
    pyautogui.click()
    time.sleep(1.0)

    handle_metal_rate_popup()

def process_order_items_section(client_name):
    screen_width, screen_height = pyautogui.size()

    blue_arrow_x = int(screen_width * 0.984)
    blue_arrow_y = int(screen_height * 0.087)

    print(f"Clicking top-right blue arrow button at ({blue_arrow_x}, {blue_arrow_y})...")
    pyautogui.moveTo(blue_arrow_x, blue_arrow_y, duration=0.6, tween=pyautogui.easeInOutQuad)
    pyautogui.click()
    time.sleep(0.5)

    checkbox_x = int(screen_width * 0.113)
    checkbox_y = int(screen_height * 0.158)

    print(f"Clicking checkbox left of 'Client Style' at ({checkbox_x}, {checkbox_y})...")
    pyautogui.moveTo(checkbox_x, checkbox_y, duration=0.6, tween=pyautogui.easeInOutQuad)
    pyautogui.click()
    time.sleep(0.3)

    input_field_x = int(screen_width * 0.185)
    input_field_y = int(screen_height * 0.158)

    print(f"Clicking 'Client Style' input field at ({input_field_x}, {input_field_y})...")
    pyautogui.moveTo(input_field_x, input_field_y, duration=0.6, tween=pyautogui.easeInOutQuad)
    pyautogui.click()
    time.sleep(0.3)

    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    time.sleep(0.2)

    print(f"Typing Client Name in Client Style field: '{client_name}'...")
    pyautogui.typewrite(client_name, interval=0.08)
    time.sleep(0.4)

    pyautogui.press('down')
    time.sleep(0.2)
    pyautogui.press('enter')
    time.sleep(0.5)

    handle_metal_rate_popup()

def open_item_checklist_and_paste_styles(style_codes):
    """
    1. Clicks the orange checklist icon.
    2. Clicks the three dots '...' button to open the Style Code modal.
    3. Clicks directly inside the Style Code text box to gain focus.
    4. Pastes the style code(s) via clipboard and fallback typing if needed.
    5. Hovers over the 'Ok' button and clicks it.
    """
    screen_width, screen_height = pyautogui.size()

    # 1. Click Item Checklist icon (~14.1% X, ~21.8% Y)
    checklist_btn_x = int(screen_width * 0.141)
    checklist_btn_y = int(screen_height * 0.218)

    print(f"Clicking Item Checklist icon at ({checklist_btn_x}, {checklist_btn_y})...")
    pyautogui.moveTo(checklist_btn_x, checklist_btn_y, duration=0.6, tween=pyautogui.easeInOutQuad)
    pyautogui.click()
    time.sleep(1.5)

    handle_metal_rate_popup()

    # 2. Click three dots '...' button (~9.8% X, ~13.8% Y)
    three_dots_x = int(screen_width * 0.098)
    three_dots_y = int(screen_height * 0.138)

    print(f"Clicking three dots '...' button at ({three_dots_x}, {three_dots_y})...")
    pyautogui.moveTo(three_dots_x, three_dots_y, duration=0.6, tween=pyautogui.easeInOutQuad)
    pyautogui.click()
    time.sleep(1.2)

    # 3. Explicitly click inside the Style Code text box (~48.0% X, ~45.0% Y) to focus cursor
    modal_text_x = int(screen_width * 0.480)
    modal_text_y = int(screen_height * 0.450)

    print(f"Clicking inside Style Code text box at ({modal_text_x}, {modal_text_y})...")
    pyautogui.moveTo(modal_text_x, modal_text_y, duration=0.5, tween=pyautogui.easeInOutQuad)
    pyautogui.click()
    time.sleep(0.3)

    if style_codes:
        styles_text = "\n".join(style_codes)
        print(f"Entering Style Code(s):\n{styles_text}")

        # Primary method: Copy & Paste
        pyperclip.copy(styles_text)
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.4)

        # Fallback safeguard: If clipboard paste yields empty text, type directly
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        pyautogui.typewrite(styles_text, interval=0.05)
        time.sleep(0.4)

    # 4. Hover over 'Ok' button inside the Style Code box (~50.5% X, ~58.2% Y) and click
    ok_btn_x = int(screen_width * 0.505)
    ok_btn_y = int(screen_height * 0.582)

    print(f"Hovering to 'Ok' button in Style Code box at ({ok_btn_x}, {ok_btn_y})...")
    pyautogui.moveTo(ok_btn_x, ok_btn_y, duration=0.6, tween=pyautogui.easeInOutQuad)
    time.sleep(0.3)

    print("Clicking 'Ok' button...")
    pyautogui.click()
    time.sleep(1.0)

    handle_metal_rate_popup()

def main():
    client_name, po_number, style_codes = get_valid_customer_data()

    if not client_name:
        print("No valid customer with pending PDF found. Exiting...")
        return

    print(f"\nExtracted Client: '{client_name}' | PO #: '{po_number}' | Styles: {style_codes}")

    if is_app_running(TARGET_PROCESS_NAME):
        print(f"'{TARGET_APP_NAME}' is running. Activating window...")
        activate_app_window(TARGET_APP_NAME)
    else:
        open_via_search(TARGET_APP_NAME)
        activate_app_window(TARGET_APP_NAME)

    search_menu_item(SEARCH_TEXT)
    click_new_transaction()
    enter_client_name(client_name)
    enter_po_number_and_remarks(po_number, "Added using AI")
    
    click_order_items()
    process_order_items_section(client_name)
    open_item_checklist_and_paste_styles(style_codes)

    print("\nWorkflow completed successfully!")

if __name__ == "__main__":
    main()