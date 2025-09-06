import tkinter as tk
from tkinter import messagebox
import os
import tkinter.ttk as ttk

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Tasks of Glory")
        self.root.geometry("900x600")
        self.tasks = []
        self.selected_column = None
        self.dragging = False
        self.drag_data = None

        self.root.configure(bg="#FFFACD")  # LemonChiffon yellow

        # App name label
        tk.Label(root, text="Tasks of Glory", font=("Segoe UI", 20, "bold"), bg="#FFFACD", fg="#333").pack(pady=(10, 0))

        # Entry and Add Button
        self.frame = tk.Frame(root, bg="#FFFACD")
        self.frame.pack(pady=10, fill="x")
        self.task_input = tk.Entry(self.frame, width=35, font=("Segoe UI", 12))
        self.task_input.pack(side=tk.LEFT, padx=10, pady=5, fill="x", expand=True)
        self.task_input.bind('<Return>', lambda event: self.add_task())
        tk.Button(self.frame, text="Add Task", font=("Segoe UI", 12), bg="#FFD700", fg="#333", relief="raised", command=self.add_task).pack(side=tk.LEFT, padx=10)

        # Criteria header (grid)
        self.criteria_frame = tk.Frame(root, bg="#FFFACD")
        self.criteria_frame.pack(fill="x", pady=(0, 5))
        for i in range(8):
            self.criteria_frame.grid_columnconfigure(i, weight=1)
        self.criteria_frame.grid_columnconfigure(0, minsize=220)

        tk.Label(self.criteria_frame, text="Task", font=("Segoe UI", 12, "bold"), bg="#FFFACD", fg="#333").grid(row=0, column=0, padx=10, sticky="w")
        self.priority_btn = tk.Button(self.criteria_frame, text="Priority", command=self.sort_by_priority,
                              bg="#FFD700", fg="#222", font=("Segoe UI", 12, "bold"), relief="raised")
        self.priority_btn.grid(row=0, column=1, padx=10, sticky="ew")
        self.ease_btn = tk.Button(self.criteria_frame, text="Ease of Task", command=self.select_ease,
                          bg="#FFD700", fg="#222", font=("Segoe UI", 12, "bold"), relief="raised")
        self.ease_btn.grid(row=0, column=2, padx=10, sticky="ew")
        tk.Label(self.criteria_frame, text="", bg="#FFFACD").grid(row=0, column=3)  # Drag handle for ease
        tk.Label(self.criteria_frame, text="", bg="#FFFACD").grid(row=0, column=4)  # Spacer
        self.urgency_btn = tk.Button(self.criteria_frame, text="Urgency", command=self.select_urgency,
                            bg="#FFD700", fg="#222", font=("Segoe UI", 12, "bold"), relief="raised")
        self.urgency_btn.grid(row=0, column=5, padx=10, sticky="ew")
        tk.Label(self.criteria_frame, text="", bg="#FFFACD").grid(row=0, column=6)  # Drag handle for urgency
        tk.Label(self.criteria_frame, text="", bg="#FFFACD").grid(row=0, column=7)  # Spacer

        # Task list frame (grid)
        self.tasks_frame = tk.Frame(root)
        self.tasks_frame.pack(fill="both", expand=True)
        for i in range(8):
            self.tasks_frame.grid_columnconfigure(i, weight=1)
        self.tasks_frame.grid_columnconfigure(0, minsize=220)

        # Remove and Sort buttons
        ttk.Button(root, text="Remove Completed Tasks", command=self.remove_completed).pack(pady=10)

        self.load_tasks()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def add_task(self, task_text=None, ease_rank=None, urgency_rank=None):
        if task_text is None:
            task_text = self.task_input.get()
        if task_text == "":
            messagebox.showwarning("Input Error", "Please enter a task.")
            return

        var = tk.BooleanVar()
        row = len(self.tasks)
        widgets = {}

        # Task checkbox (column 0)
        cb = tk.Checkbutton(self.tasks_frame, text=task_text, variable=var, anchor='w', width=30)
        cb.var = var
        cb.bind('<Double-1>', lambda event, idx=row: self.edit_task(idx))
        cb.grid(row=row, column=0, sticky="w")
        widgets['cb'] = cb

        # Ease and Urgency values
        ease_val = ease_rank if ease_rank else len(self.tasks) + 1
        urgency_val = urgency_rank if urgency_rank else len(self.tasks) + 1

        # Priority label (column 1)
        priority_label = tk.Label(self.tasks_frame, text=self.calc_priority(ease_val, urgency_val),
                         width=8, relief="solid", bg="#FFF", fg="#222", font=("Segoe UI", 12))
        priority_label.grid(row=row, column=1, padx=2, sticky="ew")
        widgets['priority_label'] = priority_label

        # Ease value label (column 2)
        ease_var = tk.IntVar(value=ease_val)
        ease_label = tk.Label(self.tasks_frame, text=str(ease_var.get()), width=5, relief="solid", bg="#FFF", fg="#222", font=("Segoe UI", 12))
        ease_label.grid(row=row, column=2, padx=2, sticky="ew")
        widgets['ease_var'] = ease_var
        widgets['ease_label'] = ease_label

        # Urgency value label (column 5)
        urgency_var = tk.IntVar(value=urgency_val)
        urgency_label = tk.Label(self.tasks_frame, text=str(urgency_var.get()), width=5, relief="solid", bg="#FFF", fg="#222", font=("Segoe UI", 12))
        urgency_label.grid(row=row, column=5, padx=2, sticky="ew")
        widgets['urgency_var'] = urgency_var
        widgets['urgency_label'] = urgency_label

        # Up/Down for urgency (columns 6/7)
        urgency_up_btn = tk.Button(self.tasks_frame, text="↑", width=2)
        urgency_down_btn = tk.Button(self.tasks_frame, text="↓", width=2)
        widgets['urgency_up_btn'] = urgency_up_btn
        widgets['urgency_down_btn'] = urgency_down_btn

        # Drag handle (column 3 for ease, 6 for urgency)
        drag_handle = tk.Label(self.tasks_frame, text="≡", font=("Segoe UI", 16), cursor="hand2", bg="#FFD700", fg="#222")
        widgets['drag_handle'] = drag_handle

        self.tasks.append(widgets)
        self.update_task_grid()
        self.task_input.delete(0, tk.END)

    def update_task_grid(self):
        active_bg = "#FFE4B5"  # Pale orange
        for widgets in self.tasks:
            for key in ['cb', 'priority_label', 'ease_label', 'urgency_label', 'ease_up_btn', 'ease_down_btn', 'urgency_up_btn', 'urgency_down_btn', 'drag_handle']:
                widget = widgets.get(key)
                if widget:
                    widget.grid_forget()
        for row, widgets in enumerate(self.tasks):
            # Update the double-click binding with the current row index
            widgets['cb'].unbind('<Double-1>')
            widgets['cb'].bind('<Double-1>', lambda event, idx=row: self.edit_task(idx))
            
            widgets['cb'].grid(row=row, column=0, sticky="ew")
            widgets['priority_label'].grid(row=row, column=1, padx=2, sticky="ew")
            widgets['ease_label'].grid(row=row, column=2, padx=2, sticky="ew")
            widgets['urgency_label'].grid(row=row, column=5, padx=2, sticky="ew")
            # Show drag handle only for selected column
            if self.selected_column == "ease":
                widgets['ease_label'].config(bg=active_bg, fg="#222")
                widgets['urgency_label'].config(bg="#FFF", fg="#222")
                widgets['drag_handle'].grid(row=row, column=3, padx=2)
                self.make_draggable(widgets['drag_handle'], row)
            elif self.selected_column == "urgency":
                widgets['urgency_label'].config(bg=active_bg, fg="#222")
                widgets['ease_label'].config(bg="#FFF", fg="#222")
                widgets['drag_handle'].grid(row=row, column=6, padx=2)
                self.make_draggable(widgets['drag_handle'], row)
            else:
                widgets['ease_label'].config(bg="#FFF", fg="#222")
                widgets['urgency_label'].config(bg="#FFF", fg="#222")
                widgets['drag_handle'].grid_forget()
            # Update priority value
            ease_val = int(widgets['ease_label'].cget("text"))
            urgency_val = int(widgets['urgency_label'].cget("text"))
            widgets['priority_label'].config(text=self.calc_priority(ease_val, urgency_val))

    def move_task(self, row, direction, criterion):
        new_idx = row + direction
        if 0 <= new_idx < len(self.tasks):
            self.tasks[row], self.tasks[new_idx] = self.tasks[new_idx], self.tasks[row]
            self.update_task_grid()
            self._reassign_ranks(criterion)

    def edit_task(self, task_idx):
        """Edit the text of a task"""
        if task_idx >= len(self.tasks):
            return
        
        widgets = self.tasks[task_idx]
        current_text = widgets['cb'].cget('text')
        
        # Create a simple dialog for editing
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Task")
        edit_window.geometry("400x150")
        edit_window.configure(bg="#FFFACD")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Center the window
        edit_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        tk.Label(edit_window, text="Edit Task:", font=("Segoe UI", 12), bg="#FFFACD").pack(pady=10)
        
        # Entry for editing
        edit_entry = tk.Entry(edit_window, width=50, font=("Segoe UI", 12))
        edit_entry.pack(pady=10, padx=20, fill='x')
        edit_entry.insert(0, current_text)
        edit_entry.select_range(0, tk.END)
        edit_entry.focus()
        
        # Buttons frame
        btn_frame = tk.Frame(edit_window, bg="#FFFACD")
        btn_frame.pack(pady=10)
        
        def save_edit():
            new_text = edit_entry.get().strip()
            if new_text:
                widgets['cb'].config(text=new_text)
                edit_window.destroy()
            else:
                messagebox.showwarning("Input Error", "Task text cannot be empty.")
        
        def cancel_edit():
            edit_window.destroy()
        
        # Bind Enter key to save
        edit_entry.bind('<Return>', lambda event: save_edit())
        edit_window.bind('<Escape>', lambda event: cancel_edit())
        
        tk.Button(btn_frame, text="Save", command=save_edit, 
                 bg="#FFD700", fg="#333", font=("Segoe UI", 10), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=cancel_edit, 
                 bg="#FFA500", fg="#333", font=("Segoe UI", 10), width=10).pack(side=tk.LEFT, padx=5)

    def remove_completed(self):
        for widgets in self.tasks[:]:
            if widgets['cb'].var.get():
                for key in widgets:
                    widget = widgets[key]
                    if hasattr(widget, "destroy"):
                        widget.destroy()
                self.tasks.remove(widgets)
        
        # Reassign ease and urgency rankings after removal
        self._reassign_all_ranks()
        self.update_task_grid()

    def _reassign_all_ranks(self):
        """Reassign both ease and urgency rankings to remove gaps"""
        n = len(self.tasks)
        
        # Sort tasks by current ease ranking to maintain relative order
        ease_sorted_tasks = sorted(enumerate(self.tasks), key=lambda x: x[1]['ease_var'].get())
        
        # Reassign ease rankings (1 to n)
        for new_ease_rank, (original_idx, widgets) in enumerate(ease_sorted_tasks, start=1):
            widgets['ease_var'].set(new_ease_rank)
            widgets['ease_label'].config(text=str(new_ease_rank))
        
        # Sort tasks by current urgency ranking to maintain relative order
        urgency_sorted_tasks = sorted(enumerate(self.tasks), key=lambda x: x[1]['urgency_var'].get(), reverse=True)
        
        # Reassign urgency rankings (n to 1, where n is highest urgency)
        for new_urgency_rank, (original_idx, widgets) in enumerate(urgency_sorted_tasks, start=1):
            widgets['urgency_var'].set(new_urgency_rank)
            widgets['urgency_label'].config(text=str(new_urgency_rank))
        
        # Update priority values for all tasks
        for widgets in self.tasks:
            ease_val = widgets['ease_var'].get()
            urgency_val = widgets['urgency_var'].get()
            widgets['priority_label'].config(text=self.calc_priority(ease_val, urgency_val))

    def _reassign_ranks(self, criterion):
        n = len(self.tasks)
        for idx, widgets in enumerate(self.tasks, start=1):
            if criterion == "ease":
                widgets['ease_var'].set(idx)
                widgets['ease_label'].config(text=str(idx))
            elif criterion == "urgency":
                urgency_rank = n - idx + 1
                widgets['urgency_var'].set(urgency_rank)
                widgets['urgency_label'].config(text=str(urgency_rank))

    def save_tasks(self):
        with open("tasks.txt", "w", encoding="utf-8") as f:
            for widgets in self.tasks:
                text = widgets['cb'].cget("text")
                ease = widgets['ease_var'].get()
                urgency = widgets['urgency_var'].get()
                f.write(f"{text}|{ease}|{urgency}\n")

    def load_tasks(self):
        if os.path.exists("tasks.txt"):
            with open("tasks.txt", "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split("|")
                    if len(parts) == 3:
                        self.add_task(parts[0], int(parts[1]), int(parts[2]))
                    elif len(parts) == 1 and parts[0]:
                        self.add_task(parts[0])

    def sort_tasks(self):
        if self.selected_column == "ease":
            self.tasks.sort(key=lambda t: t['ease_var'].get())
        elif self.selected_column == "urgency":
            self.tasks.sort(key=lambda t: -t['urgency_var'].get())
        else:
            messagebox.showinfo("Sort Tasks", "Please select Ease or Urgency to sort.")
            return
        self.update_task_grid()

    def sort_by_priority(self):
        def get_priority(widgets):
            try:
                return float(widgets['priority_label'].cget("text"))
            except Exception:
                return float('inf')
        self.tasks.sort(key=get_priority)
        self.update_task_grid()

    def select_ease(self):
        self.selected_column = "ease"
        self.ease_btn.config(text="Ease of Task (Active)")
        self.urgency_btn.config(text="Urgency")
        self.tasks.sort(key=lambda t: t['ease_var'].get())
        self.update_task_grid()

    def select_urgency(self):
        self.selected_column = "urgency"
        self.urgency_btn.config(text="Urgency (Active)")
        self.ease_btn.config(text="Ease of Task")
        self.tasks.sort(key=lambda t: -t['urgency_var'].get())
        self.update_task_grid()

    def calc_priority(self, ease, urgency):
        return str(round(ease / urgency, 3)) if urgency != 0 else "0"

    def on_close(self):
        self.save_tasks()
        self.root.destroy()

    def make_draggable(self, widget, row):
        # Unbind first to avoid duplicate bindings
        widget.unbind("<ButtonPress-1>")
        widget.unbind("<B1-Motion>")
        widget.unbind("<ButtonRelease-1>")
        if self.selected_column in ("ease", "urgency"):
            widget.bind("<ButtonPress-1>", lambda event, r=row: self.start_drag(event, r))
            widget.bind("<B1-Motion>", self.do_drag)
            widget.bind("<ButtonRelease-1>", self.stop_drag)

    def start_drag(self, event, row):
        self.drag_data = {"row": row, "y": event.y_root}
        self.dragging = True

    def do_drag(self, event):
        if not hasattr(self, "drag_data") or not self.dragging:
            return
        y = event.y_root
        delta = y - self.drag_data["y"]
        if abs(delta) > 20:  # Adjust sensitivity as needed
            new_row = self.drag_data["row"] + (1 if delta > 0 else -1)
            if 0 <= new_row < len(self.tasks):
                self.tasks[self.drag_data["row"]], self.tasks[new_row] = self.tasks[new_row], self.tasks[self.drag_data["row"]]
                self.drag_data["row"] = new_row
                self.drag_data["y"] = y
                self.update_task_grid()
                # Reassign ranks for the selected column
                if self.selected_column in ("ease", "urgency"):
                    self._reassign_ranks(self.selected_column)

    def stop_drag(self, event):
        self.dragging = False
        self.drag_data = None

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManager(root)
    root.mainloop()
