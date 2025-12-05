
# 標準ライブラリ
import logging
import sys
# ローカルモジュール
from src.config import Config
from src.mail.imap_client import IMAPClient
from src.mail.filter import MailFilter
from src.writers.spreadsheet_writer import SpreadsheetWriter


def setup_logging(log_level, log_file):
    """
    ログ出力を初期化
    ファイルとコンソール両方に出力
    Args:
        log_level: ログレベル（DEBUG, INFO, WARNING, ERROR）
        log_file: ログファイルパス
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)]
    )


def main():
    """
    メイン処理フロー
    1. 設定読み込み
    2. ログ初期化
    3. IMAP接続
    4. メール取得
    5. フィルタ適用
    6. Spreadsheet書き込み
    7. 既読化
    8. 終了
    """
    # 設定読み込み
    config = Config()
    env = config.env
    log_conf = config.log
    
    # ログ初期化
    setup_logging(log_conf["level"], log_conf["file"])
    logger = logging.getLogger("main")
    logger.info("Processing started")

    # IMAP接続・認証
    mail_conf = config.mail
    imap = IMAPClient(
        host=mail_conf["host"],
        port=mail_conf["port"],
        user=env["MAIL_USER"],
        password=env["MAIL_PASSWORD"]
    )
    imap.connect()

    # メール取得（指定期間内）
    period = mail_conf.get("check_period_minutes", 60)
    emails = imap.get_recent_emails(period)

    # メールフィルタを適用
    mail_filter = MailFilter(config.filters)
    filtered = [m for m in emails if mail_filter.match(m)]
    logger.info(f"{len(filtered)} emails matched the filter condition")

    # Google Spreadsheetに書き込み
    ss_conf = config.spreadsheet
    writer = SpreadsheetWriter(
        spreadsheet_id=ss_conf["spreadsheet_id"],
        sheet_name=ss_conf["sheet_name"],
        service_account_file=env["GOOGLE_SERVICE_ACCOUNT_FILE"],
        columns=ss_conf["columns"]
    )
    writer.authenticate()
    
    # フィルタに合致したメールをSpreadsheetに記録
    for idx, mail in enumerate(filtered, 1):
        # 設定で指定されたカラム順にデータを抽出
        data = {
            "from": mail["from"],
            "subject": mail["subject"],
            "received_at": mail["date"],
            "body": mail["body"],
        }
        writer.write(data)
        logger.info(f"Row written successfully ({idx}/{len(filtered)})")
        # 処理済みメールを既読にして重複処理を防ぐ
        imap.mark_as_read(mail["id"])
    
    imap.disconnect()
    logger.info("Processing completed")


if __name__ == "__main__":
    main()
