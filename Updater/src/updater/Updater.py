import os
import requests
import shutil
import zipfile
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
import re
import winreg
from datetime import datetime
import sys
import pytz
from tzlocal import get_localzone

# Configuration
GITHUB_REPO_API_URL = "https://api.github.com/repos/cycleapple/DeadlockTC/commits/main"
GITHUB_REPO_ZIP_URL = "https://github.com/cycleapple/DeadlockTC/archive/refs/heads/main.zip"
STEAM_APP_ID = 1422450
LAST_UPDATE_FILE = "last_update_time.txt"

def find_steam_install_path():
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Valve\Steam")
        install_path, _ = winreg.QueryValueEx(reg_key, "InstallPath")
        winreg.CloseKey(reg_key)
        return install_path
    except FileNotFoundError:
        messagebox.showerror("錯誤", "在註冊表中找不到Steam安裝位置。")
        return None
    except Exception as e:
        messagebox.showerror("錯誤", f"訪問註冊表時發生錯誤: {e}")
        return None

def find_game_directory_by_appid(steam_app_id):
    steam_install_path = find_steam_install_path()
    if not steam_install_path:
        return None

    game_path = os.path.join(steam_install_path, "steamapps", "common", "Deadlock")
    manifest_path = os.path.join(steam_install_path, "steamapps", f"appmanifest_{steam_app_id}.acf")

    if os.path.exists(game_path) and os.path.exists(manifest_path):
        return game_path

    library_folders_vdf = os.path.join(steam_install_path, "steamapps", "libraryfolders.vdf")
    if os.path.exists(library_folders_vdf):
        with open(library_folders_vdf, 'r') as file:
            for line in file:
                match = re.search(r'"path"\s+"([^"]+)"', line)
                if match:
                    library_path = match.group(1).replace('\\\\', '\\')
                    game_path = os.path.join(library_path, "steamapps", "common", "Deadlock")
                    manifest_path = os.path.join(library_path, "steamapps", f"appmanifest_{steam_app_id}.acf")

                    if os.path.exists(game_path) and os.path.exists(manifest_path):
                        return game_path

    return None

def download_and_extract_zip(url, extract_to):
    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            zip_path = os.path.join(tmpdirname, "repo.zip")

            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(zip_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdirname)

            for root, dirs, files in os.walk(tmpdirname):
                if "game" in dirs:
                    extracted_game_folder = os.path.join(root, "game")
                    break

            if os.path.exists(extracted_game_folder):
                for root, dirs, files in os.walk(extracted_game_folder):
                    relative_path = os.path.relpath(root, extracted_game_folder)
                    target_folder = os.path.join(extract_to, relative_path)

                    if not os.path.exists(target_folder):
                        os.makedirs(target_folder)

                    for file in files:
                        src_file = os.path.join(root, file)
                        dest_file = os.path.join(target_folder, file)

                        shutil.copy2(src_file, dest_file)
                        print(f"Replaced: {dest_file}")

                # Save the current time as the last update time
                current_time = datetime.now().strftime("%Y/%m/%d %H:%M")
                with open(LAST_UPDATE_FILE, 'w') as f:
                    f.write(current_time)

                last_update_time.set(current_time)
                last_update_label.config(text=f"上一次安裝/更新時間: {last_update_time.get()}")
                update_version_status()

                messagebox.showinfo("成功", "'game' 資料夾中的檔案已成功更新。")
            else:
                messagebox.showerror("錯誤", "在解壓縮的檔案中找不到 'game' 資料夾。")

    except Exception as e:
        messagebox.showerror("錯誤", f"發生錯誤: {e}")

def fetch_latest_commit_time():
    try:
        response = requests.get(GITHUB_REPO_API_URL)
        response.raise_for_status()
        commit_data = response.json()
        commit_time_utc = datetime.strptime(commit_data['commit']['committer']['date'], "%Y-%m-%dT%H:%M:%SZ")

        # Convert the commit time to the local timezone
        local_tz = get_localzone()
        commit_time_local = commit_time_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)
        return commit_time_local.strftime("%Y/%m/%d %H:%M")
    except Exception as e:
        messagebox.showerror("錯誤", f"無法獲取最新版本更新時間: {e}")
        return "無法獲取"

def read_last_update_time():
    if os.path.exists(LAST_UPDATE_FILE):
        with open(LAST_UPDATE_FILE, 'r') as f:
            return f.read().strip()
    else:
        return "尚未使用過更新器"

