import os
import subprocess
import tkinter as tk
from tkinter import ttk
import threading
import logging
import webbrowser
from datetime import datetime, timedelta, timezone
import tkinter.messagebox

REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HOME_DIR = os.path.expanduser('~')
DEBUG_DIR = os.path.join(HOME_DIR, 'Debug_log')
os.makedirs(DEBUG_DIR, exist_ok=True)
LOG_FILE = os.path.join(DEBUG_DIR, 'updater_log.txt')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def log_run_header():
    max_size = 2 * 1024 * 1024  # 2MB
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > max_size:
        with open(LOG_FILE, 'w') as f:
            f.write('')
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz)
    header = f"/----------{now.strftime('%H:%M:%S (UTC+8) %Y-%m-%d')}---------/"
    with open(LOG_FILE, 'a') as f:
        f.write(header + '\n')
    logging.info(header)

log_run_header()

class UpdaterGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Repo Updater")
        self.root.geometry("500x320")
        self.root.attributes('-topmost', True)

        # Center container using place for true center alignment
        self.container = tk.Frame(self.root)
        self.container.place(relx=0.5, rely=0.5, anchor='c')

        self.label = tk.Label(self.container, text="Checking for updates...", font=("Arial", 16), anchor="center", justify="center")
        self.label.pack(pady=10)

        self.progress = ttk.Progressbar(self.container, mode='determinate', length=300, maximum=100)
        self.progress.pack(pady=5)
        self.progress['value'] = 0

        self.btn_frame = tk.Frame(self.container)
        self.github_btn = tk.Button(self.btn_frame, text="GitHub", width=15,
                    command=lambda: webbrowser.open_new_tab("https://github.com/JiaLeChye/MobileRobot"))
        self.github_btn.pack(side=tk.LEFT, padx=10)
        self.readme_btn = tk.Button(self.btn_frame, text="README.md", width=15,
                    command=lambda: webbrowser.open_new_tab("https://github.com/JiaLeChye/MobileRobot/blob/master/README.md"))
        self.readme_btn.pack(side=tk.LEFT, padx=10)
        self.btn_frame.pack(pady=8)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.closed = False

        # Conflict widgets
        self.conflict_label = tk.Label(
            self.container,
            text="",
            fg="red",
            font=("Arial", 12),
            anchor="center",
            justify="center",
            wraplength=420
        )
        self.conflict_label.pack(pady=6, fill="x")

        # Conflict tree (two columns: file + modified time)
        self.conflict_list_container = tk.Frame(self.container)
        columns = ("file", "modified")
        self.conflict_tree = ttk.Treeview(self.conflict_list_container, columns=columns, show="headings", height=7)
        self.conflict_tree.heading("file", text="File")
        self.conflict_tree.heading("modified", text="Modified")
        self.conflict_tree.column("file", width=260, anchor="w")
        self.conflict_tree.column("modified", width=140, anchor="e")
        tree_scroll = ttk.Scrollbar(self.conflict_list_container, orient=tk.VERTICAL, command=self.conflict_tree.yview)
        self.conflict_tree.configure(yscrollcommand=tree_scroll.set)
        self.conflict_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.conflict_list_container.pack_forget()

        self.overwrite_btn = tk.Button(self.container, text="Overwrite (Force Update)", fg="white", bg="red",
                                       command=self.overwrite_conflicts)
        self.overwrite_btn.pack_forget()
        self.hide_conflicts()

    def show_conflicts(self, files=None, message=None):
        # Hide action buttons while showing conflict/error context
        if self.btn_frame.winfo_ismapped():
            self.btn_frame.pack_forget()

        # Reset tree content visibility
        for iid in self.conflict_tree.get_children():
            self.conflict_tree.delete(iid)
        self.conflict_list_container.pack_forget()

        if message and files:
            # Combine both if both provided
            combined = message.strip() + "\n"
        else:
            combined = ""

        if message:
            self.conflict_label.config(text=message.strip())
        elif files:
            self.conflict_label.config(text="Merge conflict detected! Review the affected files below.")
        else:
            self.conflict_label.config(text="Problem detected.")

        if files:
            for f in files:
                try:
                    abs_path = os.path.join(REPO_PATH, f)
                    mtime = os.path.getmtime(abs_path)
                    date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    date_str = "Unknown"
                self.conflict_tree.insert('', 'end', values=(f, date_str))
            self.conflict_list_container.pack(pady=4, fill=tk.BOTH, expand=True)

        self.overwrite_btn.pack(pady=6)
        self.root.update_idletasks()

    def hide_conflicts(self):
        self.conflict_label.config(text="")
        self.conflict_list_container.pack_forget()
        self.overwrite_btn.pack_forget()
        if not self.btn_frame.winfo_ismapped():
            self.btn_frame.pack(pady=8)

    def set_status(self, msg, progress=None):
        self.label.config(text=msg)
        if progress is not None:
            self.progress['value'] = progress
        # Hide progress bar if done
        if progress == 100 or (progress is None and not ("Checking" in msg or "Fetching" in msg or "Pulling" in msg or "Updating" in msg)):
            self.progress.pack_forget()
        else:
            self.progress.pack(pady=5)
        # Always show GitHub/README buttons
        if not self.btn_frame.winfo_ismapped():
            self.btn_frame.pack(pady=8)
        self.root.update_idletasks()

    def overwrite_conflicts(self):
        # Force checkout and pull, discarding local changes
        try:
            self.set_status("Overwriting local changes...", progress=90)
            subprocess.run(["git", "reset", "--hard"], cwd=REPO_PATH, check=True)
            subprocess.run(["git", "clean", "-fd"], cwd=REPO_PATH, check=True)
            subprocess.run(["git", "pull"], cwd=REPO_PATH, check=True)
            self.set_status("Repo updated!", progress=100)
            logging.info("Repo forcibly updated (overwrite mode).")
            self.close_after(60)
        except Exception as e:
            self.set_status(f"Error: {e}", progress=100)
            logging.error(f"Error during overwrite: {e}", exc_info=True)

    def close_after(self, seconds):
        self.root.after(int(seconds * 1000), self.root.destroy)

    def on_close(self):
        self.closed = True
        self.root.destroy()

    def run(self):
        self.root.mainloop()

