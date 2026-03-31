"""Desktop wrapper for Book Page Summarizer using PyWebView."""

import sys
import threading

import webview

from server import app

HOST = "127.0.0.1"
PORT = 5000
URL = f"http://{HOST}:{PORT}"
TITLE = "Book Page Summarizer"


def start_server():
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    window = webview.create_window(
        TITLE,
        URL,
        width=1280,
        height=860,
        min_size=(800, 600),
    )
    webview.start()
    sys.exit(0)
