import os
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import schedule

# 從雲端環境變數安全讀取網址
# 這是固定不變的前半段
part1 = "https://slack.com"

# 請把您剛剛複製的最新網址中，第三個斜線後面的最後那一截英文字母填在這裡
part2 = "/AK1Me2H309BlMcGmyBbhTFxD"

SLACK_WEBHOOK_URL = part1 + part2


def generate_and_send_french():
    # 確保有網址才執行，避免 None 導致崩潰
    if not SLACK_WEBHOOK_URL:
        print("【錯誤】找不到 Slack Webhook 網址，請檢查 Render 的 Environment 設定！")
        return

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

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json={"blocks": blocks})
        print(f"【系統】嘗試發送至 Slack，回應碼: {response.status_code}")
    except Exception as e:
        print(f"【系統】發送失敗，原因: {e}")


# --- 🛠️ 專為 Render 免費版設計的網頁伺服器 ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    # 補上 HEAD 方法，徹底解決 Render 的 501 錯誤
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"【網頁】偽裝伺服器已啟動，監聽 Port: {port}")
    server.serve_forever()


# ---------------------------------------------------

# 設定排程：每 1 分鐘執行一次測試
schedule.every(1).minutes.do(generate_and_send_french)

if __name__ == "__main__":
    # 步驟一：【最優先】立刻啟動網頁伺服器執行緒，秒回 Render 的健康檢查
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # 步驟二：讓雲端緩衝 5 秒，確保環境變數完全載入
    time.sleep(5)

    # 步驟三：首次主動執行一次
    generate_and_send_french()

    # 步驟四：進入排程無窮迴圈
    while True:
        schedule.run_pending()
        time.sleep(1)
