# Flask 相關模組
from flask import Flask, request

# Line Bot 相關模組
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApiBlob,
)

# 網頁爬蟲+繪圖相關模組
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# 圖片辨識相關模組
from ultralytics import YOLO
import cv2

# 日期時間相關模組
from datetime import datetime
import schedule
import time

# 其他常用模組
import json
import requests
import configparser
import threading


app = Flask(__name__, static_url_path="/static")
app.config['UPLOAD_FOLDER'] = 'static'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

config = configparser.ConfigParser()
config.read("config.ini")
configuration = Configuration(access_token=config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))
my_line_id = config.get('line-bot', 'my_line_id')
line_login_id = config.get('line-bot', 'line_login_id')
line_login_secret = config.get('line-bot', 'line_login_secret')
my_phone = config.get('line-bot', 'my_phone')
HEADER = {
    'Content-type': 'application/json',
    'Authorization': F'Bearer {config.get("line-bot", "channel_access_token")}'
}
current_date = datetime.now().date()
save_dir = 'static'
ngrok_url =config.get('line-bot', 'end_point')


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

                if text == "@收容所":
                    payload["messages"] = [shelter_zelda(), shelter_link()]

                elif text == "@拍照":
                    payload["messages"] = [take_a_photo()]

                elif text == "@新手飼養手冊":
                    payload["messages"] = [manual()]   

                else:
                    payload["messages"] = [RAG(text)]
                replyMessage(payload)
            elif events[0]["message"]["type"] == "image":
                message_id = events[0]["message"]["id"]
                payload["messages"] = [distinguish(message_id)]
            replyMessage(payload)

    return payload


# 無情的辨識圖片開始
def distinguish(message_id):
    with ApiClient(configuration) as api_client:
        line_bot_blob_api = MessagingApiBlob(api_client)
        message_content = line_bot_blob_api.get_message_content(message_id=message_id)
        # 使用文件路徑寫入圖片
        image_path = f'images/{message_id}.jpg' #放在images資料夾的圖片名稱
        with open(image_path, 'wb') as f:
            f.write(message_content)    #將抓到的圖片資訊(binary)寫成圖片
    # 辨識圖片  
    img = cv2.imread(image_path)
    model = YOLO('0108.pt')
    results = model(img)
    if isinstance(results, list):
        results = results[0]
        
    # 將結果圖片寫入到static資料夾內
    output_image_path = f'{save_dir}/{message_id}_result.jpg'
    results.save(output_image_path)  
    
    # 需要透過一個網站提供URL
    image_url = f'{ngrok_url}/static/{message_id}_result.jpg'
    message = {
        "type" : "image",
        "originalContentUrl" : image_url , 
        "previewImageUrl" : image_url,
    }
    return message


# 政府網站偶爾會鬧脾氣
def shelter_link():

    message = {
        "type": "text",
        "text": "想在google map上面查看? 前往連結：https://maps.app.goo.gl/DCfrDHKc17zV68tV6",
    }
    return message


# 我只是附帶的
def shelter_zelda():
    # 每天更新一次，但同一天的資料一樣
    image_url = f'{ngrok_url}/static/{current_date}.jpg'

    message = {
        "type" : "image",
        "originalContentUrl" : image_url , 
        "previewImageUrl" : image_url,
    }

    return message


