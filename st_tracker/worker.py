from PySide6.QtCore import QObject, Signal
import time, psutil, win32gui, win32process, win32api
from shared.memory import stats_data, stats_lock
from backend.database import get_today_data, add_today_usage, bulk_save_usage
from datetime import date
from shared.status import *

class TrackerWorker(QObject):
  update = Signal(dict)
  finished = Signal()

  def __init__(self, initial_threshold):
    super().__init__()
    self.idle_threshold = initial_threshold

    self.running = True
    self.reset_flag = False
    self.paused = False
    self.was_idle = False

    
    self.last_sync_time = time.time()
    self.loop_count = 0
    self.current_day = date.today()

    self.current_app = None
    self.session_start = None
    self.total_info = {}
    self.pid_cache = {}

    self.total_info = get_today_data()

    print("[DB LOADED]", self.total_info)

  def get_active_window(self):
    hwnd = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(hwnd)
    try:
      _, pid = win32process.GetWindowThreadProcessId(hwnd)
      if pid in self.pid_cache:
         proc_name = self.pid_cache[pid] #calling the cache instead of calling psutil every single time
      else:
         proc_name = psutil.Process(pid).name()
         self.pid_cache[pid] = proc_name
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
       proc_name = "Unknown"

    return hwnd, title, proc_name
  
  def normalize_win32_name(self, proc):
      name = proc.replace(".exe", "")
      return name.capitalize()
  
  def pause(self):
      if not self.paused:
        self.paused = True
        self.paused_time = time.time()

  def resume(self):
      if self.paused:
        paused_duration = time.time() - self.paused_time
        
        # shifting the session start forward so paused time is not counted
        if self.session_start is not None:
            self.session_start += paused_duration
        
        self.paused = False
        self.paused_time = None

  def reset(self):
      self.reset_flag = True

  def perform_sync(self, now):
      """Prepares a batch and sends it to the DB in one shot."""
      sync_batch = []
      for app, total in self.total_info.items():
          val = total
          # Add live progress for the active app so the DB is 100% current
          if app == self.current_app and self.session_start:
              val += (now - self.session_start)
          sync_batch.append((app, val))
      
      if sync_batch:
          # We are going to write this 'bulk_save_usage' in database.py next
          bulk_save_usage(sync_batch)
  
  def get_idle_time(self):
     last_input_time = win32api.GetLastInputInfo()
     current_tick = win32api.GetTickCount()
     idle_seconds = (current_tick - last_input_time) / 1000.0
     return idle_seconds

  def run(self):
    try:
      while self.running:

        self.loop_count += 1
        #clearing the cache
        if self.loop_count > 1000:
          self.pid_cache.clear()
          self.loop_count = 0
        
        #on pause, skips everything below
        if self.paused:
          time.sleep(1)
          continue

        now = time.time()
        if now - self.last_sync_time > 30:
            # We call a helper method to prepare the data
            self.perform_sync(now)
            self.last_sync_time = now

        #reset
        if self.reset_flag:
          self.total_info = {}
          self.current_app = None
          self.session_start = None
          self.reset_flag = False

        hwnd, title, proc = self.get_active_window()
        idle_time = self.get_idle_time()

        if idle_time > self.idle_threshold: 
          if not self.was_idle:
              if self.current_app and self.session_start:
                duration = (now - self.idle_threshold) - self.session_start
                if duration>0:
                    self.total_info[self.current_app] = self.total_info.get(self.current_app, 0) + duration

              self.was_idle = True

              time.sleep(1)
              continue
          
        if self.was_idle:
          self.session_start = now
          self.was_idle = False

        if proc == "Unknown" or proc is None:
          time.sleep(0.1)
          continue

        if proc.lower() == "applicationframehost.exe": 
          app = title if title.strip() != "" else "Windows System App"
        else:
          app = self.normalize_win32_name(proc) #reutnring title if the app is an UWP app

        if not app or app == "Unknown":
          app = "System Idle"


        if date.today() != self.current_day:
            if self.current_app is not None:
                now = time.time()
                duration = now - self.session_start
                self.total_info[self.current_app] = (
                    self.total_info.get(self.current_app, 0) + duration
                )
                add_today_usage(self.current_app, duration)

            self.total_info = {}
            self.current_day = date.today()
            self.total_info = get_today_data()
            self.session_start = time.time()
            continue

        #on app switch  
        if app != self.current_app:
            if self.current_app is not None:
              duration = now - self.session_start
              if duration > 2.0:
                self.total_info[self.current_app] = (self.total_info.get(self.current_app, 0) + duration)
              else:
                print(f"[CLEANUP] Ignored brief switch to: {self.current_app} ({duration:.2f}s)")
            
            #new session
            self.current_app = app
            self.session_start = now

        #live display      
        display_info = self.total_info.copy()
        # 2. Add the live ticking seconds for the active app
        if self.current_app is not None and self.session_start is not None:
            live_delta = time.time() - self.session_start
            display_info[self.current_app] = display_info.get(self.current_app, 0) + live_delta

        # 3. Push this "Live + Total" dictionary to shared memory
        with stats_lock:
            stats_data.clear()
            stats_data.update(display_info)

        time.sleep(1)
    except Exception as e:
       worker_status["running"] = False,
       worker_status["error"] = str(e)
       

    self.finished.emit()
        
