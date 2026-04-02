import os
import requests
import sys

def send_log():
    token = os.environ.get('TOKEN')
    user_id = os.environ.get('USER_ID')
    log_path = 'tauri_build_error.log'
    
    if not os.path.exists(log_path):
        print("Log file not found.")
        return

    url = f"https://api.telegram.org/bot{token}/sendDocument"
    
    with open(log_path, 'rb') as f:
        files = {'document': f}
        data = {'chat_id': user_id, 'caption': '❌ 빌드 에러 로그가 도착했습니다! (V21.0)'}
        res = requests.post(url, files=files, data=data)
        print(res.json())

if __name__ == "__main__":
    send_log()
