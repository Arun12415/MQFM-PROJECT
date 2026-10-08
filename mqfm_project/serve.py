"""
serve.py — Production entry point for Windows
--------------------------------------------------
Runs the app with Waitress (a production-grade WSGI server that works on
Windows, unlike Gunicorn). Use this instead of app.py for 24/7 running.

Run manually:
    python serve.py

Or point NSSM at this file to run it as a Windows Service (see README.md).
"""
import os
from waitress import serve
from app import app

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", 5001))

if __name__ == "__main__":
    print(f"Serving MQFM app on http://{HOST}:{PORT}  (Ctrl+C to stop)")
    serve(app, host=HOST, port=PORT, threads=4)
