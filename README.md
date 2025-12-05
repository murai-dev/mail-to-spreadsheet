# Mail-to-Spreadsheet

メールを検知してGoogle Spreadsheetに自動記録するプログラム。  
特定の件名や送信元を持つメールを受信したら、送信元・件名・受信日時などをGoogle Spreadsheetに自動転記します。

## 概要

- **メール取得**: IMAPでメールサーバーに接続し、指定期間内のメールを取得
- **フィルタリング**: 件名や送信元でメールをフィルター
- **自動記録**: 条件に合致したメールをGoogle Spreadsheetに記録
- **スケジュール実行**: cronで定期的に自動実行（Docker環境）

## 主な機能

- ✅ Gmail/IMAP対応のメール取得
- ✅ 件名の前方一致フィルター
- ✅ 送信元メールアドレスのフィルター（完全一致・部分一致）
- ✅ Google Spreadsheetへの自動書き込み
- ✅ Docker環境での自動スケジュール実行
- ✅ 設定ファイル（YAML）による柔軟な設定管理
- ✅ 詳細なログ出力

## 技術構成

- Python 3.11+
- Gmail IMAP / Google Sheets API
- Docker & Docker Compose
- pytest（テストフレームワーク）

## 必要なもの

- Docker & Docker Compose
- Gmailアカウント（またはIMAP対応メールアカウント）
- Google Cloud Platformアカウント
- Google Spreadsheet

## セットアップ

### 1. Gmail設定

1. [IMAPを有効化](https://support.google.com/mail/answer/7126229)
2. [アプリパスワードを作成](https://support.google.com/accounts/answer/185833)

### 2. Google Sheets API設定

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクト作成
2. Google Sheets APIを有効化
3. サービスアカウントを作成し、JSON認証ファイルをダウンロード
4. Spreadsheetをサービスアカウントのメールアドレスと共有（編集権限を付与）
5. Spreadsheet IDをURLから取得  
   `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit`

### 3. プロジェクトのセットアップ

```bash
# リポジトリをクローン
git clone <repository-url>
cd mail-to-spreadsheet

# 環境変数ファイルを作成
cp .env.example .env

# .envファイルを編集
MAIL_USER=your-email@gmail.com
MAIL_PASSWORD=your-app-password
GOOGLE_SERVICE_ACCOUNT_FILE=config/service-account.json
```

### 4. 設定ファイルの編集

`config/settings.yaml` を編集：

```yaml
mail:
  host: imap.gmail.com
  port: 993
  check_period_minutes: 60  # 過去60分以内のメールをチェック
  check_interval_minutes: 30  # 30分ごとに実行

filters:
  - type: "subject"
    condition: "prefix"
    value: "【重要】"
  - type: "from"
    condition: "contains"
    value: "@example.com"

spreadsheet:
  spreadsheet_id: "your-spreadsheet-id-here"
  sheet_name: "メール記録"
  columns:
    - from
    - subject
    - received_at

log:
  level: INFO  # ログレベル: DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: "/var/log/mail-to-spreadsheet.log"  # ログファイル出力先
```

### 5. サービスアカウント認証ファイルの配置

ダウンロードしたJSON認証ファイルを `config/service-account.json` に配置

```bash
cp ~/Downloads/service-account-key.json config/service-account.json
```

## 実行方法

### Docker Composeで実行

```bash
# コンテナをビルド・起動
cd infra
docker-compose up -d

# ログを確認
docker-compose logs -f

# コンテナを停止
docker-compose down
```

### ローカル環境で実行（開発用）

```bash
# 依存パッケージをインストール
pip install -r requirements.txt

# 直接実行
python -m src.main
```

## テスト

### 単体テスト

```bash
# 全テスト実行
pytest tests/unit/

# カバレッジ測定
pytest --cov=src tests/unit/
```

### 統合テスト

統合テストは実際のメールアカウントとSpreadsheetを使用します。

```bash
# 環境変数を設定
export RUN_INTEGRATION_TESTS=true
export TEST_MAIL_USER=your-test-email@gmail.com
export TEST_MAIL_PASSWORD=your-test-app-password
export TEST_SPREADSHEET_ID=your-test-spreadsheet-id
export TEST_SERVICE_ACCOUNT_FILE=config/service-account.json

# 統合テスト実行
pytest tests/integration/
```

## ディレクトリ構造

```
mail-to-spreadsheet/
├── src/
│   ├── mail/
│   │   ├── imap_client.py      # IMAPクライアント
│   │   └── filter.py            # メールフィルタ
│   ├── writers/
│   │   ├── base.py              # 書き込み基底クラス
│   │   └── spreadsheet_writer.py # Spreadsheet書き込み
│   ├── config.py                # 設定管理
│   └── main.py                  # メイン処理
├── config/
│   ├── settings.yaml            # 設定ファイル
│   └── service-account.json     # Google認証（.gitignore）
├── infra/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── docker-entrypoint.sh     # コンテナ起動スクリプト
│   └── generate_crontab.py      # crontab生成
├── tests/
│   ├── unit/                    # 単体テスト
│   └── integration/             # 統合テスト
├── requirements.txt
├── .env.example
└── README.md
```

## フィルター条件のカスタマイズ

### 件名の前方一致

```yaml
filters:
  - type: "subject"
    condition: "prefix"
    value: "【重要】"
```

### 送信元の完全一致

```yaml
filters:
  - type: "from"
    condition: "equals"
    value: "admin@example.com"
```

### 送信元の部分一致（ドメイン指定）

```yaml
filters:
  - type: "from"
    condition: "contains"
    value: "@example.com"
```

### 複数条件の組み合わせ

```yaml
filters:
  - type: "subject"
    condition: "prefix"
    value: "【重要】"
  - type: "from"
    condition: "contains"
    value: "@example.com"
```

すべての条件を満たすメールのみが記録されます（AND条件）。

## トラブルシューティング

### メールが取得できない

- IMAPが有効化されているか確認
- アプリパスワードが正しいか確認
- ファイアウォールでポート993が開いているか確認

### Spreadsheetに書き込めない

- サービスアカウントがSpreadsheetに編集権限で共有されているか確認
- Spreadsheet IDが正しいか確認
- Google Sheets APIが有効化されているか確認

### ログの確認

```bash
# Dockerコンテナのログ
docker-compose logs -f

# ログファイル（Dockerボリューム）
docker-compose exec mail-to-spreadsheet tail -f /var/log/mail-to-spreadsheet.log
```

## ライセンス

MIT License

## 参考資料

- [Gmail IMAP設定](https://support.google.com/mail/answer/7126229)
- [Googleアプリパスワード](https://support.google.com/accounts/answer/185833)
- [Google Sheets API](https://developers.google.com/sheets/api/guides/concepts)
