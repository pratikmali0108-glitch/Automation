import pyautogui
import time
import random

# Fail-safe: Move mouse to top-left corner to abort script
pyautogui.FAILSAFE = True

def human_type(text, min_delay=0.06, max_delay=0.15):
    """Types text character by character with slight random variations."""
    for char in text:
        pyautogui.write(char)
        time.sleep(random.uniform(min_delay, max_delay))

def human_move_to(x, y, duration=1.2):
    """Moves mouse smoothly using an ease-out curve."""
    pyautogui.moveTo(
        x, y, 
        duration=duration, 
        tween=pyautogui.easeOutQuad
    )

def main():
    screen_width, screen_height = pyautogui.size()

    print("Starting in 3 seconds... Switch to desktop if desired.")
    time.sleep(3)

    # -------------------------------------------------------------
    # Step 1: Move Mouse to Windows Search Bar & Search Excel
    # -------------------------------------------------------------
    # Center-left target for Windows 11 centered search bar
    search_x = int(screen_width * 0.42)
    search_y = screen_height - 18

    print("Hovering mouse to Windows Search Bar...")
    human_move_to(search_x, search_y, duration=1.2)
    
    # Open search via Windows shortcut & click for visual accuracy
    pyautogui.hotkey('win', 's')
    time.sleep(0.6)

    print("Typing 'excel'...")
    human_type("excel")
    time.sleep(1.0)

    # Press Enter to open Excel
    pyautogui.press('enter')
    print("Waiting for Excel to launch...")
    time.sleep(5)  # Wait for Excel process to initialize

    # -------------------------------------------------------------
    # Step 2: Open a Blank Workbook
    # -------------------------------------------------------------
    # Trigger Blank Workbook directly via keyboard
    pyautogui.press('enter')
    time.sleep(2.5)

    # -------------------------------------------------------------
    # Step 3: Type Headers
    # -------------------------------------------------------------
    headers = ["Name", "Address", "Number", "City"]

    print("Typing headers...")
    for index, header in enumerate(headers):
        human_type(header)
        if index < len(headers) - 1:
            pyautogui.press('tab')
            time.sleep(0.3)

    # -------------------------------------------------------------
    # Step 4: Highlight and Bold Headers
    # -------------------------------------------------------------
    print("Formatting headers in Bold...")
    time.sleep(0.5)
    
    # Select written header cells (Shift + Left Arrow x 3)
    for _ in range(3):
        pyautogui.hotkey('shift', 'left')
        time.sleep(0.2)
        
    # Apply Ctrl + B
    pyautogui.hotkey('ctrl', 'b')
    
    # Return cursor to cell A1
    time.sleep(0.3)
    pyautogui.press('home')

    print("Task completed successfully!")

if __name__ == "__main__":
    main()