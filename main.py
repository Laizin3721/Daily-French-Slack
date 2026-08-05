import json
import time
import requests
import schedule

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"


def generate_and_send_french():
    # 這是先前的大模型生成與發送 Slack 邏輯
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


# 設定每天早上 08:30 執行（注意：雲端伺服器預設通常是 UTC 時間，00:30 UTC = 08:30 台灣時間）
schedule.every().day.at("00:30").do(generate_and_send_french)

if __name__ == "__main__":
    # 首次啟動先發送一次，確保設定成功
    generate_and_send_french()

    # 讓程式保持在背景常駐執行，等待排程時間
    while True:
        schedule.run_pending()
        time.sleep(60)
