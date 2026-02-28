import time
import psutil
import win32gui
import win32process
import pprint
import os

session_start = None
current_app = None
total_info = {}


def get_active_window():
    window = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(window)
    _, pid = win32process.GetWindowThreadProcessId(window)
    proc_name = psutil.Process(pid).name()
    return title, proc_name,

while(True):
    title, proc = get_active_window()
    
    if proc != current_app:
        current_time = time.time()

        if current_app is not None:
            session_end = current_time
            duration = session_end - session_start
            if current_app not in total_info:
                total_info[current_app] = 0
            total_info[current_app] += duration
            
            print("\n")
        
        current_app = proc
        current_title = title
        session_start = current_time

    display_info=total_info.copy()
    live_duration = time.time() - session_start
    if current_app in display_info:
        display_info[current_app] += live_duration
    else:
        display_info[current_app] = live_duration

    os.system("cls")
    pprint.pprint(display_info)
    time.sleep(1)