def update_version_status():
    last_update = last_update_time.get()
    latest_commit = latest_commit_time.get()

    if last_update == "尚未使用過更新器":
        version_status.set("版本狀態: 尚未使用過更新器")
        version_status_label.config(fg="black")
    elif latest_commit != "無法獲取":
        last_update_dt = datetime.strptime(last_update, "%Y/%m/%d %H:%M")
        latest_commit_dt = datetime.strptime(latest_commit, "%Y/%m/%d %H:%M")

        if last_update_dt < latest_commit_dt:
            version_status.set("版本狀態: 漢化已有新版本建議更新")
            version_status_label.config(fg="red")
        else:
            version_status.set("版本狀態: 已經安裝最新版本漢化")
            version_status_label.config(fg="green")
    else:
        version_status.set("版本狀態: 無法獲取最新版本信息")
        version_status_label.config(fg="black")

def check_update():
    latest_commit_time.set(fetch_latest_commit_time())
    last_update_time.set(read_last_update_time())
    last_update_label.config(text=f"上一次安裝/更新時間: {last_update_time.get()}")
    latest_commit_label.config(text=f"最新版本更新時間: {latest_commit_time.get()}")
    update_version_status()

    # Show success message
    messagebox.showinfo("成功", "更新檢查完成。")

def select_directory():
    directory = filedialog.askdirectory(title="選擇遊戲安裝路徑")
    if directory:
        target_directory.set(directory)

def run_updater():
    if not target_directory.get():
        messagebox.showwarning("警告", "請選擇遊戲安裝路徑。")
        return

    game_dir = os.path.join(target_directory.get(), "game")
    download_and_extract_zip(GITHUB_REPO_ZIP_URL, game_dir)
    last_update_time.set(datetime.now().strftime("%Y/%m/%d %H:%M"))
    last_update_label.config(text=f"上一次安裝/更新時間: {last_update_time.get()}")
    update_version_status()

def auto_detect_game_directory():
    game_dir = find_game_directory_by_appid(STEAM_APP_ID)
    if game_dir:
        target_directory.set(game_dir)
        messagebox.showinfo("偵測完成", f"偵測到的遊戲目錄: {game_dir}")
    else:
        messagebox.showwarning("未找到", "無法自動偵測遊戲路徑。請手動選擇。")

# GUI Setup
root = tk.Tk()
root.title("Deadlock繁體漢化更新器")

# Determine if the script is running as a bundle
if getattr(sys, 'frozen', False):
    script_dir = sys._MEIPASS
else:
    script_dir = os.path.dirname(__file__)

icon_path = os.path.join(script_dir, 'icon.ico')

# Set the custom icon
root.iconbitmap(icon_path)

target_directory = tk.StringVar()
last_update_time = tk.StringVar(value=read_last_update_time())
latest_commit_time = tk.StringVar(value=fetch_latest_commit_time())
version_status = tk.StringVar()

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

label = tk.Label(frame, text="選擇您的遊戲安裝路徑:")
label.grid(row=0, column=0, padx=5, pady=5)

entry = tk.Entry(frame, textvariable=target_directory, width=50)
entry.grid(row=1, column=0, padx=5, pady=5)

browse_button = tk.Button(frame, text="瀏覽...", command=select_directory)
browse_button.grid(row=1, column=1, padx=5, pady=5)

detect_button = tk.Button(frame, text="自動偵測路徑", command=auto_detect_game_directory)
detect_button.grid(row=2, column=0, columnspan=2, pady=5)

update_button = tk.Button(frame, text="安裝/更新漢化", command=run_updater)
update_button.grid(row=3, column=0, columnspan=2, pady=10)

check_update_button = tk.Button(frame, text="檢查更新", command=check_update)
check_update_button.grid(row=4, column=0, columnspan=2, pady=10)

last_update_label = tk.Label(frame, text=f"上一次安裝/更新時間: {last_update_time.get()}", anchor="w", justify=tk.LEFT)
last_update_label.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="w")

latest_commit_label = tk.Label(frame, text=f"最新版本更新時間: {latest_commit_time.get()}", anchor="w", justify=tk.LEFT)
latest_commit_label.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="w")

version_status_label = tk.Label(frame, textvariable=version_status, anchor="w", justify=tk.LEFT)
version_status_label.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="w")

# Execute initial version check and update status on launch
check_update()

root.mainloop()
