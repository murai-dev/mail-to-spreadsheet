# Python 3.11をベースイメージとして使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージを更新・インストール
RUN apt-get update && apt-get install -y \
    cron \
    && rm -rf /var/lib/apt/lists/*

# requirements.txtをコピーして依存パッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY src/ src/
COPY config/ config/
COPY infra/ infra/

# ログ出力ディレクトリを作成
RUN mkdir -p /var/log

# 環境変数を設定（デフォルト値）
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO
ENV LOG_FILE=/var/log/mail-to-spreadsheet.log

# エントリーポイントに実行権限を付与
RUN chmod +x infra/docker-entrypoint.sh

ENTRYPOINT ["infra/docker-entrypoint.sh"]
CMD ["cron", "-f"]
