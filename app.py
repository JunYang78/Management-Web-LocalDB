import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os

# Excel file path
EXCEL_FILE = r'C:\LocalDB\CKENG.xlsx'

# Helper function to read a sheet from the Excel file
def read_data(sheet_name):
    if os.path.exists(EXCEL_FILE):
        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
        except Exception as e:
            print(f"Error reading {sheet_name}:", e)
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()
    return df

# ---------------------------
# Frame 1: List of CUs (Main Page)
# ---------------------------
class CUListFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Main title centered at the top
        title = tk.Label(self, text="List of CUs", font=("Arial", 24))
        title.pack(pady=20)
        
        # Center the listbox with more padding
        self.cu_listbox = tk.Listbox(self, font=("Helvetica", 16), width=40, height=10)
        self.cu_listbox.pack(fill="both", expand=True, padx=50, pady=20)
        self.cu_listbox.bind("<<ListboxSelect>>", self.on_cu_select)
        
        self.load_cus()

    def load_cus(self):
        df_cu = read_data("CU")
        self.cu_listbox.delete(0, tk.END)
        self.cu_data = df_cu.to_dict(orient='records')
        for cu in self.cu_data:
            display = f"{cu.get('CU_Name', 'N/A')} - {cu.get('Location', 'Unknown')}"
            self.cu_listbox.insert(tk.END, display)

    def on_cu_select(self, event):
        if not self.cu_listbox.curselection():
            return
        index = self.cu_listbox.curselection()[0]
        selected_cu = self.cu_data[index]
        self.controller.show_cu_details(selected_cu)

# ---------------------------
# Frame 2: CU Details (Shows Parts and FCUs)
# ---------------------------
class CUDetailsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Selected CU info at the top
        self.cu_info_label = tk.Label(self, text="", font=("Arial", 20))
        self.cu_info_label.pack()

        self.cu_location_label = tk.Label(self, text="", font=("Arial", 20))
        self.cu_location_label.pack(pady=20)
        
        # Content frame with two panels
        content_frame = tk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=50, pady=20)
        
        # Left Panel: CU Parts list
        left_frame = tk.Frame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=20)
        
        tk.Label(left_frame, text="CU Parts", font=("Arial", 18)).pack(pady=10)
        self.parts_listbox = tk.Listbox(left_frame, font=("Helvetica", 16), width=25, height=8)
        self.parts_listbox.pack(fill="both", expand=True, pady=10)
        self.parts_listbox.bind("<Double-Button-1>", self.on_part_double_click)
        
        # Right Panel: FCUs list
        right_frame = tk.Frame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=20)
        tk.Label(right_frame, text="FCUs", font=("Arial", 18)).pack(pady=10)
        self.fcu_listbox = tk.Listbox(right_frame, font=("Helvetica", 16), width=25, height=8)
        self.fcu_listbox.pack(fill="both", expand=True, pady=10)
        self.fcu_listbox.bind("<<ListboxSelect>>", self.on_fcu_select)
        
        # Back Button centered at the bottom
        back_btn = tk.Button(self, text="Back", font=("Arial", 16),
                             command=lambda: controller.show_frame("CUListFrame"))
        back_btn.pack(pady=20)

    def set_cu(self, cu):
        self.selected_cu = cu
        self.cu_info_label.config(text=f"CU: {cu.get('CU_Name', 'N/A')}")
        self.cu_location_label.config(text=f"Location: {cu.get('Location', 'Unknown')}")
        # Load parts for the selected CU
        df_parts = read_data("CU_Parts")
        parts = df_parts[df_parts['CU_ID'] == cu.get('CU_ID')].to_dict(orient='records')
        self.parts_data = parts
        self.parts_listbox.delete(0, tk.END)
        for part in parts:
            display = f"{part.get('Part_Name', 'Unnamed')}"
            self.parts_listbox.insert(tk.END, display)
        
        # Load FCUs for the selected CU
        df_fcus = read_data("FCU")
        fcus = df_fcus[df_fcus['CU_ID'] == cu.get('CU_ID')].to_dict(orient='records')
        self.fcu_data = fcus
        self.fcu_listbox.delete(0, tk.END)
        for fcu in fcus:
            display = f"{fcu.get('FCU_Name', 'Unnamed')}"
            self.fcu_listbox.insert(tk.END, display)

    def on_part_double_click(self, event):
        if not self.parts_listbox.curselection():
            return
        index = self.parts_listbox.curselection()[0]
        selected_part = self.parts_data[index]
        self.controller.show_cupart_details(selected_part)

    def on_fcu_select(self, event):
        if not self.fcu_listbox.curselection():
            return
        index = self.fcu_listbox.curselection()[0]
        selected_fcu = self.fcu_data[index]
        self.controller.show_fcu_details(selected_fcu)

