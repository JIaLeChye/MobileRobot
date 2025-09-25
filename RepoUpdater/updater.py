from pathlib import Path
import os
import subprocess
import importlib.util
import sys
import logging
from packaging import version
import platform


# === CONFIG ===
REPO_REL_PATH = Path("Desktop/MobileRobot")
VERSION_FILE = "version.py"
BRANCH = "master"
REMOTE = "origin"
REPO_URL = "https://github.com/JiaLeChye/MobileRobot.git"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/mcupdater.log')
    ]
)


def get_home_dir():
    """Identify user type"""
    if platform.system() == "Windows":
        return Path.home()
    
    # Unix/Linux systems
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user:
        import pwd
        return Path(pwd.getpwnam(sudo_user).pw_dir)
    return Path.home()


# === PATHS ===
HOME_DIR = get_home_dir()
REPO_PATH = HOME_DIR / REPO_REL_PATH
LOCAL_VERSION_FILE = REPO_PATH / VERSION_FILE


# === HELPERS ===
def clone_or_update_repo():
    try:
        if not REPO_PATH.exists():
            logging.info("📥 Cloning repository...")
            subprocess.run(
                ["git", "clone", "-b", BRANCH, REPO_URL, str(REPO_PATH)],
                check=True
            )
        elif (REPO_PATH / ".git").exists():
            logging.info("🔄 Repo already exists, pulling latest changes...")
            subprocess.run(["git", "fetch"], cwd=REPO_PATH, check=True)
            subprocess.run(["git", "pull", REMOTE, BRANCH], cwd=REPO_PATH, check=True)
        else:
            logging.error(f"⚠️ Path {REPO_PATH} exists but is not a Git repo. Please clean it manually.")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Error cloning/updating repository: {e}")
        raise


def get_local_version():
    try:
        if not LOCAL_VERSION_FILE.exists():
            logging.warning(f"Local version file not found: {LOCAL_VERSION_FILE}")
            return None
        spec = importlib.util.spec_from_file_location("version", str(LOCAL_VERSION_FILE))
        if spec is None or spec.loader is None:
            logging.error("Failed to load version module spec")
            return None
        version_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(version_module)
        return getattr(version_module, "__version__", None)
    except Exception as e:
        logging.error(f"Error getting local version: {e}")
        return None


def get_remote_version():
    try:
        subprocess.run(["git", "fetch", REMOTE], cwd=REPO_PATH, check=True)
        output = subprocess.check_output(
            ["git", "show", f"{REMOTE}/{BRANCH}:{VERSION_FILE}"],
            cwd=REPO_PATH
        ).decode()
        context = {}
        exec(output, context)
        return context.get("__version__")
    except Exception as e:
        logging.error(f"Error getting remote version: {e}")
        return None


def update_repo():
    try:
        logging.info("Pulling latest changes...")
        subprocess.run(["git", "pull", REMOTE, BRANCH], cwd=REPO_PATH, check=True)
        logging.info("Running setup.sh...")
        subprocess.run(["./setup.sh"], cwd=REPO_PATH, check=True)
        logging.info("Repository update completed successfully")
    except Exception as e:
        logging.error(f"Error updating repository: {e}")
        raise


# === MAIN ===
def main():
    if not HOME_DIR:
        logging.error("❌ Unable to retrieve Home Directory")
        sys.exit(1)
    
    logging.info(f"🏠 Home Directory: {HOME_DIR}")
    logging.info(f"📂 Repo Path: {REPO_PATH}")
    logging.info(f"📄 Version File: {LOCAL_VERSION_FILE}")

    local_ver = None
    remote_ver = None
    
    try:
        # Clone or update repository
        clone_or_update_repo()

        # Get version information
        local_ver = get_local_version()
        remote_ver = get_remote_version()

        logging.info(f"📦 Local version:  {local_ver}")
        logging.info(f"🌐 Remote version: {remote_ver}")

        # Compare versions and update if needed
        should_update = False
        
        if local_ver and remote_ver:
            try:
                # Try semantic version comparison
                local_parsed = version.parse(local_ver)
                remote_parsed = version.parse(remote_ver)
                
                if remote_parsed > local_parsed:
                    logging.info(f"🚀 Updating from {local_ver} to {remote_ver}...")
                    should_update = True
                else:
                    logging.info("✅ Already up to date.")
            except Exception as version_error:
                logging.warning(f"Version parsing failed: {version_error}, using string comparison")
                if local_ver != remote_ver:
                    logging.info(f"🚀 Versions differ: {local_ver} != {remote_ver}, updating...")
                    should_update = True
                else:
                    logging.info("✅ Already up to date.")
        elif not local_ver and remote_ver:
            logging.info(f"🚀 No local version found, updating to {remote_ver}...")
            should_update = True
        else:
            logging.warning("Unable to determine version information")
            
        # Perform update if needed
        if should_update:
            update_repo()
            logging.info(f"✅ Update complete: now at version {remote_ver}")
            
    except Exception as e:
        logging.error(f"Fatal error during execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