# 結合聊天機器人可以讓功能好一點
def manual():
    message = {
        "type": "template",
        "altText": "this is a carousel template",
        "template": {
            "type": "carousel",
            "columns": [
                {
                    "thumbnailImageUrl": f"{ngrok_url}/static/1研究不同狗的品種.jpg",
                    "imageBackgroundColor": "#FFFFFF",
                    "title": "研究不同狗的品種",
                    "text": "step 1",
                    "defaultAction": {
                        "type": "message",
                        "label": "Reply with message",
                        "text": "Information about different dog breeds"
                    },
                    "actions": [
                        {
                            "type": "message",
                            "label": "查看",
                            "text": "研究不同的犬種，了解他們的性格、需求和特點，以選擇適合您的生活方式的犬種。"
                        }
                    ]
                },
                {
                    "thumbnailImageUrl": f"{ngrok_url}/static/2犬舍.jpg",
                    "imageBackgroundColor": "#FFFFFF",
                    "title": "犬舍",
                    "text": "step 2",
                    "defaultAction": {
                        "type": "message",
                        "label": "Reply with message",
                        "text": "Information about dog breeds"
                    },
                    "actions": [
                        {
                            "type": "message",
                            "label": "查看",
                            "text": "尋找當地的動物收容所、犬舍或領養機構，以找到可供領養的狗。"
                        }
                    ]
                },
                {
                    "thumbnailImageUrl": f"{ngrok_url}/static/3填寫領養表單.jpg",
                    "imageBackgroundColor": "#FFFFFF",
                    "title": "填寫領養表單",
                    "text": "step 3",
                    "defaultAction": {
                        "type": "message",
                        "label": "Reply with message",
                        "text": "Information about adopting dog"
                    },
                    "actions": [
                        {
                            "type": "message",
                            "label": "查看",
                            "text": "填寫領養申請表，提供您的個人資料、家庭情況和居住環境等信息。"
                        }
                    ]
                },
                {
                    "thumbnailImageUrl": f"{ngrok_url}/static/4領養面談.jpg",
                    "imageBackgroundColor": "#FFFFFF",
                    "title": "領養面談",
                    "text": "step 4",
                    "defaultAction": {
                        "type": "message",
                        "label": "Reply with message",
                        "text": "Interview about adoption"
                    },
                    "actions": [
                        {
                            "type": "message",
                            "label": "查看",
                            "text": "領養機構的工作人員會與您進行面談，了解您的意圖、生活方式和對狗的照顧能力。"
                        }
                    ]
                },
                {
                    "thumbnailImageUrl": f"{ngrok_url}/static/5參觀狗狗.jpg",
                    "imageBackgroundColor": "#FFFFFF",
                    "title": "參觀狗狗",
                    "text": "step 5",
                    "defaultAction": {
                        "type": "message",
                        "label": "Reply with message",
                        "text": "visit doge"
                    },
                    "actions": [
                        {
                            "type": "message",
                            "label": "查看",
                            "text": "您會有機會參觀可供領養的狗，了解牠們的性格和行為。"
                        }
                    ]
                },
                {
                    "thumbnailImageUrl": f"{ngrok_url}/static/6簽署合同.jpg",
                    "imageBackgroundColor": "#FFFFFF",
                    "title": "簽署合同",
                    "text": "step 6",
                    "defaultAction": {
                        "type": "message",
                        "label": "Reply with message",
                        "text": "sign contract"
                    },
                    "actions": [
                        {
                            "type": "message",
                            "label": "查看",
                            "text": "如果您決定領養，將會完成相關的合約，承諾提供適當的照顧和愛護。"
                        }
                    ]
                },
                {
                    "thumbnailImageUrl": f"{ngrok_url}/static/7接狗回家.jpg",
                    "imageBackgroundColor": "#FFFFFF",
                    "title": "接狗回家",
                    "text": "step 7",
                    "defaultAction": {
                        "type": "message",
                        "label": "Reply with message",
                        "text": "bring dog to home"
                    },
                    "actions": [
                        {
                            "type": "message",
                            "label": "查看",
                            "text": "領養完成後，您可以接狗回家，開始新的生活。"
                        }
                    ]
                }
            ],
            "imageAspectRatio": "rectangle",
            "imageSize": "cover"
        }
    }
    return message

