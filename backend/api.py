from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, sys, requests, json
from shared.memory import stats_data, stats_lock
from backend.database import get_weekly_usage, get_monthly_usage
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from shared.status import *


if getattr(sys, 'frozen', False):
    BASE_PATH = Path(sys.executable).parent
    VERSION_FILE = BASE_PATH / "_internal" / "version.json"
    DIST_DIR = BASE_PATH / "_internal" / "frontend" / "dist"
else:
    BASE_PATH = Path(__file__).resolve().parent.parent
    VERSION_FILE = BASE_PATH / "version.json"
    DIST_DIR = BASE_PATH / "frontend" / "dist"


def get_local_version():
    try:
        with open(VERSION_FILE, "r") as f:
            data = json.load(f)
            return data.get("version", "0.0.0")
    except Exception:
        return "0.0.0"

APP_VERSION = get_local_version()

url = "https://raw.githubusercontent.com/sr1k7nth/WinTrack/main/remote_version.json"

def version_tuple(v):
    return tuple(map(int, v.split(".")))

app = FastAPI()
app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def format_top_apps(raw_data_dict):
    others_time = 0

    sorted_data = sorted(raw_data_dict.items(), key=lambda x: x[1], reverse=True)

    top_apps = sorted_data[:6]
    rest = sorted_data[6:]

    for app, duration in rest:
        others_time += duration
    
    if others_time > 0:
        top_apps.append(["Others",others_time])

    return dict(top_apps)

@app.get("/api/status")
def get_api_stats():
    return worker_status

@app.get("/api/daily")
def get_stats():
    with stats_lock:
        data = stats_data.copy()
    return format_top_apps(data)

@app.get("/api/weekly")
def weekly_stats():
    raw_weekly = get_weekly_usage()

    total_weekly = {}

    for day, apps in raw_weekly.items():
        for app, duration in apps.items():
            if app not in total_weekly:
                total_weekly[app] = 0
            total_weekly[app] += duration

    sorted_apps = sorted(
        total_weekly.items(),
        key=lambda x: x[1],
        reverse=True
    )

    top_apps = [app for app, _ in sorted_apps[:6]]

    formatted_daily = {}

    for day, apps in raw_weekly.items():
        day_data = {}
        others_time = 0

        for app, duration in apps.items():
            if app in top_apps:
                day_data[app] = duration
            else:
                others_time += duration

        for app in top_apps:
            if app not in day_data:
                day_data[app] = 0

        if others_time > 0:
            day_data["Others"] = others_time

        formatted_daily[day] = day_data

    formatted_totals = format_top_apps(total_weekly)

    return {
        "daily": formatted_daily,
        "totals": formatted_totals
    }

@app.get("/api/monthly")
def monthly_stats():
    raw_monthly = get_monthly_usage()
    total_weekly = {}

    for day, apps in raw_monthly.items():
        for app, duration in apps.items():
            if app not in total_weekly:
                total_weekly[app] = 0
            total_weekly[app] += duration

    sorted_apps = sorted(
        total_weekly.items(),
        key=lambda x: x[1],
        reverse=True
    )

    top_apps = [app for app, _ in sorted_apps[:6]]

    formatted_daily = {}

    for day, apps in raw_monthly.items():
        day_data = {}
        others_time = 0

        for app, duration in apps.items():
            if app in top_apps:
                day_data[app] = duration
            else:
                others_time += duration

        for app in top_apps:
            if app not in day_data:
                day_data[app] = 0

        if others_time > 0:
            day_data["Others"] = others_time

        formatted_daily[day] = day_data

    formatted_totals = format_top_apps(total_weekly)

    return {
        "daily": formatted_daily,
        "totals": formatted_totals
    }

@app.get("/api/update")
def get_version():
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        version_data = response.json()
        current_version = get_local_version()
        latest_version = version_data.get("latest_version", current_version)
        update_available = version_tuple(latest_version) > version_tuple(current_version)

        return {
            "update_available": update_available,
            "current_version": current_version,
            "latest_version": latest_version,
        }

    except Exception:
        return {
            "update_available": False,
            "current_version": APP_VERSION,
            "latest_version": APP_VERSION
        }

@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    file_path = DIST_DIR / full_path
    
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    
    return FileResponse(DIST_DIR / "index.html")


def run_api():
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=7777,
        reload=False,
        log_config=None
    )
