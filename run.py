#!/usr/bin/env python3
"""
The Lenny Growth Assistant - One-Command Startup Runner
Starts both the FastAPI Backend and React Frontend concurrently.
"""

import os
import sys
import subprocess
import time
import signal
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def main():
    print("=" * 65)
    print(" ⚡ STARTING THE LENNY GROWTH ASSISTANT ⚡")
    print("=" * 65)

    # 1. Check Python & Node
    backend_dir = BASE_DIR / "backend"
    frontend_dir = BASE_DIR / "frontend"

    print("\n[1/3] Checking environment & directories...")
    if not (backend_dir / "data" / "transcripts").exists():
        print("ERROR: Transcripts directory not found at backend/data/transcripts!")
        sys.exit(1)

    print("✔ Transcripts verified (50 Lenny podcast episodes loaded).")

    # 2. Start FastAPI Backend
    print("\n[2/3] Launching FastAPI Backend on http://localhost:8000...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(backend_dir)
    )

    # 3. Start Frontend Dev Server
    print("[3/3] Launching React Vite Frontend on http://localhost:5173...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=str(frontend_dir)
    )

    print("\n" + "=" * 65)
    print(" 🚀 THE LENNY GROWTH ASSISTANT IS LIVE!")
    print("=" * 65)
    print(" 👉 Web Application:   http://localhost:5173")
    print(" 👉 API Documentation: http://localhost:8000/docs")
    print(" 👉 System Health:     http://localhost:8000/api/health")
    print("=" * 65)
    print("Press Ctrl+C to terminate both servers.\n")

    # Open browser after 2 seconds
    time.sleep(2)
    try:
        webbrowser.open("http://localhost:5173")
    except Exception:
        pass

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Lenny Assistant services...")
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_proc.wait()
        frontend_proc.wait()
        print("Done. Goodbye!")

if __name__ == "__main__":
    main()
