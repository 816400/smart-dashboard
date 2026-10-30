import tkinter as tk
from tkinter import messagebox
import json
import os
import urllib.request
import webbrowser

CURRENT_VERSION = "1.0.0"
VERSION_URL = "https://raw.githubusercontent.com/816400/smart-dashboard/main/version.json"
DATA_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

class SmartDashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Smart Life Dashboard v{CURRENT_VERSION}")
        self.root.geometry("600x550")
        self.root.configure(bg="#1e1e2e")

        # --- متغيرات بومودورو ---
        self.work_time = 25 * 60
        self.time_left = self.work_time
        self.timer_running = False

        self.create_widgets()
        
        # فحص التحديثات عند بدء التشغيل في الخلفية
        self.root.after(2000, self.check_for_updates)

    def create_widgets(self):
        title_label = tk.Label(
            self.root, 
            text="Smart Productivity Dashboard", 
            font=("Helvetica", 18, "bold"), 
            bg="#1e1e2e", 
            fg="#cdd6f4"
        )
        title_label.pack(pady=10)

        # --- زر فحص التحديثات يدوياً ---
        update_btn = tk.Button(
            self.root, 
            text="Check for Updates 🔄", 
            command=lambda: self.check_for_updates(manual=True), 
            bg="#f9e2af", 
            fg="#11111b", 
            font=("Helvetica", 9, "bold")
        )
        update_btn.pack(pady=2)

        # --- قسم بومودورو ---
        pomo_frame = tk.LabelFrame(
            self.root, 
            text=" ⏱️ Pomodoro Timer ", 
            font=("Helvetica", 11, "bold"), 
            bg="#1e1e2e", 
            fg="#89b4fa",
            bd=2, 
            relief="groove"
        )
        pomo_frame.pack(fill="x", padx=20, pady=5)

        self.timer_label = tk.Label(
            pomo_frame, 
            text="25:00", 
            font=("Helvetica", 24, "bold"), 
            bg="#1e1e2e", 
            fg="#a6e3a1"
        )
        self.timer_label.pack(pady=2)

        btn_frame = tk.Frame(pomo_frame, bg="#1e1e2e")
        btn_frame.pack(pady=5)

        start_btn = tk.Button(btn_frame, text="Start", command=self.start_timer, bg="#a6e3a1", fg="#11111b", width=10, font=("Helvetica", 9, "bold"))
        start_btn.pack(side="left", padx=5)

        reset_btn = tk.Button(btn_frame, text="Reset", command=self.reset_timer, bg="#f38ba8", fg="#11111b", width=10, font=("Helvetica", 9, "bold"))
        reset_btn.pack(side="left", padx=5)

        # --- قسم قائمة المهام ---
        todo_frame = tk.LabelFrame(
            self.root, 
            text=" 📝 Daily To-Do List ", 
            font=("Helvetica", 11, "bold"), 
            bg="#1e1e2e", 
            fg="#89b4fa",
            bd=2, 
            relief="groove"
        )
        todo_frame.pack(fill="both", expand=True, padx=20, pady=5)

        input_frame = tk.Frame(todo_frame, bg="#1e1e2e")
        input_frame.pack(fill="x", padx=10, pady=5)

        self.task_entry = tk.Entry(input_frame, font=("Helvetica", 11), bg="#313244", fg="#cdd6f4", insertbackground="white")
        self.task_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.task_entry.bind("<Return>", lambda event: self.add_task())

        add_btn = tk.Button(input_frame, text="Add Task", command=self.add_task, bg="#89b4fa", fg="#11111b", font=("Helvetica", 9, "bold"))
        add_btn.pack(side="right")

        self.task_listbox = tk.Listbox(
            todo_frame, 
            font=("Helvetica", 10), 
            bg="#313244", 
            fg="#cdd6f4", 
            selectbackground="#45475a"
        )
        self.task_listbox.pack(fill="both", expand=True, padx=10, pady=5)

        delete_btn = tk.Button(todo_frame, text="Delete Selected Task", command=self.delete_task, bg="#f38ba8", fg="#11111b", font=("Helvetica", 9, "bold"))
        delete_btn.pack(pady=5)

        self.tasks = load_tasks()
        self.refresh_task_list()

    # --- منطق فحص التحديثات ---
    def check_for_updates(self, manual=False):
        try:
            req = urllib.request.urlopen(VERSION_URL, timeout=3)
            data = json.loads(req.read().decode("utf-8"))
            latest_version = data.get("version")
            download_url = data.get("download_url")
            notes = data.get("release_notes", "")

            if latest_version != CURRENT_VERSION:
                answer = messagebox.askyesno(
                    "تحديث جديد متوفر!", 
                    f"يتوفر إصدار جديد ({latest_version})!\n\nالتفاصيل: {notes}\n\nهل تريد فتح رابط التحميل الآن؟"
                )
                if answer:
                    webbrowser.open(download_url)
            elif manual:
                messagebox.showinfo("لا توجد تحديثات", "برنامجك على أحدث إصدار بالفعل!")
        except Exception as e:
            if manual:
                messagebox.showerror("خطأ", "تعذر الاتصال بالخادم لفحص التحديثات.")

    # --- بومودورو ---
    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def reset_timer(self):
        self.timer_running = False
        self.time_left = self.work_time
        self.timer_label.config(text="25:00")

    def update_timer(self):
        if self.timer_running and self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        elif self.time_left == 0:
            self.timer_running = False
            messagebox.showinfo("Pomodoro Done", "Great work! Time for a short break.")

    # --- المهام ---
    def add_task(self):
        task_text = self.task_entry.get().strip()
        if task_text:
            self.tasks.append(task_text)
            save_tasks(self.tasks)
            self.refresh_task_list()
            self.task_entry.delete(0, tk.END)

    def delete_task(self):
        try:
            selected_idx = self.task_listbox.curselection()[0]
            del self.tasks[selected_idx]
            save_tasks(self.tasks)
            self.refresh_task_list()
        except IndexError:
            messagebox.showwarning("Warning", "Please select a task to delete.")

    def refresh_task_list(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            self.task_listbox.insert(tk.END, f"• {task}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartDashboardApp(root)
    root.mainloop()