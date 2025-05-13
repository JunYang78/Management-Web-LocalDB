import threading
import webbrowser
import sys
import tkinter as tk
from app import app

class FlaskGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Web App Controller")
        self.geometry("300x150")
        self.server_thread = None

        self.btn_start = tk.Button(self, text="Start", command=self.start_server, width=20, height=2)
        self.btn_start.pack(pady=10)

        self.btn_stop = tk.Button(self, text="Stop", command=self.stop_server, state=tk.DISABLED, width=20, height=2)
        self.btn_stop.pack()

    def start_server(self):
        if self.server_thread is None or not self.server_thread.is_alive():
            def run_flask():
                app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

            self.server_thread = threading.Thread(target=run_flask, daemon=True)
            self.server_thread.start()

            self.after(1000, lambda: webbrowser.open("http://127.0.0.1:5000/"))

            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)

    def stop_server(self):
        self.destroy()
        sys.exit(0)

    def on_close(self):
        self.stop_server()
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    gui = FlaskGUI()
    gui.protocol("WM_DELETE_WINDOW", gui.on_close)
    gui.mainloop()
