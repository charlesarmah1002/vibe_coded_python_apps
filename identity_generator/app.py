import tkinter as tk
from tkinter import ttk
import random
import string

class GeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dark Identity Generator")
        self.root.geometry("450x600")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)

        # Colors
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#3d5afe"
        self.secondary_bg = "#2d2d2d"

        # Data for Username Generation
        self.adjectives = ["Swift", "Silent", "Shadow", "Neon", "Cyber", "Mystic", "Frost", "Blaze", "Iron", "Lunar", "Solar", "Void", "Ethereal", "Grim", "Radiant"]
        self.nouns = ["Hunter", "Ghost", "Rider", "Blade", "Wolf", "Raven", "Knight", "Storm", "Pulse", "Echo", "Titan", "Viper", "Dragon", "Phoenix", "Specter"]

        # Data for Name Generation
        self.first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
        self.last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

        self.setup_ui()

    def setup_ui(self):
        # Title
        title_label = tk.Label(
            self.root, text="Identity Generator", 
            font=("Helvetica", 20, "bold"), 
            bg=self.bg_color, fg=self.fg_color, pady=20
        )
        title_label.pack()

        # Notebook for Tabs
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.secondary_bg, foreground=self.fg_color, padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", self.accent_color)])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Username Tab
        self.username_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.username_frame, text="Username")
        self.setup_username_tab()

        # Name Tab
        self.name_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.name_frame, text="Real Name")
        self.setup_name_tab()

        # Result Display (Shared)
        self.result_var = tk.StringVar(value="Click Generate")
        self.result_label = tk.Label(
            self.root, textvariable=self.result_var,
            font=("Consolas", 16), bg=self.secondary_bg,
            fg=self.accent_color, width=30, height=2,
            relief="flat", pady=10
        )
        self.result_label.pack(pady=20)

        # Copy Button
        copy_btn = tk.Button(
            self.root, text="Copy to Clipboard", command=self.copy_to_clipboard,
            font=("Helvetica", 9), bg=self.secondary_bg,
            fg=self.fg_color, relief="flat", cursor="hand2", width=20
        )
        copy_btn.pack(pady=(0, 20))

    def setup_username_tab(self):
        # Length Control
        length_frame = tk.Frame(self.username_frame, bg=self.bg_color)
        length_frame.pack(pady=20)

        tk.Label(length_frame, text="Length:", font=("Helvetica", 10), bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT, padx=5)
        self.u_length_var = tk.IntVar(value=10)
        self.u_scale = ttk.Scale(length_frame, from_=5, to_=20, orient=tk.HORIZONTAL, variable=self.u_length_var, command=lambda e: self.u_display.config(text=str(int(self.u_length_var.get()))))
        self.u_scale.pack(side=tk.LEFT, padx=5)
        self.u_display = tk.Label(length_frame, text="10", font=("Helvetica", 10, "bold"), bg=self.bg_color, fg=self.fg_color, width=2)
        self.u_display.pack(side=tk.LEFT, padx=5)

        # Options
        self.use_numbers = tk.BooleanVar(value=True)
        self.use_special = tk.BooleanVar(value=False)
        tk.Checkbutton(self.username_frame, text="Include Numbers", variable=self.use_numbers, bg=self.bg_color, fg=self.fg_color, selectcolor=self.secondary_bg, activebackground=self.bg_color).pack(pady=5)
        tk.Checkbutton(self.username_frame, text="Include Special Chars", variable=self.use_special, bg=self.bg_color, fg=self.fg_color, selectcolor=self.secondary_bg, activebackground=self.bg_color).pack(pady=5)

        # Generate Button
        tk.Button(self.username_frame, text="GENERATE USERNAME", command=self.generate_username, font=("Helvetica", 10, "bold"), bg=self.accent_color, fg=self.fg_color, relief="flat", width=20, height=2).pack(pady=20)

    def setup_name_tab(self):
        # Length Control (Number of characters in total name)
        length_frame = tk.Frame(self.name_frame, bg=self.bg_color)
        length_frame.pack(pady=20)

        tk.Label(length_frame, text="Max Length:", font=("Helvetica", 10), bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT, padx=5)
        self.n_length_var = tk.IntVar(value=15)
        self.n_scale = ttk.Scale(length_frame, from_=8, to_=25, orient=tk.HORIZONTAL, variable=self.n_length_var, command=lambda e: self.n_display.config(text=str(int(self.n_length_var.get()))))
        self.n_scale.pack(side=tk.LEFT, padx=5)
        self.n_display = tk.Label(length_frame, text="15", font=("Helvetica", 10, "bold"), bg=self.bg_color, fg=self.fg_color, width=2)
        self.n_display.pack(side=tk.LEFT, padx=5)

        # Options
        self.include_middle = tk.BooleanVar(value=False)
        tk.Checkbutton(self.name_frame, text="Include Middle Initial", variable=self.include_middle, bg=self.bg_color, fg=self.fg_color, selectcolor=self.secondary_bg, activebackground=self.bg_color).pack(pady=10)

        # Generate Button
        tk.Button(self.name_frame, text="GENERATE NAME", command=self.generate_name, font=("Helvetica", 10, "bold"), bg=self.accent_color, fg=self.fg_color, relief="flat", width=20, height=2).pack(pady=20)

    def generate_username(self):
        length = int(self.u_length_var.get())
        base = random.choice(self.adjectives) + random.choice(self.nouns)
        if len(base) > length: base = base[:length]
        chars = ""
        if self.use_numbers.get(): chars += string.digits
        if self.use_special.get(): chars += "!@#$%^&*"
        username = list(base)
        while len(username) < length:
            username.append(random.choice(chars if chars else string.ascii_lowercase))
        if chars:
            for _ in range(min(2, length // 4)):
                username[random.randint(0, len(username)-1)] = random.choice(chars)
        self.result_var.set("".join(username))

    def generate_name(self):
        max_len = int(self.n_length_var.get())
        first = random.choice(self.first_names)
        last = random.choice(self.last_names)
        middle = f" {random.choice(string.ascii_uppercase)}." if self.include_middle.get() else ""
        
        full_name = f"{first}{middle} {last}"
        
        # If too long, try again or truncate
        attempts = 0
        while len(full_name) > max_len and attempts < 10:
            first = random.choice(self.first_names)
            last = random.choice(self.last_names)
            full_name = f"{first}{middle} {last}"
            attempts += 1
            
        self.result_var.set(full_name[:max_len])

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.result_var.get())

if __name__ == "__main__":
    root = tk.Tk()
    app = GeneratorApp(root)
    root.mainloop()
