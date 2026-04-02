import requests
import os
import glob
from dotenv import load_dotenv

# .env 로드
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "agents", "veronica_bot", ".env"))
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USER_ID = os.getenv("TELEGRAM_USER_ID")

def send_file(file_path, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    files = {'document': open(file_path, 'rb')}
    payload = {'chat_id': USER_ID, 'caption': caption}
    
    print(f"🚀 Sending {file_path} to Telegram...")
    response = requests.post(url, data=payload, files=files)
    if response.status_code == 200:
        print("✅ Successfully sent to Telegram!")
    else:
        print(f"❌ Failed: {response.text}")

if __name__ == "__main__":
    # Tauri 빌드 결과물 경로 (Windows MSI/EXE)
    # 보통 src-tauri/target/release/bundle/msi/ 또는 setup.exe 등
    build_pattern = "src-tauri/target/release/bundle/exe/*.exe"
    build_files = glob.glob(build_pattern)
    
    if build_files:
        latest_file = max(build_files, key=os.path.getctime)
        send_file(latest_file, "🎉 FranRename 윈도우용 빌드가 완료되었습니다!")
    else:
        print("⚠️ No build files found. Please run 'npm run tauri build' first.")
