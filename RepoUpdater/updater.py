
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

# Place Debug_log outside Desktop (in user's home directory)
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

# Write log header with time (UTC+8) and date

def log_run_header():
    # Clear log if too large (e.g., >2MB)
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
        self.root.geometry("400x180")
        self.root.attributes('-topmost', True)
        self.label = tk.Label(self.root, text="Checking for updates...", font=("Arial", 16))
        self.label.pack(pady=10)
        # Status bar (progress bar)
        self.progress = ttk.Progressbar(self.root, mode='determinate', length=300, maximum=100)
        self.progress.pack(pady=5)
        self.progress['value'] = 0
        # Buttons frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        github_btn = tk.Button(btn_frame, text="GitHub", width=15, command=lambda: webbrowser.open_new_tab("https://github.com/JiaLeChye/MobileRobot"))
        github_btn.pack(side=tk.LEFT, padx=10)
        readme_btn = tk.Button(btn_frame, text="README.md", width=15, command=lambda: webbrowser.open_new_tab("https://github.com/JiaLeChye/MobileRobot/blob/master/README.md"))
        readme_btn.pack(side=tk.LEFT, padx=10)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.closed = False
        # Conflict UI elements (hidden by default)
        self.conflict_label = tk.Label(self.root, text="", fg="red", font=("Arial", 12))
        self.conflict_label.pack(pady=5)
        self.conflict_files_box = tk.Listbox(self.root, width=50, height=4)
        self.conflict_files_box.pack_forget()
        self.overwrite_btn = tk.Button(self.root, text="Overwrite (Force Update)", fg="white", bg="red", command=self.overwrite_conflicts)
        self.overwrite_btn.pack_forget()
        self.hide_conflicts()

    def show_conflicts(self, files):
        self.conflict_label.config(text="Merge conflict detected! Please save your changes elsewhere if needed.")
        self.conflict_files_box.delete(0, tk.END)
        for f in files:
            self.conflict_files_box.insert(tk.END, f)
        self.conflict_files_box.pack(pady=2)
        self.overwrite_btn.pack(pady=5)
        self.root.update_idletasks()

    def hide_conflicts(self):
        self.conflict_label.config(text="")
        self.conflict_files_box.pack_forget()
        self.overwrite_btn.pack_forget()
        self.root.update_idletasks()

    def overwrite_conflicts(self):
        # Force checkout all files to match remote, discarding local changes
        try:
            subprocess.run(["git", "reset", "--hard", "origin/master"], cwd=REPO_PATH, check=True)
            subprocess.run(["git", "clean", "-fd"], cwd=REPO_PATH, check=True)
            tkinter.messagebox.showinfo("Overwrite Complete", "All conflicts have been overwritten with the latest update.")
            self.hide_conflicts()
            self.set_status("Repo forcibly updated to latest.", progress=100)
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Failed to overwrite: {e}")


    # open_readme method removed; now handled by webbrowser lambda

    def set_status(self, msg, progress=None):
        self.label.config(text=msg)
        if progress is not None:
            self.progress['value'] = progress
            self.progress.pack(pady=5)
        # Hide progress bar if done
        if progress == 100 or (progress is None and not ("Checking" in msg or "Fetching" in msg or "Pulling" in msg or "Updating" in msg)):
            self.progress.pack_forget()
        self.root.update_idletasks()

    def close_after(self, seconds):
        self.root.after(int(seconds * 1000), self.root.destroy)

    def on_close(self):
        self.closed = True
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def update_repo(gui: UpdaterGUI):
    try:
        logging.info("Starting update process.")
        gui.set_status("Checking for updates...", progress=0)
        gui.hide_conflicts()
        gui.set_status("Fetching updates...", progress=25)
        logging.info("Running: git fetch")
        subprocess.run(["git", "fetch"], cwd=REPO_PATH, check=True)
        gui.set_status("Pulling latest changes...", progress=75)
        logging.info("Running: git pull")
        result = subprocess.run(["git", "pull"], cwd=REPO_PATH, capture_output=True, text=True)
        logging.info(f"git pull output: {result.stdout.strip()}")
        # Check for conflicts
        conflict_files = get_conflict_files()
        if conflict_files:
            gui.set_status("Merge conflict detected!", progress=100)
            gui.show_conflicts(conflict_files)
            logging.warning(f"Merge conflicts: {conflict_files}")
            return
        if "Already up to date" in result.stdout:
            gui.set_status("Repo up to date", progress=100)
            logging.info("Repo is already up to date.")
            gui.close_after(60)
        else:
            gui.set_status("Repo updated!\n" + result.stdout.strip(), progress=100)
            logging.info("Repo updated successfully.")
    except Exception as e:
        gui.set_status(f"Error: {e}", progress=100)
        logging.error(f"Error during update: {e}", exc_info=True)

# Helper to get conflicted files
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
    # Check for X11/Wayland display or Raspberry Pi desktop session
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
