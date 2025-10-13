import os
import subprocess
import tkinter as tk
from tkinter import ttk
import threading
import logging
import webbrowser
import argparse
import sys
from datetime import datetime, timedelta, timezone
import tkinter.messagebox

# Network/offline detection keywords (stderr/stdout patterns)
# Only include genuine network connectivity issues
OFFLINE_KEYWORDS = [
    "Could not resolve hostname",
    "Temporary failure in name resolution", 
    "network is unreachable",
    "Name or service not known",
    "Connection timed out",
    "No route to host",
    "Failed to connect",
    "Connection refused",
    "Host is down",
    "Network timeout",
    "fatal: unable to connect",
    "Operation timed out",
    "couldn't connect to host"
]

# Separate authentication/access errors (not network issues)
ACCESS_ERROR_KEYWORDS = [
    "Could not read from remote repository",
    "Permission denied", 
    "Authentication failed"
]

# Git corruption detection keywords
CORRUPTION_KEYWORDS = [
    "object file .git/objects",
    "is empty",
    "is corrupt",
    "loose object",
    "stored in .git/objects",
    "fatal: loose object",
    "error: object file",
    "bad object",
    "corrupt object",
    "fatal: bad object",
    "git fsck"
]

REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HOME_DIR = os.path.expanduser('~')
DEBUG_DIR = os.path.join(HOME_DIR, 'Debug_log')
os.makedirs(DEBUG_DIR, exist_ok=True)
LOG_FILE = os.path.join(DEBUG_DIR, 'updater_log.txt')

# Setup logging - file only, no console spam
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE)
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

def print_recent_logs(lines=10):
    """Print only the most recent log entries to avoid console spam."""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                all_lines = f.readlines()
                recent = all_lines[-lines:] if len(all_lines) > lines else all_lines
                if recent:
                    print("".join(recent).strip())
    except Exception:
        pass  # Silently handle any file read issues

def test_network_connectivity():
    """Test basic network connectivity to github.com and general internet"""
    # Quick tests with short timeouts to avoid hanging
    tests = [
        # Test DNS resolution first (fastest)
        (['nslookup', 'github.com'], 2),
        # Test ping to github.com
        (['ping', '-c', '1', '-W', '2', 'github.com'], 3),
        # Test ping to Google DNS as fallback
        (['ping', '-c', '1', '-W', '2', '8.8.8.8'], 3),
    ]
    
    for cmd, timeout in tests:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if result.returncode == 0:
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    # All tests failed - no network connectivity
    return False

def is_git_corruption_error(combined_output):
    """Check if the git output indicates repository corruption."""
    if not combined_output:
        return False
    
    output_lower = combined_output.lower()
    
    # Check for corruption-specific keywords
    has_corruption = any(keyword.lower() in output_lower for keyword in CORRUPTION_KEYWORDS)
    
    return has_corruption

