import re
import time
from pathlib import Path
import pyautogui
import pygetwindow as gw
from pypdf import PdfReader

# Global pause setting for UI actions
pyautogui.PAUSE = 0.5


def extract_pdf_data(pdf_path):
    print(f"Reading text from PDF: {pdf_path}")
    style_codes = []

    try:
        reader = PdfReader(pdf_path)
        if not reader.pages:
            return []

        full_text = ""
        for page in reader.pages:
            full_text += (page.extract_text() or "") + "\n"

        # Extract Style Numbers using line item regex pattern
        lines = full_text.split("\n")
        for line in lines:
            match = re.search(
                r"\d+\s+\d+\s+Each\s*\$?[\d,]+\.\d{2}(?:Quoted)?\d+\s+\d+([A-Z0-9-]+)",
                line,
                re.IGNORECASE,
            )
            if match:
                style = match.group(1).strip()
                style_codes.append(style)

        # Deduplicate while preserving order
        style_codes = list(dict.fromkeys(style_codes))
        print(f"Extracted Style Code(s): {style_codes}")
        return style_codes

    except Exception as e:
        print(f"Error reading PDF: {e}")
        return []


def get_test_pdf_path():
    """Locates the first available PDF in the 'customers' directory structure."""
    base_dir = Path(__file__).parent / "customers"
    if base_dir.exists():
        for customer_folder in base_dir.iterdir():
            if customer_folder.is_dir():
                new_folder = customer_folder / "new"
                pdf_files = (
                    list(new_folder.glob("*.pdf")) if new_folder.exists() else []
                )
                if pdf_files:
                    return pdf_files[0]
    return None


def test_type_styles_only(style_codes):
    """Activates the modal, clicks inside the Style Code box, clears it, and types the styles."""
    if not style_codes:
        print("No style codes to type. Exiting test.")
        return

    screen_width, screen_height = pyautogui.size()

    # 1. Bring active modal popup window to focus
    try:
        active_wins = gw.getAllWindows()
        for w in active_wins:
            if w.visible and w.width < 700 and w.height < 700:
                w.activate()
                time.sleep(0.3)
                break
    except Exception as e:
        print(f"Window activation notice: {e}")

    # 2. Click directly inside the white Style Code text box (~49.5% X, ~48.0% Y)
    text_box_x = int(screen_width * 0.495)
    text_box_y = int(screen_height * 0.480)

    print(
        f"Clicking inside Style Code text box at ({text_box_x}, {text_box_y})..."
    )
    pyautogui.moveTo(
        text_box_x, text_box_y, duration=0.5, tween=pyautogui.easeInOutQuad
    )
    pyautogui.click()
    time.sleep(0.3)

    # 3. Clear existing text
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")
    time.sleep(0.2)

    # 4. Type extracted styles directly
    styles_text = "\n".join(style_codes)
    print(f"Typing style code(s):\n{styles_text}")
    pyautogui.write(styles_text, interval=0.08)
    time.sleep(0.5)

    # 5. Hover over 'Ok' button (~50.5% X, ~60.0% Y) and click
    ok_btn_x = int(screen_width * 0.505)
    ok_btn_y = int(screen_height * 0.60)

    print(f"Hovering to 'Ok' button at ({ok_btn_x}, {ok_btn_y})...")
    pyautogui.moveTo(
        ok_btn_x, ok_btn_y, duration=0.6, tween=pyautogui.easeInOutQuad
    )
    time.sleep(0.3)

    print("Clicking 'Ok' button...")
    pyautogui.click()

    # 6. Hover over 'Ok' button (~50.5% X, ~60.0% Y) and click
    ok_btn_x_2 = 404
    ok_btn_y_2 = 1087

    print(f"Hovering to 'Ok' button at ({ok_btn_x_2}, {ok_btn_y_2})...")
    pyautogui.moveTo(ok_btn_x_2, ok_btn_y_2, duration=0.6, tween=pyautogui.easeInOutQuad)
    time.sleep(0.3)

    print("Clicking 'Ok' button...")
    pyautogui.click()
    time.sleep(1.0)
def bestfit():
    b1 = 599
    b2 = 282
    pyautogui.moveTo(b1, b2, duration=0.6, tween=pyautogui.easeInOutQuad)
    pyautogui.click(button="right")
    time.sleep(0.3)
    
    b3 = 666
    b4 = 468
    pyautogui.moveTo(b3, b4, duration=0.6, tween=pyautogui.easeInOutQuad)
    pyautogui.click()
    time.sleep(1.0)

def clickorder_items():
    ok_btn_x_3 = 105
    ok_btn_y_3 = 224

    pyautogui.moveTo(ok_btn_x_3, ok_btn_y_3, duration=0.6, tween=pyautogui.easeInOutQuad)
    time.sleep(0.3)

    print("Clicking 'document' button...")
    pyautogui.click()


    time.sleep(1.0)
def main():
    # pdf_path = get_test_pdf_path()
    pdf_path = r"C:\Users\Pratik.SJFS\Downloads\M147366.pdf"
    
    if not pdf_path:
        print("Could not find a test PDF in 'customers/*/new/'. Exiting...")
        return

    print(f"Using PDF: {pdf_path}")
    style_codes = extract_pdf_data(pdf_path)

    if style_codes:
        print("\nStarting typing test in 3 seconds. Focus your target window...")
        time.sleep(3)
        test_type_styles_only(style_codes)
        print("\nTest completed!")
    else:
        print("No style codes were extracted from the PDF.")
        clickorder_items()
    bestfit()
    clickorder_items()


if __name__ == "__main__":
    main()