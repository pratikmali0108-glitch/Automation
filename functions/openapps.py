import time
import pyautogui
import psutil
import pygetwindow as gw

# Set delay for smooth execution
pyautogui.PAUSE = 0.5

# Define your target app name and executable process name
TARGET_APP_NAME = "SJE PLUS"            # Name typed in Windows Search Bar
TARGET_PROCESS_NAME = "SJE PLUS.exe"     # Executable process name to check background tasks

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
    """Brings an already running application window to the foreground."""
    windows = gw.getWindowsWithTitle(app_keyword)
    if windows:
        window = windows[0]
        if window.isMinimized:
            window.restore()
        window.activate()
        return True
    return False

def open_via_search(app_name):
    """Clicks the Windows search bar with real-time mouse action and opens the app."""
    screen_width, screen_height = pyautogui.size()

    # Calculate Search Bar position (Windows 11 center-left area of taskbar)
    search_x = int(screen_width * 0.41)
    search_y = screen_height - 35

    print(f"App not running. Moving mouse to Windows Search at ({search_x}, {search_y})...")
    pyautogui.moveTo(search_x, search_y, duration=0.8)
    pyautogui.click()
    time.sleep(1)

    print(f"Typing '{app_name}' into search...")
    pyautogui.write(app_name, interval=0.1)  # Real-time typing
    pyautogui.press("enter")
    print(f"Launched {app_name} via Windows Search.")

def main():
    print(f"Checking if '{TARGET_PROCESS_NAME}' is currently running in background...")
    
    if is_app_running(TARGET_PROCESS_NAME):
        print(f"'{TARGET_APP_NAME}' is ALREADY running!")
        # Attempt to bring window to focus
        if not activate_app_window(TARGET_APP_NAME):
            print("Process active in background. Pressing Alt+Tab or activating window...")
    else:
        open_via_search(TARGET_APP_NAME)

if __name__ == "__main__":
    main()