#!/bin/bash

import os
import base64
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# 指定路径
CREDENTIAL_PATH = "./google_credentials.json"
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_PATH, SCOPE)
client = gspread.authorize(creds)
sheet = client.open_by_key(os.environ["SPREADSHEET_ID"]).worksheet("Staff List")

# 只生成一次 JSON 文件
if not os.path.exists("google_credentials.json"):
    with open("google_credentials.json", "wb") as f:
        f.write(base64.b64decode(os.environ["CREDENTIAL_JSON"]))


# 激活虚拟环境路径，按你自己环境改
source ~/vidlab_env/bin/activate

# 跳转到Bot脚本目录，改成你自己的路径
cd "/Users/gggcapital/Desktop/VIDLAB PROJECT/final_data/script/SCRIPTS/"

# 后台运行Bot，日志写到bot.log
nohup python3 python-telegram-bot.py > bot.log 2>&1 &

echo "Bot已启动，日志输出到 bot.log"
