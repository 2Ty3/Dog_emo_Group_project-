from __future__ import unicode_literals
from flask import Flask, request, abort, render_template
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)

import requests, configparser

app = Flask(__name__, static_url_path='/static')
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])


config = configparser.ConfigParser()
# config.read(r"D:\Line ChatBot\LineBot2024-12\LineBot2024-12\config.ini")
config.read('/config.ini')
configuration = Configuration(access_token=config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

my_line_id = config.get('line-bot', 'my_line_id')
end_point = config.get('line-bot', 'end_point')
line_login_id = config.get('line-bot', 'line_login_id')
line_login_secret = config.get('line-bot', 'line_login_secret')
my_phone = config.get('line-bot', 'my_phone')
HEADER = {
    'Content-type': 'application/json',
    'Authorization': F'Bearer {config.get("line-bot", "channel_access_token")}'
}

# Line的部分由POST傳、抓資料
@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return 'GET_ok'   
    body = request.json
    events = body["events"]
    if request.method == 'POST' and len(events) == 0:
        return 'POST_ok'
    print(body)
    if "replyToken" in events[0]:
        payload = dict()
        replyToken = events[0]["replyToken"]
        payload["replyToken"] = replyToken
        if events[0]["type"] == "message":
            if events[0]["message"]["type"] == "text":
                text = events[0]["message"]["text"]

                if text == "@附近收容所":
                    payload["messages"] = [shelter()] 

                elif text == "@拍照":
                    payload["messages"] = [take_a_photo()]

                elif text == "@新手飼養手冊":
                    payload["messages"] = [manual()]   

                elif text == "@意見回饋":
                    payload["messages"] = [surveymonkey()]   

                elif text == "你太無情了":
                    payload["messages"] = [test()]

                elif text.startswith("/ai"):
                    payload["messages"] = [RAG(text)]

                else:
                    payload["messages"] = []

                replyMessage(payload)

    return payload

# 我是範本，要回傳訊息需要這個json格式
def test():
    message = {
        "type":"text",
        "text":"哭阿"
    }
    return message

def shelter():
    pass

def take_a_photo():
    pass

def manual():
    pass

def surveymonkey():
    message = {
        "type" : "text",
        "text" : "請點擊連結:"
    }
    return message

def RAG(text):
    # 測試用網址 --這邊需要更改本機網址
    n8n_url = 'http://localhost:5678/webhook-test/170accfe-f167-4f24-813e-63b437adaf29'
    # 生產用網址
    # n8n_url = 'http://localhost:5678/webhook/170accfe-f167-4f24-813e-63b437adaf29'

    data = {
        "text": text  # 將傳遞的文字作為參數傳送
    }
    # n8n處理後的訊息接收並回傳
    response = requests.post(n8n_url, json=data)

    # print(f"n8n 回傳資料: {response}")

    # 確認返回的資料中是否包含 response 和 text 欄位
    try:
        # 嘗試解析 JSON 資料
        n8n_response_data = response.json()
        
        # 根據回傳的結構提取 'text' 資料
        processed_text = n8n_response_data[0]["response"]["text"]
        
    except ValueError:
        # 如果回應不是有效的 JSON 格式
        print(f"無效的 JSON 格式: {response.text}")
        processed_text = "系統忙碌中，請稍後再試"


    message = {
        "type": "text",
        "text": processed_text
    }
    return message

# 回覆訊息
def replyMessage(payload):
    url = "https://api.line.me/v2/bot/message/reply"
    response = requests.post(url=url, headers=HEADER, json=payload)

    if response.status_code == 200:
        return "reply_ok"
    else:
        print(response.text)


if __name__ == "__main__":
    app.debug = True
    app.run()
