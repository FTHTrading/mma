"""
MMA.INC x Unykorn.ai x BitGo Enterprise — One-Click Platform Launcher
Starts the backend API server and opens the command center interface in the default browser.
"""

import os
import sys
import webbrowser
import threading
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Set root directory
PLATFORM_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER_DIR = os.path.join(PLATFORM_DIR, "server")
sys.path.insert(0, SERVER_DIR)

from api_server import run_server

def open_browser():
    time.sleep(1.2)
    port = 8888
    port_file = os.path.join(PLATFORM_DIR, ".active_port")
    if os.path.exists(port_file):
        try:
            with open(port_file, "r") as f:
                port = int(f.read().strip())
        except Exception:
            pass
    url = f"http://127.0.0.1:{port}/index.html"
    print(f"\n[LAUNCHER] Opening MMA.INC Command Center at: {url}")
    webbrowser.open(url)

def main():
    port = int(os.environ.get("PORT", 8888))
    print("================================================================")
    print(" [LAUNCHER] INITIALIZING MMA.INC x UNYKORN.AI x BITGO PLATFORM")
    print("    - ERC-3643 Permissioned Token Engine")
    print("    - BitGo Enterprise Qualified Custody & Treasury Rails")
    print("    - Multi-Jurisdiction Compliance (US, JP, TH, SG, UAE)")
    print("    - $21M Run-Rate Financial Velocity Engine")
    print("================================================================")

    # Launch browser in a background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Start HTTP server
    run_server(port)

if __name__ == "__main__":
    main()
