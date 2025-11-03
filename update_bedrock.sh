#!/bin/bash
# ==============================================
# Minecraft Bedrock Server Auto Updater (Linux)
# ==============================================

set -e
cd /home/ubuntu/minecraft

HEADERS="Mozilla/5.0 (X11; Linux x86_64)"
API_URL="https://net-secondary.web.minecraft-services.net/api/v1.0/download/links"
LOGFILE="/home/ubuntu/minecraft/update.log"
WEBHOOK_URL="https://discord.com/api/webhooks/XXXXXXXXXXXXXXXXXXXX"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] Checking latest Bedrock Server version..." | tee -a "$LOGFILE"

# APIから最新リンク取得
download_link=$(curl -s -H "User-Agent: $HEADERS" "$API_URL" \
    | grep -oP "\"downloadType\":\"serverBedrockLinux\".*?\"downloadUrl\":\"\\K[^\"]+" | head -n 1)

if [ -z "$download_link" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] 最新のBedrockサーバーURLを取得できませんでした。" | tee -a "$LOGFILE"
    exit 0
fi

# バージョン判定
latest_ver=$(echo "$download_link" | grep -oP "bedrock-server-[0-9.]+(?=.zip)" | sed "s/bedrock-server-//")

# ==== 現在のバージョン確認 ====
current_ver=$(cat version.txt 2>/dev/null || echo "none")

echo "現在のバージョン: $current_ver"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] 現在: $current_ver, 最新: $latest_ver" | tee -a "$LOGFILE"

# バージョンが異なる場合のみ更新
if [ "$latest_ver" != "$current_ver" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] 新バージョンを検出。アップデートを開始します..." | tee -a "$LOGFILE"
    message="新バージョンを検出。アップデートしています... \nversion:${latest_ver}\nクライアント側のバージョンを合わせて下さい"

    curl -H "Content-Type: application/json" \
         -X POST \
         -d "{\"content\": \"${message}\"}" \
         "$WEBHOOK_URL"
    wget -q --user-agent="$HEADERS" -O bedrock-server-latest.zip "$download_link"
    unzip -o bedrock-server-latest.zip -d bedrock_tmp >/dev/null

    # world データを引き継ぎ
    if [ -d worlds ]; then
        cp -r worlds bedrock_tmp/worlds
    fi
    if [ -f server.properties ]; then
        cp server.properties bedrock_tmp/
    fi
    if [ -f permissions.json ]; then
        cp permissions.json bedrock_tmp/
    fi
    echo "ZIPを削除:"
    rm -f *.zip

    # 旧サーバを削除
    if [ -f bedrock_server ]; then
        rm -f bedrock_server 2>/dev/null || true
    fi
    rm -rf behavior_packs definitions resource_packs structures 2>/dev/null || true

    # 新サーバ反映
    rm -rf worlds
    rm -rf config
    mv bedrock_tmp/* .
    rm -rf bedrock_tmp/*
    echo "$latest_ver" > version.txt

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] Bedrock Serverをバージョン $latest_ver に更新しました。" | tee -a "$LOGFILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] すでに最新バージョンです。アップデートは不要です。" | tee -a "$LOGFILE"
    message="version:${latest_ver}"

    curl -H "Content-Type: application/json" \
         -X POST \
         -d "{\"content\": \"${message}\"}" \
         "$WEBHOOK_URL"

fi