def get_conflict_files():
    try:
        result = subprocess.run(["git", "ls-files", "-u"], cwd=REPO_PATH, capture_output=True, text=True)
        lines = result.stdout.strip().splitlines()
        files = set()
        for line in lines:
            parts = line.split('\t')
            if len(parts) == 2:
                files.add(parts[1])
        return sorted(files)
    except Exception:
        return []

def update_repo(gui: UpdaterGUI):
    try:
        logging.info("Starting update process.")
        gui.set_status("Checking for updates...", progress=0)
        gui.hide_conflicts()
        gui.set_status("Fetching updates...", progress=25)
        logging.info("Running: git fetch")
        fetch_result = subprocess.run(["git", "fetch"], cwd=REPO_PATH, capture_output=True, text=True)
        logging.info(f"git fetch stdout: {fetch_result.stdout.strip()}")
        if fetch_result.stderr:
            logging.warning(f"git fetch stderr: {fetch_result.stderr.strip()}")
        gui.set_status("Pulling latest changes...", progress=75)
        logging.info("Running: git pull")
        pull_result = subprocess.run(["git", "pull"], cwd=REPO_PATH, capture_output=True, text=True)
        logging.info(f"git pull stdout: {pull_result.stdout.strip()}")
        if pull_result.stderr:
            logging.warning(f"git pull stderr: {pull_result.stderr.strip()}")

        conflict_keywords = [
            "would be overwritten by merge",
            "Please commit your changes or stash them before you merge",
            "Aborting",
            "error:",
            "divergent branches",
            "Need to specify how to reconcile divergent branches"
        ]
        conflict_in_stderr = any(kw in pull_result.stderr for kw in conflict_keywords)
        divergent_error = "Need to specify how to reconcile divergent branches" in pull_result.stderr or "divergent branches" in pull_result.stderr
        pull_failed = pull_result.returncode != 0
        if pull_failed or conflict_in_stderr:
            if divergent_error:
                concise_msg = "Update failed: Divergent branches detected."
                gui.set_status(concise_msg, progress=100)
                gui.show_conflicts(message=(
                    "Your local and remote branches have diverged.\n"
                    "Please run one of the following commands in the terminal before updating again:\n"
                    "git config pull.rebase false  # merge\n"
                    "git config pull.rebase true   # rebase\n"
                    "git config pull.ff only       # fast-forward only\n"
                    "See log for details."
                ))
                logging.error(concise_msg + " " + pull_result.stderr.strip())
                return
            concise_msg = "Update failed: local changes or conflict."
            gui.set_status(concise_msg, progress=100)
            files = []
            lines = pull_result.stderr.splitlines()
            capture = False
            for line in lines:
                if 'would be overwritten by merge:' in line:
                    capture = True
                    continue
                if capture:
                    if line.strip() == '' or line.startswith('Please commit') or line.startswith('Aborting'):
                        break
                    files.append(line.strip())
            if not files:
                files = get_conflict_files()
            if files:
                gui.show_conflicts(files=files)
            else:
                gui.show_conflicts(message="Click 'Overwrite' to force update (local changes will be lost).")
            logging.error(concise_msg + " " + pull_result.stderr.strip())
            return

        conflict_files = get_conflict_files()
        if conflict_files:
            gui.set_status("Merge conflict detected!", progress=100)
            gui.show_conflicts(conflict_files)
            logging.warning(f"Merge conflicts: {conflict_files}")
            return
        if "Already up to date" in pull_result.stdout:
            gui.set_status("Repo up to date", progress=100)
            logging.info("Repo is already up to date.")
            gui.close_after(60)
        else:
            gui.set_status("Repo updated!", progress=100)
            logging.info("Repo updated successfully.")
    except Exception as e:
        gui.set_status(f"Error: {e}", progress=100)
        logging.error(f"Error during update: {e}", exc_info=True)

def headless_update():
    try:
        logging.info("Starting update process (headless mode).")
        subprocess.run(["git", "fetch"], cwd=REPO_PATH, check=True)
        logging.info("Running: git pull")
        result = subprocess.run(["git", "pull"], cwd=REPO_PATH, capture_output=True, text=True)
        logging.info(f"git pull output: {result.stdout.strip()}")
        conflict_files = get_conflict_files()
        if conflict_files:
            logging.warning(f"Merge conflicts: {conflict_files}")
            logging.warning("Merge conflict detected! Please resolve manually or run the updater in GUI mode to use the overwrite option.")
            print("Merge conflict detected! Files:")
            for f in conflict_files:
                print(f" - {f}")
            print("Resolve manually or run updater.py in GUI mode to force overwrite.")
            return
        if "Already up to date" in result.stdout:
            logging.info("Repo is already up to date.")
        else:
            logging.info("Repo updated successfully.")
    except Exception as e:
        logging.error(f"Error during update: {e}", exc_info=True)

def is_gui_available():
    return os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")

def main():
    if is_gui_available():
        gui = UpdaterGUI()
        t = threading.Thread(target=update_repo, args=(gui,), daemon=True)
        t.start()
        gui.run()
    else:
        print("No GUI detected. Running in headless mode.")
        headless_update()

if __name__ == "__main__":
    main()
