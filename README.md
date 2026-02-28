# Screen Time App
A desktop screen-time tracking application built with:

- PySide6 (Desktop App & System Tray)
- FastAPI (Backend API)
- React + Vite (Frontend Dashboard)
- Chart.js (Data Visualization)

The app tracks daily app usage and provides:
- Daily stats
- Weekly analytics
- Monthly summaries

---

## Features
- Real-time application usage tracking
- Daily usage breakdown
- Weekly usage trends (Line charts)
- Monthly summaries
- Also detects inactive time and handle's it smartly.

---

## Screenshots
![Daily](media/screenshots/daily.png)
![Weekly](media/screenshots/weekly.png)
![Monthly](media/screenshots/monthly.png)

---

## Architecture
```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "background": "#0f172a",
    "primaryColor": "#1e293b",
    "primaryTextColor": "#e2e8f0",
    "primaryBorderColor": "#334155",
    "lineColor": "#64748b",
    "secondaryColor": "#1e293b",
    "tertiaryColor": "#1e293b",
    "fontFamily": "monospace"
  }
}}%%

graph TD
    A[User] -->|Interact via tray / app| B[PySide6 GUI<br>gui/interface.py → python -m gui.interface]

    subgraph "GUI Layer (gui/)"
        B --> C[QSystemTrayIcon<br>Start/Pause/Quit/Open Dashboard]
        B --> D[Main Window / Settings]
        B --> E[QThread Worker Launch]
    end

    E --> F[Screen Time Worker<br>st_tracker/worker.py]

    subgraph "Tracking Layer (st_tracker/)"
        F --> G[Periodic Polling Loop<br>~1-5s interval]
        G --> H[Windows API Calls<br>→ win32gui.GetForegroundWindow<br>→ win32process.GetWindowThreadProcessId<br>→ GetModuleFileNameEx / psutil]
        H --> I[Get: process name, exe path, window title]
        G --> J[Idle / AFK Check<br>→ GetLastInputInfo or similar]
        J -->|Idle > threshold| K[Pause accumulation<br>Mark as INACTIVE]
        I -->|Active window change| L[Calculate duration slice<br>Current - last timestamp]
        L --> M[Create usage record<br>timestamp + app + title + duration + active flag]
        M --> N[Save to SQLite<br>via shared/db or backend/database.py helper]
    end

    subgraph "Backend / API Layer (backend/)"
        N --> O[FastAPI Application<br>backend/api.py]
        O --> P[Key Endpoints]
        P --> Q[GET /api/daily<br>→ aggregated daily stats]
        P --> R[GET /api/weekly<br>→ time-series data for line chart]
        P --> S[GET /api/monthly<br>→ monthly totals / breakdown]
        O --> T[Serve Static Files<br>frontend/dist/ → React build]
        O --> U[SPA Fallback Route<br>catch-all → index.html]
        O -->|DB access| V[SQLite Connection<br>backend/database.py]
    end

    subgraph "Frontend Dashboard (frontend/ → React + Vite)"
        W[Tray → 'Open Dashboard'] --> X[Browser opens http://localhost:port]
        X --> Y[React SPA<br>src/App.tsx / main entry]
        Y -->|fetch / axios| Q
        Y -->|fetch / axios| R
        Y -->|fetch / axios| S
        Q & R & S --> Z[Chart.js renders:<br>→ Daily pie/bar<br>→ Weekly line/area<br>→ Monthly summary]
        Z --> AA[Interactive UI<br>totals, top apps, trends, tooltips]
    end

    subgraph "Shared Utilities"
        AB[shared/ → constants / models / db helpers<br>e.g. DB path, schemas, API base]
        AB -.-> F
        AB -.-> O
        AB -.-> Y
    end

    style A fill:#7c3aed,stroke:#e2e8f0,color:#ffffff
    style W fill:#2563eb,stroke:#e2e8f0,color:#ffffff
    style AA fill:#059669,stroke:#e2e8f0,color:#ffffff
```

---

## Setup (Development)

#### 1. Clone repository
```
git clone https://github.com/yourusername/screen-time.git
cd screen-time
```

#### 2. Create virtual environment
```
python -m venv venv
venv\Scripts\activate
```

#### 3. Install backend dependencies
```
pip install -r requirements.txt
```

### Frontend (Development Mode)
```
cd frontend
npm install
npm run dev
```

### Production Mode
```
cd frontend
npm run build
python -m gui.interface
```