# 無情的聊天機器人
def RAG(text):
    # 測試用網址 --這邊需要更改
    # n8n_url = 'http://localhost:5678/webhook-test/170accfe-f167-4f24-813e-63b437adaf29'
    # 生產用網址
    n8n_url = 'http://localhost:5678/webhook/170accfe-f167-4f24-813e-63b437adaf29'

    data = {
        "text": text  # 將傳遞的文字作為參數傳送
    }
    # n8n處理後的訊息接收並回傳
    response = requests.post(n8n_url, json=data)

    # 確認返回的資料中是否包含 response 和 text 欄位
    try:
        n8n_response_data = response.json()
    
        RAG_text = n8n_response_data[0]["response"]["text"]
        
    except ValueError:
        # 如果回應不是有效的 JSON 格式
        print(f"無效的 JSON 格式: {response.text}")
        RAG_text = "勞動布出現，請稍後再試"

    message = {
        "type": "text",
        "text": RAG_text
    }
    return message


#偷偷塞爬蟲在這裡
def crawler():

    # 配置 Chrome 選項
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # 初始化 WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    # 打開目標網站
    url = "https://www.pet.gov.tw/AnimalApp/ShelterMap.aspx"
    driver.get(url)

    # 等待特定元素加載
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "tab2-1")))

    # 獲取頁面源代碼並解析
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # 取得指定的表格
    table = soup.find("table", {"id": "tab2-1"})

    # 提取表格中的每一行資料
    rows = table.find_all("tr")
    # 把資料丟進清單，方便儲存
    data = []

    # 跳過第一行標題，並解析每一行數據
    for row in rows[1:]:
        columns = row.find_all("td")
        
        # 確保列數正確
        if len(columns) >= 3:
            shelter_name = columns[0].get_text(strip=True)
            max_capacity = int(columns[1].get_text(strip=True))
            current_count = int(columns[2].get_text(strip=True))

            # 將資料加入 data 清單
            data.append([shelter_name, max_capacity, current_count])
    # 儲存資料到 JSON 文件
    bbkkbkk = "shelter_data"
    save_path = f"{bbkkbkk}/{current_date}"

    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    driver.quit()

    shelter_fig()#將資料轉成圖片


def shelter_fig():
    with open(f'shelter_data/{current_date}', 'rb') as file:
        data = json.load(file)

    # 轉換為 DataFrame
    df = pd.DataFrame(data, columns=["機構名稱", "可收容數量", "目前數量"])

    # 創建圖像
    matplotlib.rc('font', family='Microsoft JhengHei')
    fig, ax = plt.subplots(figsize=(10, 8))  # 設定圖像大小
    ax.axis('off')  # 不顯示軸

    # 建立表格 (直接用 matplotlib.table.Table)
    tbl = ax.table(
        cellText=df.values,  # 表格內容
        colLabels=df.columns,  # 表頭
        loc='center',  # 表格位置
        cellLoc='center',  # 單元格對齊方式
        colWidths=[0.3, 0.2, 0.2]  # 列寬比例
    )

    tbl.auto_set_font_size(False)
    tbl.set_fontsize(12)
    tbl.scale(1.2, 1.2)  # 調整表格大小

    plt.savefig(f'{save_dir}/{current_date}.jpg')

# 設定每天00:00執行爬蟲
schedule.every().day.at("00:00").do(crawler)  


# 先爬一次，之後每天自動爬一次
def run_schedule():
    crawler()
    while True:
        schedule.run_pending()  # 執行排程任務
        time.sleep(3600)  # 每小時檢查一次，才不會占用資源


# Line官方給的回覆訊息方法
def replyMessage(payload):
    url = "https://api.line.me/v2/bot/message/reply"
    response = requests.post(url=url, headers=HEADER, json=payload)
    if response.status_code == 200:
        return "reply_ok"
    else:
        print(response.text)

# 任務分頭行動，這邊可以寫成兩個程式，沒必要硬擠
if __name__ == "__main__":
    threading.Thread(target=run_schedule, daemon=True).start()
    app.run(debug=True)