def repair_git_repository():
    """Attempt to repair Git repository corruption.
    
    Returns:
        bool: True if repair was successful, False otherwise
    """
    try:
        logging.info("Attempting to repair Git repository corruption...")
        
        # Step 1: Try git fsck to identify and repair issues
        logging.info("Running git fsck --full")
        fsck_result = subprocess.run(
            ["git", "fsck", "--full"], 
            cwd=REPO_PATH, 
            capture_output=True, 
            text=True, 
            timeout=120
        )
        
        if fsck_result.returncode == 0:
            logging.info("Git fsck completed successfully - no corruption detected")
        else:
            logging.warning(f"Git fsck found issues: {fsck_result.stderr}")
        
        # Step 2: Try to remove corrupted objects and re-fetch
        logging.info("Attempting to clean up corrupted objects...")
        
        # Find and remove empty/corrupted object files
        objects_dir = os.path.join(REPO_PATH, '.git', 'objects')
        if os.path.exists(objects_dir):
            # Remove empty object files
            for root, dirs, files in os.walk(objects_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        if os.path.getsize(file_path) == 0:
                            logging.info(f"Removing empty object file: {file_path}")
                            os.remove(file_path)
                    except OSError:
                        continue
        
        # Step 3: Try git gc with aggressive cleanup
        logging.info("Running git gc --aggressive --prune=now")
        gc_result = subprocess.run(
            ["git", "gc", "--aggressive", "--prune=now"], 
            cwd=REPO_PATH, 
            capture_output=True, 
            text=True, 
            timeout=300
        )
        
        if gc_result.returncode != 0:
            logging.warning(f"Git gc had issues: {gc_result.stderr}")
        
        # Step 4: Re-fetch all objects from remote
        logging.info("Re-fetching all objects from remote...")
        fetch_result = subprocess.run(
            ["git", "fetch", "--all", "--prune"], 
            cwd=REPO_PATH, 
            capture_output=True, 
            text=True, 
            timeout=120
        )
        
        if fetch_result.returncode != 0:
            logging.error(f"Failed to fetch after repair: {fetch_result.stderr}")
            
            # Step 5: Last resort - reset to remote HEAD
            logging.info("Attempting hard reset to remote HEAD...")
            try:
                # Get the default branch
                branch_result = subprocess.run(
                    ["git", "symbolic-ref", "refs/remotes/origin/HEAD"], 
                    cwd=REPO_PATH, 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                
                if branch_result.returncode == 0:
                    remote_head = branch_result.stdout.strip().replace('refs/remotes/origin/', '')
                else:
                    remote_head = "main"  # fallback to main
                
                # Reset to remote branch
                reset_result = subprocess.run(
                    ["git", "reset", "--hard", f"origin/{remote_head}"], 
                    cwd=REPO_PATH, 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                
                if reset_result.returncode == 0:
                    logging.info("Successfully reset to remote HEAD")
                    return True
                else:
                    logging.error(f"Hard reset failed: {reset_result.stderr}")
                    
            except Exception as e:
                logging.error(f"Hard reset attempt failed: {e}")
        else:
            logging.info("Successfully re-fetched objects from remote")
        
        # Step 6: Final verification with fsck
        logging.info("Running final git fsck verification...")
        final_fsck = subprocess.run(
            ["git", "fsck"], 
            cwd=REPO_PATH, 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        
        if final_fsck.returncode == 0:
            logging.info("Git repository repair completed successfully")
            return True
        else:
            logging.error(f"Repository still has issues after repair: {final_fsck.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logging.error("Git repository repair timed out")
        return False
    except Exception as e:
        logging.error(f"Error during Git repository repair: {e}", exc_info=True)
        return False

def is_network_error(combined_output):
    """Check if the git output indicates a network connectivity issue (not auth/access)."""
    if not combined_output:
        return False
    
    output_lower = combined_output.lower()
    
    # Check for genuine network issues
    has_network_error = any(keyword.lower() in output_lower for keyword in OFFLINE_KEYWORDS)
    
    # Check for authentication/permission errors (these are NOT network issues)
    has_auth_error = any(keyword.lower() in output_lower for keyword in ACCESS_ERROR_KEYWORDS)
    
    # If it's clearly an authentication/permission error, it's not a network issue
    if has_auth_error and not has_network_error:
        return False
    
    # If we detect network-related keywords, verify with actual connectivity test
    if has_network_error:
        return not test_network_connectivity()
    
    # For "fatal: unable to access" messages, check if it's network vs auth related
    if "fatal: unable to access" in output_lower:
        # If it mentions network-related issues, it's likely network
        if any(net_kw.lower() in output_lower for net_kw in OFFLINE_KEYWORDS):
            return not test_network_connectivity()
        # If it mentions auth issues, it's not network
        if any(auth_kw.lower() in output_lower for auth_kw in ACCESS_ERROR_KEYWORDS):
            return False
        # For ambiguous cases, test actual connectivity
        return not test_network_connectivity()
    
    # For other fatal errors, test connectivity to be sure
    if "fatal:" in output_lower and not has_auth_error:
        return not test_network_connectivity()
    
    return False

def safe_input(prompt, default='r'):
    """Safe input function that handles non-interactive environments.
    
    Args:
        prompt: The input prompt to display
        default: Default value to return if stdin is not available or interactive
    
    Returns:
        User input or default value
    """
    if not sys.stdin.isatty():
        # Non-interactive environment (e.g., systemd service)
        print(f"{prompt}(non-interactive, using default: {default})")
        return default
    
    try:
        return input(prompt)
    except EOFError:
        # Fallback in case of EOF error
        print(f"(EOF error, using default: {default})")
        return default

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
        
        # Network error buttons
        self.network_btn_frame = tk.Frame(self.container)
        self.retry_btn = tk.Button(self.network_btn_frame, text="Retry", fg="white", bg="green", width=15,
                                   command=self.retry_update)
        self.retry_btn.pack(side=tk.LEFT, padx=5)
        self.skip_btn = tk.Button(self.network_btn_frame, text="Skip Update", fg="white", bg="orange", width=15,
                                  command=self.skip_update)
        self.skip_btn.pack(side=tk.LEFT, padx=5)
        self.network_btn_frame.pack_forget()
        
        # Retry counter for network errors
        self.network_retry_count = 0
        self.max_network_retries = 3
        
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
        self.network_btn_frame.pack_forget()
        if not self.btn_frame.winfo_ismapped():
            self.btn_frame.pack(pady=8)

    def show_network_error(self, message="Network connectivity issue detected."):
        """Show network error UI with retry and skip options."""
        # Hide action buttons while showing network error
        if self.btn_frame.winfo_ismapped():
            self.btn_frame.pack_forget()
        
        # Hide conflict UI
        self.conflict_list_container.pack_forget()
        self.overwrite_btn.pack_forget()
        
        # Show network error message
        self.conflict_label.config(text=message)
        
        # Show retry/skip buttons
        self.network_btn_frame.pack(pady=10)
        self.root.update_idletasks()

    def hide_network_error(self):
        """Hide network error UI."""
        self.network_btn_frame.pack_forget()
        self.conflict_label.config(text="")
        if not self.btn_frame.winfo_ismapped():
            self.btn_frame.pack(pady=8)

    def retry_update(self):
        """Retry the update process with limits."""
        self.network_retry_count += 1
        
        if self.network_retry_count >= self.max_network_retries:
            self.set_status("❌ Maximum retries reached. Update failed.", progress=100)
            logging.error("GUI update failed after maximum network retries.")
            self.hide_network_error()
            self.close_after(5)
            return
            
        # Check network connectivity before retry
        if not test_network_connectivity():
            self.set_status("❌ No network connectivity. System is offline.", progress=100)
            self.show_network_error(f"No network connectivity detected.\nSystem appears to be offline.\n\nRetry attempts: {self.network_retry_count}/{self.max_network_retries}")
            logging.warning("GUI retry failed - no network connectivity.")
            return
            
        self.hide_network_error()
        self.set_status(f"Retrying update... (attempt {self.network_retry_count + 1}/{self.max_network_retries + 1})", progress=10)
        
        # Start the update process again in a new thread
        t = threading.Thread(target=update_repo, args=(self,), daemon=True)
        t.start()

    def skip_update(self):
        """Skip the update and close the GUI."""
        self.set_status("Update skipped due to network issue.", progress=100)
        logging.info("Update skipped by user due to network issue.")
        self.close_after(3)

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
        
        # Reset retry counter for new update attempt
        if not hasattr(gui, 'network_retry_count'):
            gui.network_retry_count = 0
            
        # Check network connectivity first
        gui.set_status("Checking network connectivity...", progress=5)
        if not test_network_connectivity():
            gui.set_status("❌ No network connectivity detected.", progress=50)
            gui.show_network_error("No network connectivity detected.\nSystem appears to be offline.\nPlease check your internet connection.")
            logging.warning("GUI update failed - no network connectivity.")
            return
        gui.set_status("Fetching updates...", progress=25)
        logging.info("Running: git fetch")
        
        # Try fetch with timeout and network error detection
        try:
            fetch_result = subprocess.run(["git", "fetch"], cwd=REPO_PATH, capture_output=True, text=True, timeout=60)
            logging.info(f"git fetch stdout: {fetch_result.stdout.strip()}")
            if fetch_result.stderr:
                logging.warning(f"git fetch stderr: {fetch_result.stderr.strip()}")
                
            # Check for network errors during fetch first
            combined_fetch = (fetch_result.stdout or '') + "\n" + (fetch_result.stderr or '')
            if is_network_error(combined_fetch):
                gui.set_status("Network connectivity issue detected during fetch.", progress=50)
                gui.show_network_error("Network connectivity issue detected during fetch.\nPlease check your internet connection and try again.")
                logging.error("Network connectivity issue detected during fetch.")
                return
            
            # Check for Git corruption errors during fetch
            elif is_git_corruption_error(combined_fetch):
                gui.set_status("Git corruption detected during fetch. Attempting repair...", progress=40)
                logging.warning("Git corruption detected during fetch. Attempting repair...")
                
                if repair_git_repository():
                    gui.set_status("Git corruption repaired. Retrying fetch...", progress=50)
                    logging.info("Git corruption repaired successfully. Retrying fetch...")
                    
                    # Retry the fetch after repair
                    try:
                        retry_fetch = subprocess.run(["git", "fetch"], cwd=REPO_PATH, capture_output=True, text=True, timeout=60)
                        if retry_fetch.returncode != 0:
                            logging.error(f"Fetch still failed after repair: {retry_fetch.stderr}")
                            gui.set_status("❌ Fetch failed even after corruption repair", progress=100)
                            return
                    except subprocess.TimeoutExpired:
                        gui.set_status("Timeout during fetch retry after repair.", progress=100)
                        logging.error("Timeout during fetch retry after corruption repair.")
                        return
                else:
                    gui.set_status("❌ Failed to repair Git corruption", progress=100)
                    gui.show_conflicts(message="Git repository corruption detected but repair failed. Manual intervention may be required. Check logs for details.")
                    logging.error("Failed to repair Git corruption during fetch.")
                    return
                
        except subprocess.TimeoutExpired:
            gui.set_status("Network timeout during fetch.", progress=50)
            gui.show_network_error("Network timeout occurred during fetch.\nPlease check your internet connection and try again.")
            logging.error("Network timeout during fetch.")
            return
            
        gui.set_status("Pulling latest changes...", progress=75)
        logging.info("Running: git pull")
        
        # Try pull with timeout and network error detection
        try:
            pull_result = subprocess.run(["git", "pull"], cwd=REPO_PATH, capture_output=True, text=True, timeout=120)
            logging.info(f"git pull stdout: {pull_result.stdout.strip()}")
            if pull_result.stderr:
                logging.warning(f"git pull stderr: {pull_result.stderr.strip()}")
                
            # Check for network errors during pull first
            combined_pull = (pull_result.stdout or '') + "\n" + (pull_result.stderr or '')
            if is_network_error(combined_pull):
                gui.set_status("Network connectivity issue detected during pull.", progress=75)
                gui.show_network_error("Network connectivity issue detected during pull.\nPlease check your internet connection and try again.")
                logging.error("Network connectivity issue detected during pull.")
                return
            
            # Check for Git corruption errors after network check
            elif is_git_corruption_error(combined_pull):
                gui.set_status("Git corruption detected. Attempting repair...", progress=80)
                logging.warning("Git corruption detected during pull. Attempting repair...")
                
                if repair_git_repository():
                    gui.set_status("Git corruption repaired. Retrying update...", progress=85)
                    logging.info("Git corruption repaired successfully. Retrying pull...")
                    
                    # Retry the pull after repair
                    try:
                        retry_pull = subprocess.run(["git", "pull"], cwd=REPO_PATH, capture_output=True, text=True, timeout=120)
                        if retry_pull.returncode == 0:
                            logging.info("Pull successful after corruption repair")
                            pull_result = retry_pull  # Use the successful result
                        else:
                            logging.error(f"Pull still failed after repair: {retry_pull.stderr}")
                            gui.set_status("❌ Pull failed even after corruption repair", progress=100)
                            gui.show_conflicts(message="Git corruption was repaired but pull still failed. Check logs for details.")
                            return
                    except subprocess.TimeoutExpired:
                        gui.set_status("Timeout during retry after repair.", progress=100)
                        logging.error("Timeout during retry after corruption repair.")
                        return
                else:
                    gui.set_status("❌ Failed to repair Git corruption", progress=100)
                    gui.show_conflicts(message="Git repository corruption detected but repair failed. Manual intervention may be required. Check logs for details.")
                    logging.error("Failed to repair Git corruption.")
                    return
                
        except subprocess.TimeoutExpired:
            gui.set_status("Network timeout during pull.", progress=75)
            gui.show_network_error("Network timeout occurred during pull.\nPlease check your internet connection and try again.")
            logging.error("Network timeout during pull.")
            return

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
    """Interactive headless updater with retry/overwrite options."""
    # Detect if we're in boot process (no real terminal available)
    is_boot_time = not (sys.stdin.isatty() and os.environ.get('TERM') and os.environ.get('USER'))
    
    if is_boot_time:
        # Boot-time mode: fast, non-interactive, no retries
        return headless_update_boot()
    
    # Normal interactive headless mode

    print("🔄 Checking for repository updates...")
    
    try:
        logging.info("Starting update process (headless mode).")
        
        # Check network connectivity first to avoid endless retries
        if not test_network_connectivity():
            print("❌ No network - update skipped")
            logging.warning("Update skipped - no network connectivity.")
            return
        
        # Fetch with retry limit
        max_fetch_retries = 3
        fetch_attempts = 0
        
        while fetch_attempts < max_fetch_retries:
            fetch_attempts += 1
            
            try:
                fetch_result = subprocess.run(["git", "fetch"], cwd=REPO_PATH, capture_output=True, text=True, timeout=30)
                combined_fetch = (fetch_result.stdout or '') + "\n" + (fetch_result.stderr or '')
                
                # Check for network errors first
                if is_network_error(combined_fetch):
                    if fetch_attempts >= max_fetch_retries:
                        print("❌ Network error - update failed")
                        logging.error("Fetch failed after maximum retries due to network issues.")
                        return
                    
                    # Quick network re-check before retry
                    if not test_network_connectivity():
                        print("❌ Network lost - update skipped")
                        logging.warning("Network connectivity lost during fetch retries.")
                        return
                    
                    # Auto-retry network errors without user prompt
                    print(f"Network error - retrying... ({max_fetch_retries - fetch_attempts} attempts left)")
                    import time
                    time.sleep(2)  # Brief delay before retry
                    continue
                
                # Check for Git corruption after network check
                elif is_git_corruption_error(combined_fetch):
                    print("⚠️  Git corruption detected during fetch - attempting repair...")
                    logging.warning("Git corruption detected during fetch. Attempting repair...")
                    
                    if repair_git_repository():
                        print("✅ Git corruption repaired - retrying fetch...")
                        logging.info("Git corruption repaired successfully. Retrying fetch...")
                        
                        # Retry the fetch after repair
                        try:
                            retry_fetch = subprocess.run(["git", "fetch"], cwd=REPO_PATH, capture_output=True, text=True, timeout=30)
                            if retry_fetch.returncode == 0:
                                logging.info("Fetch successful after corruption repair")
                                break  # Fetch successful after repair
                            else:
                                logging.error(f"Fetch still failed after repair: {retry_fetch.stderr}")
                                print("❌ Fetch failed even after corruption repair")
                                return
                        except subprocess.TimeoutExpired:
                            print("❌ Timeout during fetch retry after repair")
                            logging.error("Timeout during fetch retry after corruption repair.")
                            return
                    else:
                        print("❌ Failed to repair Git corruption")
                        logging.error("Failed to repair Git corruption during fetch.")
                        return
                else:
                    break  # Fetch successful
                    
            except subprocess.TimeoutExpired:
                if fetch_attempts >= max_fetch_retries:
                    print("❌ Timeout - update failed")
                    logging.error("Fetch failed after maximum retries due to timeouts.")
                    return
                    
                # Auto-retry timeout errors
                print(f"Timeout - retrying... ({max_fetch_retries - fetch_attempts} attempts left)")
                import time
                time.sleep(2)  # Brief delay before retry
                continue
        
        # Pull with conflict handling and retry limits
        max_pull_retries = 3
        pull_attempts = 0
        
        while pull_attempts < max_pull_retries:
            pull_attempts += 1
            logging.info("Running: git pull")
            
            try:
                result = subprocess.run(["git", "pull"], cwd=REPO_PATH, capture_output=True, text=True, timeout=60)
                logging.info(f"git pull output: {result.stdout.strip()}")
                if result.stderr:
                    logging.warning(f"git pull stderr: {result.stderr.strip()}")
                
                combined = (result.stdout or '') + "\n" + (result.stderr or '')
                
                # FIRST: Check for network errors (highest priority)
                if is_network_error(combined):
                    if pull_attempts >= max_pull_retries:
                        print("❌ Network error - update failed")
                        logging.error("Pull failed after maximum retries due to network issues.")
                        return
                        
                    # Quick network re-check before retry
                    if not test_network_connectivity():
                        print("❌ Network lost - update skipped")
                        logging.warning("Network connectivity lost during pull retries.")
                        return
                    
                    # Auto-retry network errors without user prompt
                    print(f"Network error - retrying... ({max_pull_retries - pull_attempts} attempts left)")
                    import time
                    time.sleep(3)  # Longer delay for pull retries
                    continue
                
                # SECOND: Check for Git corruption errors
                elif is_git_corruption_error(combined):
                    print("⚠️  Git corruption detected - attempting repair...")
                    logging.warning("Git corruption detected during pull. Attempting repair...")
                    
                    if repair_git_repository():
                        print("✅ Git corruption repaired - retrying update...")
                        logging.info("Git corruption repaired successfully. Retrying pull...")
                        
                        # Retry the pull after repair
                        try:
                            retry_result = subprocess.run(["git", "pull"], cwd=REPO_PATH, capture_output=True, text=True, timeout=60)
                            if retry_result.returncode == 0:
                                logging.info("Pull successful after corruption repair")
                                result = retry_result  # Use the successful result
                                # Continue with success handling below
                            else:
                                logging.error(f"Pull still failed after repair: {retry_result.stderr}")
                                print("❌ Pull failed even after corruption repair")
                                return
                        except subprocess.TimeoutExpired:
                            print("❌ Timeout during retry after repair")
                            logging.error("Timeout during retry after corruption repair.")
                            return
                    else:
                        print("❌ Failed to repair Git corruption")
                        logging.error("Failed to repair Git corruption.")
                        return
                
                # THIRD: Check if git command failed but it's not a network issue
                if result.returncode != 0:
                    # Additional network check for generic failures
                    if not test_network_connectivity():
                        print("❌ Network connectivity lost - update skipped")
                        logging.warning("Git command failed and network connectivity lost.")
                        return
                        
                    # Check for specific conflict-related errors
                    conflict_keywords = [
                        'would be overwritten by merge',
                        'Please commit your changes or stash them before you merge',
                        'Aborting',
                        'divergent branches',
                        'Need to specify how to reconcile divergent branches'
                    ]
                    
                    has_conflict = any(kw in (result.stderr or '') for kw in conflict_keywords)
                    
                    if has_conflict:
                        conflict_files = get_conflict_files()
                        print("⚠️  Local changes conflict with update")
                        if conflict_files:
                            print(f"Files: {', '.join(conflict_files[:3])}")
                            if len(conflict_files) > 3:
                                print(f"... and {len(conflict_files) - 3} more")
                        
                        choice = input("Fix: [o]verwrite local changes / [s]kip update? ").strip().lower() or 's'
                        if choice.startswith('o'):
                            if _cli_overwrite_flow():
                                print("✅ Repository updated (local changes overwritten)")
                                logging.info("Repo updated successfully via overwrite.")
                                return
                            else:
                                continue
                        else:
                            print("Update skipped")
                            return
                    else:
                        # Generic git error - could be network, so retry
                        if pull_attempts >= max_pull_retries:
                            print(f"❌ Git error - update failed: {result.stderr.strip()}")
                            logging.error(f"Pull failed after maximum retries: {result.stderr.strip()}")
                            return
                            
                        # Auto-retry generic git errors (often network-related)
                        print(f"Git error - retrying... ({max_pull_retries - pull_attempts} attempts left)")
                        import time
                        time.sleep(3)
                        continue
                else:
                    # Success case
                    if "Already up to date" in result.stdout:
                        print("✅ Repository up to date")
                        logging.info("Repo is already up to date.")
                    else:
                        print("✅ Repository updated successfully!")
                        logging.info("Repo updated successfully.")
                    return
                    
            except subprocess.TimeoutExpired:
                if pull_attempts >= max_pull_retries:
                    print("❌ Timeout - update failed")
                    logging.error("Pull failed after maximum retries due to timeouts.")
                    return
                    
                # Auto-retry timeout errors
                print(f"Timeout - retrying... ({max_pull_retries - pull_attempts} attempts left)")
                import time
                time.sleep(3)
                continue
                    
    except Exception as e:
        logging.error(f"Error during update: {e}", exc_info=True)
        print(f"❌ Update failed: {e}")

def _cli_overwrite_flow():
    """Handle the overwrite flow for CLI mode."""
    try:
        # Reset to remote state
        subprocess.run(['git', 'reset', '--hard', 'HEAD'], cwd=REPO_PATH, check=True)
        subprocess.run(['git', 'clean', '-fd'], cwd=REPO_PATH, check=True)
        subprocess.run(['git', 'pull'], cwd=REPO_PATH, check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Overwrite failed: {e}")
        logging.error(f"Overwrite failed: {e}")
        return False

def is_gui_available():
    return os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")

def headless_update_boot():
    """Boot-time update mode: fast, non-interactive, no blocking."""
    try:
        logging.info("Starting update process (boot-time mode).")
        
        # Quick network check with very short timeout
        try:
            subprocess.run(['ping', '-c', '1', '-W', '1', '8.8.8.8'], 
                         capture_output=True, timeout=2)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            logging.info("No network during boot - skipping update.")
            return
        
        # Fast fetch with short timeout
        try:
            subprocess.run(["git", "fetch"], cwd=REPO_PATH, capture_output=True, 
                         text=True, timeout=10)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            logging.info("Fetch failed during boot - skipping update.")
            return
            
        # Fast pull with short timeout  
        try:
            result = subprocess.run(["git", "pull"], cwd=REPO_PATH, capture_output=True, 
                                  text=True, timeout=10)
            if "Already up to date" in result.stdout:
                logging.info("Repo is already up to date.")
            elif result.returncode == 0:
                logging.info("Repo updated successfully during boot.")
            else:
                logging.info("Update issues during boot - continuing boot process.")
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            logging.info("Pull failed during boot - continuing boot process.")
            
    except Exception as e:
        logging.info(f"Boot update failed: {e} - continuing boot process.")

def headless_update_service():
    """Non-interactive service mode for systemd."""
    try:
        logging.info("Starting update process (service mode).")
        subprocess.run(["git", "fetch"], cwd=REPO_PATH, check=True, timeout=60)
        logging.info("Running: git pull")
        result = subprocess.run(["git", "pull"], cwd=REPO_PATH, capture_output=True, text=True, timeout=120)
        logging.info(f"git pull output: {result.stdout.strip()}")
        
        if "Already up to date" in result.stdout:
            logging.info("Repo is already up to date.")
        elif result.returncode == 0:
            logging.info("Repo updated successfully.")
        else:
            logging.warning(f"Update may have issues: {result.stderr.strip()}")
            
    except subprocess.TimeoutExpired:
        logging.error("Service update timed out.")
    except Exception as e:
        logging.error(f"Error during service update: {e}", exc_info=True)

def main():
    parser = argparse.ArgumentParser(description='MobileRobot Repo Updater')
    parser.add_argument('--service', action='store_true', help='Run non-interactive service mode')
    parser.add_argument('--headless', action='store_true', help='Run interactive headless mode')
    args = parser.parse_args()

    if args.service:
        headless_update_service()
        return
    elif args.headless:
        headless_update()
        return

    # Default behavior: GUI when available, otherwise headless
    if is_gui_available():
        gui = UpdaterGUI()
        t = threading.Thread(target=update_repo, args=(gui,), daemon=True)
        t.start()
        gui.run()
    else:
        headless_update()

if __name__ == "__main__":
    main()
