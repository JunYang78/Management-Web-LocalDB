import json
import os
import threading
import webbrowser
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, Menu, Label, Button, Frame
from app import app

CONFIG_JSON = os.path.join(os.path.dirname(__file__), 'file_config.json')

class FlaskGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Web App Controller")
        self.geometry("400x250")
        self.resizable(False, False)

        menubar = Menu(self)
        menubar.add_command(label="Server",   command=self.show_server_page)
        menubar.add_command(label="Settings", command=self.show_settings_page)
        self.config(menu=menubar)

        self.server_frame   = Frame(self)
        self.settings_frame = Frame(self)

        self._build_server_frame()
        self._build_settings_frame()

        self.server_frame.pack(fill="both", expand=True)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_server_frame(self):
        f = self.server_frame
        f.pack_propagate(False)

        self.btn_start = Button(
            f,
            text="Start Server",
            width=25,
            height=2,
            font=("Arial", 14),
            command=self.start_server
        )
        self.btn_start.pack(pady=15, anchor='center')

        self.btn_stop = Button(
            f,
            text="Stop Server",
            width=25,
            height=2,
            font=("Arial", 14),
            state=tk.DISABLED,
            command=self.stop_server
        )
        self.btn_stop.pack(pady=15, anchor='center')

        self.server_thread = None

    def _build_settings_frame(self):
        f = self.settings_frame
        existing = ''
        if os.path.exists(CONFIG_JSON):
            try:
                with open(CONFIG_JSON, 'r', encoding='utf-8') as fd:
                    cfg = json.load(fd)
                existing = cfg.get('data_file', '')
            except:
                existing = ''

        Label(f, text="Current data file:", font=("Arial", 14), anchor="w").pack(fill="x", padx=10, pady=(10,0))
        self.lbl_path = Label(
            f,
            font=("Arial", 14),
            text=existing or "No file selected",
            relief="sunken",
            anchor="w",
            wraplength=380
        )
        self.lbl_path.pack(fill="x", padx=10, pady=(0,10))

        Button(
            f,
            text="Choose File…",
            width=25,
            height=2,
            font=("Arial", 14),
            command=self.select_file
        ).pack(pady=10)

    def show_server_page(self):
        self.settings_frame.pack_forget()
        self.server_frame.pack(fill="both", expand=True)

    def show_settings_page(self):
        self.server_frame.pack_forget()
        self.settings_frame.pack(fill="both", expand=True)

    def start_server(self):
        if not getattr(self, 'server_thread', None) or not self.server_thread.is_alive():
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

    def select_file(self):
        path = filedialog.askopenfilename(
            title="Select Excel file",
            filetypes=[("Excel files", ("*.xlsx", "*.xls"))]
        )
        if not path:
            return

        try:
            with open(CONFIG_JSON, 'w', encoding='utf-8') as f:
                json.dump({'data_file': path}, f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save config:\n{e}")
            return

        self.lbl_path.config(text=path)
        messagebox.showinfo("Saved", f"Configuration saved.\nPath: {path}")

if __name__ == "__main__":
    gui = FlaskGUI()
    gui.mainloop()
