import os
import sys
import requests
import time
import signal
import subprocess

# Constants
FILES = {
    "useful_files/hamsterkombat.io-telegram-web-app.php": "https://raw.githubusercontent.com/masterking32/MasterHamsterKombatBot/main/useful_files/hamsterkombat.io-telegram-web-app.php",
    "useful_files/hamsterkombat.js": "https://raw.githubusercontent.com/masterking32/MasterHamsterKombatBot/main/useful_files/hamsterkombat.js",
    "useful_files/user-agents.md": "https://raw.githubusercontent.com/masterking32/MasterHamsterKombatBot/main/useful_files/user-agents.md",
    ".gitignore": "https://raw.githubusercontent.com/masterking32/MasterHamsterKombatBot/main/.gitignore",
    "README.MD": "https://raw.githubusercontent.com/masterking32/MasterHamsterKombatBot/main/README.MD",
    "config.py.example": "https://raw.githubusercontent.com/masterking32/MasterHamsterKombatBot/main/config.py.example",
    "main.py": "https://raw.githubusercontent.com/masterking32/MasterHamsterKombatBot/main/main.py",
    "promogames.py": "https://raw.githubusercontent.com/masterking32/MasterHamsterKombatBot/main/promogames.py",
    "utilities.py": "https://raw.githubusercontent.com/masterking32/MasterHamsterKombatBot/main/utilities.py",
    "warna.py": "https://raw.githubusercontent.com/masterking32/MasterHamsterKombatBot/main/warna.py",
    "banner.py": "https://raw.githubusercontent.com/masterking32/MasterHamsterKombatBot/main/banner.py"
}
CHECK_DELAY = 500  # Delay in seconds between each update check cycle
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # Current directory of the updater script
MAIN_SCRIPT_PATH = os.path.join(CURRENT_DIR, 'main.py')  # Full path to main.py

def get_local_file_contents(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            contents = file.read()
        return contents
    except FileNotFoundError:
        print(f"File {file_path} not found. It will be downloaded.")
        return None
    except UnicodeDecodeError as e:
        print(f"Error reading local file {file_path}: {e}")
        return None
    except Exception as e:
        print(f"General error reading local file {file_path}: {e}")
        return None

def get_github_file_contents(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Error fetching file from GitHub: {url} - Status Code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching file from GitHub: {e}")
        return None

def check_for_updates():
    updates_needed = []
    for local_file, github_url in FILES.items():
        local_contents = get_local_file_contents(local_file)
        github_contents = get_github_file_contents(github_url)
        if local_contents is None:  # If the file is missing or an error occurred, download it
            updates_needed.append(local_file)
            continue
        if github_contents is None:
            continue  # Skip this file if there's an error fetching it from GitHub
        if local_contents != github_contents:
            updates_needed.append(local_file)
            print(f"Update needed for {local_file}")
        else:
            print(f"No update needed for {local_file}")
    return updates_needed

def download_update(file_name, github_url):
    github_contents = get_github_file_contents(github_url)
    if github_contents is None:
        return False
    try:
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(github_contents)
        print(f"Successfully updated {file_name}")
        return True
    except UnicodeEncodeError as e:
        print(f"Error writing to file {file_name}: {e}")
        return False
    except Exception as e:
        print(f"General error writing to file {file_name}: {e}")
        return False

def close_main_process():
    try:
        output = subprocess.check_output(["pgrep", "-f", f"python.*{MAIN_SCRIPT_PATH}"], universal_newlines=True)
        pids = [int(pid) for pid in output.split()]
        for pid in pids:
            os.kill(pid, signal.SIGTERM)
            print(f"Sent SIGTERM to process {pid}")
        
        # Wait for processes to terminate
        for _ in range(5):  # Try up to 5 times
            if not pids:
                break
            time.sleep(1)
            pids = [pid for pid in pids if os.path.exists(f"/proc/{pid}")]
        
        # Force kill any remaining processes
        for pid in pids:
            os.kill(pid, signal.SIGKILL)
            print(f"Sent SIGKILL to process {pid}")
    except subprocess.CalledProcessError:
        print("No matching process found.")
    except Exception as e:
        print(f"Error closing main process: {e}")

def reopen_main():
    try:
        print("Reopening main.py...")
        subprocess.Popen(["python3", MAIN_SCRIPT_PATH], start_new_session=True)
    except Exception as e:
        print(f"Error reopening main.py: {e}")

def update_check():
    updates_needed = check_for_updates()
    if updates_needed:
        close_main_process()  # Attempt to close main.py process if it's running
        all_updates_successful = True
        for file_name in updates_needed:
            github_url = FILES[file_name]
            if not download_update(file_name, github_url):
                all_updates_successful = False
        if all_updates_successful:
            print("All updates downloaded.")
            time.sleep(2)  # Add a delay to ensure old process has completely terminated
            reopen_main()  # Always reopen main.py after updates
        else:
            print("Some updates failed to download.")
    else:
        print("No updates available.")

# Main loop to continuously check for updates
def main_loop():
    while True:
        update_check()
        print(f"Waiting {CHECK_DELAY} seconds before next check...")
        time.sleep(CHECK_DELAY)  # Wait before checking again

# Start the main loop
if __name__ == "__main__":
    main_loop()
