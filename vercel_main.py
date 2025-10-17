"""
Vercel 版本的 Line Bot
"""

import json
import os
from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 初始化 Flask
app = Flask(__name__)

# Line Bot 設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    raise ValueError("LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET must be set")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route('/api/v1/webhook', methods=['POST'])
def webhook():
    """Line Bot Webhook 端點"""
    try:
        # 取得請求內容
        body = request.get_data(as_text=True)
        signature = request.headers.get('X-Line-Signature', '')
        
        # 處理事件
        handler.handle(body, signature)
        
        return jsonify({"status": "success"})
        
    except InvalidSignatureError:
        return jsonify({"error": "Invalid signature"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/health', methods=['GET'])
def health():
    """健康檢查端點"""
    return jsonify({
        "status": "healthy",
        "service": "Company Bot System",
        "version": "1.0.0"
    })

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """處理文字訊息"""
    try:
        user_message = event.message.text
        user_id = event.source.user_id
        
        # 基本回應邏輯
        if user_message == "幫助":
            reply_text = "歡迎使用公司 Bot 系統！\n\n可用指令：\n• 合約 - 合約管理\n• 客戶 - 客戶管理\n• 進度 - 進度追蹤\n• 報表 - 報表功能"
        elif user_message == "合約":
            reply_text = "合約管理功能：\n• 查看合約\n• 新增合約\n• 更新合約"
        elif user_message == "客戶":
            reply_text = "客戶管理功能：\n• 查看客戶資料\n• 新增客戶\n• 更新客戶資訊"
        elif user_message == "進度":
            reply_text = "進度追蹤功能：\n• 查看案件進度\n• 更新進度\n• 生成報告"
        elif user_message == "報表":
            reply_text = "報表功能：\n• 財務報表\n• 業務報表\n• 績效報表"
        else:
            reply_text = f"您說：{user_message}\n\n請輸入「幫助」查看可用指令。"
        
        # 發送回應
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        
    except Exception as e:
        print(f"Error handling message: {e}")

# Vercel 入口點
def vercel_handler(request):
    """Vercel 入口點"""
    return app(request.environ, lambda *args: None)
    
if __name__ == '__main__':
    app.run(debug=True)

