import os

def get_logo_path():
    return os.path.expanduser("~/Desktop/VIDLAB PROJECT/final_data/script/ASSETS/VIDLAB MAIN LOGO.png")

DROPBOX_FOOTAGE_PATH = os.path.expanduser("~/Library/CloudStorage/Dropbox/VIDLAB MARKETING/TELEGRAM BOT FOR SA SEND IN FOOTAGE/Footage (M CODE)")

def save_video_file(file_obj, m_code):
    os.makedirs(DROPBOX_FOOTAGE_PATH, exist_ok=True)
    file_path = os.path.join(DROPBOX_FOOTAGE_PATH, f"{m_code}.mp4")
    # 假设file_obj为telegram的get_file()对象
    file_obj.download(custom_path=file_path)
    return file_path
