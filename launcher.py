import os
import sys
import traceback
import signal

def debug(msg):
    print("[LAUNCHER]", msg, flush=True)

# --- GLOBAL SHUTDOWN FLAG ---
stop_server = False

def handle_interrupt(sig, frame):
    global stop_server
    debug("Ctrl+C detected. Shutting down server...")
    stop_server = True
    try:
        if httpd:
            httpd.shutdown()
    except:
        pass
    sys.exit(0)

# Attach Ctrl+C handler (WORKS IN .EXE)
signal.signal(signal.SIGINT, handle_interrupt)
signal.signal(signal.SIGTERM, handle_interrupt)

try:
    debug("Starting launcher...")

    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    debug(f"Base dir = {base_dir}")

    # -------------------------------
    # FFMPEG PATH SETUP
    # -------------------------------
    ffmpeg_dir = os.path.join(base_dir, "ffmpeg", "bin")
    debug(f"Adding ffmpeg path: {ffmpeg_dir}")
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
    
    sys.path.insert(0, base_dir)
    debug("Added base_dir to sys.path")

    # -------------------------------
    # DJANGO SETUP
    # -------------------------------
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meeting_summarizer.settings")
    debug("Django settings set.")

    import django
    debug(f"Django imported OK — version {django.get_version()}")

    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    debug("WSGI application created successfully")

    # -------------------------------
    # START INTERNAL WSGI SERVER
    # -------------------------------
    from wsgiref.simple_server import make_server

    debug("Starting server...")
    global httpd
    httpd = make_server("127.0.0.1", 8000, application)
    debug("Server running at http://127.0.0.1:8000")

    # -------------------------------
    # OPEN BROWSER
    # -------------------------------
    import webbrowser
    try:
        webbrowser.open("http://127.0.0.1:8000")
        debug("Browser opened.")
    except:
        debug("Browser failed to open.")

    # -------------------------------
    # SERVE WITH INTERRUPT SUPPORT
    # -------------------------------
    while not stop_server:
        httpd.handle_request()   # allows graceful exit instead of blocking

    debug("Server stopped gracefully.")

except KeyboardInterrupt:
    handle_interrupt(None, None)

except Exception as e:
    debug("FATAL ERROR:")
    debug(str(e))
    debug(traceback.format_exc())
    input("\nPress Enter to exit...")