# ---------------------------
# Frame 3: FCU Activities (Details for selected FCU)
# ---------------------------
class FCUActivitiesFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.fcu_info_label = tk.Label(self, text="", font=("Arial", 20))
        self.fcu_info_label.pack(pady=20)
        
        tk.Label(self, text="FCU Activities", font=("Arial", 18)).pack(pady=10)
        self.fcu_act_listbox = tk.Listbox(self, font=("Helvetica", 16), width=40, height=10)
        self.fcu_act_listbox.pack(fill="both", expand=True, padx=50, pady=20)
        
        back_btn = tk.Button(self, text="Back", font=("Arial", 16),
                             command=lambda: controller.show_frame("CUDetailsFrame"))
        back_btn.pack(pady=20)
        
    def set_fcu(self, fcu):
        self.selected_fcu = fcu
        self.fcu_info_label.config(text=f"FCU: {fcu.get('FCU_Name', 'Unnamed')}")
        df_activities = read_data("FCU_Activity")
        acts = df_activities[df_activities['FCU_ID'] == fcu.get('FCU_ID')].to_dict(orient='records')
        self.fcu_act_listbox.delete(0, tk.END)
        for act in acts:
            display = f"{act.get('Activity_Name', 'Unnamed')} on {act.get('Activity_Date', '')}"
            self.fcu_act_listbox.insert(tk.END, display)

# ---------------------------
# Frame 4: CU Part Activities (Details for selected CU Part)
# ---------------------------
class CUPartActivitiesFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.part_info_label = tk.Label(self, text="", font=("Arial", 20))
        self.part_info_label.pack(pady=20)

        tk.Label(self, text="CU Part Activities", font=("Arial", 18)).pack(pady=10)
        self.part_act_listbox = tk.Listbox(self, font=("Helvetica", 16), width=40, height=10)
        self.part_act_listbox.pack(fill="both", expand=True, padx=50, pady=20)

        back_btn = tk.Button(self, text="Back", font=("Arial", 16),
                             command=lambda: controller.show_frame("CUDetailsFrame"))
        back_btn.pack(pady=20)

    def set_part(self, part):
        self.selected_part = part
        self.part_info_label.config(text=f"Part: {part.get('Part_Name', 'Unnamed')}")
        df_activities = read_data("CU_Parts_Activity")
        acts = df_activities[df_activities['Part_ID'] == part.get('Part_ID')].to_dict(orient='records')
        self.part_act_listbox.delete(0, tk.END)
        for act in acts:
            display = f"{act.get('Activity_Name', 'Unnamed')} on {act.get('Activity_Date', '')}"
            self.part_act_listbox.insert(tk.END, display)

# ---------------------------
# Main Application: Manages Navigation Among Frames
# ---------------------------
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CKEng Management App")
        # Increase the window size to 1024x768 for a more spacious layout
        self.geometry("900x506")
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (CUListFrame, CUDetailsFrame, FCUActivitiesFrame, CUPartActivitiesFrame):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("CUListFrame")
    
    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()
        
    def show_cu_details(self, cu):
        frame = self.frames["CUDetailsFrame"]
        frame.set_cu(cu)
        self.show_frame("CUDetailsFrame")
    
    def show_fcu_details(self, fcu):
        frame = self.frames["FCUActivitiesFrame"]
        frame.set_fcu(fcu)
        self.show_frame("FCUActivitiesFrame")
    
    def show_cupart_details(self, part):
        frame = self.frames["CUPartActivitiesFrame"]
        frame.set_part(part)
        self.show_frame("CUPartActivitiesFrame")
        
if __name__ == '__main__':
    app = MainApp()
    app.mainloop()
