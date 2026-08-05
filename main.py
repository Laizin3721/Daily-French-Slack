import os
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import schedule

SLACK_WEBHOOK_URL = "你的_SLACK_WEBHOOK_URL"


def generate_and_send_french():
    sample_data = {
        "sentences": [
            {
                "french": "J'ai trop le seum pour l'équipe hier soir, ils ont foiré le match !",
                "chinese": "昨晚那場比賽搞砸了，我現在整個人鬱卒到極點！",
                "slang": "• *Avoir le seum*：極度鬱卒、不爽。\n• *Foirer*：搞砸了、失敗。",
            }
        ]
    }

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🇫🇷 每日法語時事流行語 ⚽",
                "emoji": True,
            },
        },
        {"type": "divider"},
    ]

    for idx, item in enumerate(sample_data["sentences"], 1):
        blocks.extend(
            [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{idx}. {item['french']}*",
                    },
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"💡 *中文：* {item['chinese']}\n📚 *解析：*\n{item['slang']}",
                        }
                    ],
                },
                {"type": "divider"},
            ]
        )

    requests.post(SLACK_WEBHOOK_URL, json={"blocks": blocks})
    print("法語推播成功！")


# --- 🛠️ 專為 Render 免費版設計的偽裝網頁伺服器 ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")


def run_web_server():
    # 自動讀取 Render 提供給免費 Web Service 的 Port 號碼
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"偽裝網頁伺服器已啟動，監聽 Port: {port}")
    server.serve_forever()


# ---------------------------------------------------

# 設定排程：每天台灣時間早上 08:30 執行（00:30 UTC）
schedule.every().day.at("00:30").do(generate_and_send_french)

if __name__ == "__main__":
    # 1. 先跑一次測試，確認 Slack 有收到
    generate_and_send_french()

    # 2. 開啟另一個背景執行緒，常駐啟動網頁通訊埠（解決 Render Port 錯誤）
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # 3. 保持主程式在背景常駐，等待每天定時排程
    while True:
        schedule.run_pending()
        time.sleep(60)
