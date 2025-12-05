#!/bin/bash
# Docker コンテナ起動時に実行するスクリプト
# settings.yamlの設定に基づいてcrontabを自動生成

set -e

APP_DIR="/app"
CONFIG_FILE="${APP_DIR}/config/settings.yaml"
CRONTAB_FILE="/etc/cron.d/mail-relay"

echo "===================================================="
echo "Mail-to-Spreadsheet コンテナ起動"
echo "====================================================="

# 設定ファイルの確認
echo "[*] 設定ファイルを確認中..."
if [ ! -f "$CONFIG_FILE" ]; then
    echo "[!] エラー: 設定ファイルが見つかりません: $CONFIG_FILE"
    exit 1
fi
echo "[✓] 設定ファイル: $CONFIG_FILE"

# Python スクリプトで crontab を生成
echo "[*] crontab を生成中..."
CRON_LINE=$(cd /app && python -m infra.generate_crontab)

if [ $? -ne 0 ] || [ -z "$CRON_LINE" ]; then
    echo "[!] エラー: crontab の生成に失敗しました"
    exit 1
fi

echo "[✓] 生成された crontab:"
echo "    ${CRON_LINE}"

# crontab ファイルを作成（ヘッダー付き）
cat > "$CRONTAB_FILE" <<CRON_EOF
# Mail-to-Spreadsheet crontab
# 自動生成ファイル（${CONFIG_FILE} から自動生成）

# タイムゾーン設定
TZ=Asia/Tokyo

# 環境設定
SHELL=/bin/sh
PATH=/usr/local/bin:/usr/bin:/bin
MAILTO=""

# Mail-to-Spreadsheet 実行設定
${CRON_LINE}

CRON_EOF

echo "[✓] crontab ファイル作成: $CRONTAB_FILE"

# crontab ファイルのパーミッション設定
chmod 644 "$CRONTAB_FILE"
echo "[✓] crontab パーミッション設定完了"

# ログファイルパスをsettings.yamlから取得
echo "[*] ログ設定を確認中..."
LOG_FILE=$(cd /app && python -c "import yaml; print(yaml.safe_load(open('config/settings.yaml'))['log']['file'])")
echo "[✓] ログファイル: $LOG_FILE"

# ログディレクトリの確認・作成
LOG_DIR=$(dirname "$LOG_FILE")
if [ ! -d "$LOG_DIR" ]; then
    echo "[*] ログディレクトリを作成中: $LOG_DIR"
    mkdir -p "$LOG_DIR"
    echo "[✓] ログディレクトリ作成完了"
fi

# ログファイルの作成
touch "$LOG_FILE"

echo "[*] cron デーモンを起動中..."
echo "===================================================="

# cronデーモンを起動
exec "$@"
