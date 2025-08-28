# base_tab.py
import tkinter as tk
from tkinter import ttk, messagebox

class BaseTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.style = ttk.Style()
        self.style.configure("Header.TLabel", font=("Arial", 10, "bold"))
        self.style.configure("Required.TLabel", foreground="red")
        self.style.configure("Success.TButton", foreground="green")

    def info(self, msg: str):
        messagebox.showinfo("Info", msg)

    def error(self, msg: str):
        messagebox.showerror("Erro", msg)

    def create_section(self, parent, title):
        frame = ttk.LabelFrame(parent, text=title, padding=(10, 5))
        return frame

    def create_form_field(self, parent, label, row, required=False, tooltip=None):
        label_widget = ttk.Label(parent, text=label)
        if required:
            label_widget.configure(style="Required.TLabel")
        else:
            label_widget.configure(style="Header.TLabel")
        label_widget.grid(row=row, column=0, sticky="w", pady=(5, 2))
        
        if tooltip:
            self.create_tooltip(label_widget, tooltip)
            
        return row + 1

    def create_tooltip(self, widget, text):
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = ttk.Label(tooltip, text=text, background="yellow", relief="solid", borderwidth=1)
            label.pack()
            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
