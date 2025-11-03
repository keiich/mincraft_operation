#!/usr/bin/env python3
import datetime
import os
import requests

# current_logfile.txt から実際のログファイル名を読む
logfile_marker = "/home/ubuntu/minecraft/current_logfile.txt"
webhook_url = 'https://discord.com/api/webhooks/XXXXXXXXXXXXXXXXXXXX'
try:
    with open(logfile_marker, "r") as f:
        file_name = f.read().strip()
except FileNotFoundError:
    print("LOG FILE MARKER NOT FOUND!")
    exit(1)

# ログファイルパス
file_path = f"/home/ubuntu/minecraft/{file_name}"

# カウンタ初期化
in_cnt = 0
out_cnt = 0
starting = True
server_start_seconds = None  # サーバー起動時刻（秒）

try:
    with open(file_path, 'r') as f:
        lines = f.readlines()
except FileNotFoundError:
    print("LOG FILE NOT FOUND!")
    exit(1)

for line in lines:
    line = line.strip()
    if not line:
        continue
    if not line.startswith('['):
        continue

    parts = line[1:].split()
    if len(parts) < 2:
        continue

    timestamp_str = parts[1]  # 'hh:mm:ss:ms'
    hms = timestamp_str.split(':')
    if len(hms) < 3:
        continue

    hour, minute, second = int(hms[0]), int(hms[1]), int(hms[2])
    log_seconds = hour * 3600 + minute * 60 + second

    # サーバー起動時刻を Server started. の行から取得
    if server_start_seconds is None and 'Server started.' in line:
        server_start_seconds = log_seconds
        continue

    # プレイヤー接続・切断の判定
    if 'Player connected:' in line:
        in_cnt += 1
    if 'Player disconnected:' in line:
        out_cnt += 1

# 起動15分以内か判定
if server_start_seconds is not None:
    now = datetime.datetime.now()
    now_seconds = now.hour*3600 + now.minute*60 + now.second
    diff = now_seconds - server_start_seconds
    if diff < 0:
        diff += 24*3600  # 日をまたいだ場合
    starting = diff < 15*60
else:
    # Server started. の行が見つからなかった場合
    print("Server start time not found in log.")
    starting = True  # 安全のため起動中扱い

# 判定結果を出力
if starting:
    print('Server is starting... (shutdown disabled for first 15 min)')
elif in_cnt > out_cnt:
    print('Someone is logged in.')
else:
    print('No players online. Shutting down...')
    data = {
        'content': f'ログインユーザがいなくなったため、インスタンスはシャットダウンしました。'
    }
    requests.post(webhook_url, json=data)
    os.system('sudo shutdown -h now')
