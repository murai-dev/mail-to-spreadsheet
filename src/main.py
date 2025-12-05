
# 標準ライブラリ
import logging
import sys
# ローカルモジュール
from src.config import Config
from src.mail.imap_client import IMAPClient
from src.mail.filter import MailFilter
from src.line.line_client import LineClient
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


def get_email_messages(config, logger):
    """
    メールサーバーからメッセージを取得
    Args:
        config: Config オブジェクト
        logger: ロガー
    Returns:
        メッセージリスト
    """
    mail_conf = config.mail
    
    # メールが無効の場合はスキップ
    if not mail_conf.get("enabled", True):
        logger.info("Mail source is disabled")
        return [], None
    
    env = config.env
    
    # IMAP接続・認証
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
    logger.info(f"Got {len(emails)} emails from IMAP server")
    
    return emails, imap


def get_line_messages(config, logger):
    """
    LINEメッセージを取得
    Args:
        config: Config オブジェクト
        logger: ロガー
    Returns:
        LINEメッセージリスト
    """
    line_conf = config.line
    
    if not line_conf.get("enabled", False):
        logger.info("LINE is disabled")
        return []
    
    env = config.env
    line_client = LineClient(
        channel_access_token=env.get("LINE_CHANNEL_ACCESS_TOKEN"),
        channel_secret=env.get("LINE_CHANNEL_SECRET")
    )
    
    messages = line_client.get_messages()
    logger.info(f"Got {len(messages)} messages from LINE")
    line_client.clear_messages()
    
    return messages


def main():
    """
    メイン処理フロー
    1. 設定読み込み
    2. ログ初期化
    3. メール・LINEのデータ取得
    4. フィルタ適用
    5. Spreadsheet書き込み
    6. 既読化
    7. 終了
    """
    # 設定読み込み
    config = Config()
    env = config.env
    log_conf = config.log
    
    # ログ初期化
    setup_logging(log_conf["level"], log_conf["file"])
    logger = logging.getLogger("main")
    logger.info("Processing started")

    # メールとLINEのメッセージを収集
    all_messages = []
    imap_client = None
    
    # メール取得
    try:
        emails, imap_client = get_email_messages(config, logger)
        all_messages.extend(emails)
    except Exception as e:
        logger.error(f"Error getting emails: {e}")
    
    # LINE取得
    try:
        line_messages = get_line_messages(config, logger)
        all_messages.extend(line_messages)
    except Exception as e:
        logger.error(f"Error getting LINE messages: {e}")
    
    # データ源が何もない場合は処理終了
    if not all_messages:
        logger.info("No messages from any source")
        if imap_client:
            imap_client.disconnect()
        logger.info("Processing completed (0 messages processed)")
        return

    # フィルタを適用（メールのみ対象、LINEメッセージはフィルタスキップ）
    mail_filter = MailFilter(config.filters)
    filtered_messages = []
    for msg in all_messages:
        # LINEメッセージはフィルタをスキップ
        if msg.get("type") == "line":
            filtered_messages.append(msg)
            logger.debug(f"LINE message passed (no filter): {msg['from']}")
        # メールはフィルタ適用
        elif mail_filter.match(msg):
            filtered_messages.append(msg)
            logger.debug(f"Email passed filter: {msg['subject']}")
    
    logger.info(f"{len(filtered_messages)} messages matched the filter condition")

    # Google Spreadsheetに書き込み
    ss_conf = config.spreadsheet
    writer = SpreadsheetWriter(
        spreadsheet_id=ss_conf["spreadsheet_id"],
        sheet_name=ss_conf["sheet_name"],
        service_account_file=env["GOOGLE_SERVICE_ACCOUNT_FILE"],
        columns=ss_conf["columns"]
    )
    writer.authenticate()
    
    # フィルタに合致したメッセージをSpreadsheetに記録
    for idx, msg in enumerate(filtered_messages, 1):
        # 設定で指定されたカラム順にデータを抽出
        data = {
            "from": msg["from"],
            "subject": msg.get("subject", ""),
            "received_at": msg.get("date", ""),
            "body": msg.get("body", ""),
        }
        writer.write(data)
        logger.info(f"Row written successfully ({idx}/{len(filtered_messages)})")
        
        # メール（IMAPクライアント経由）の既読処理
        if msg.get("type") != "line" and imap_client:
            imap_client.mark_as_read(msg["id"])
            logger.debug(f"Marked as read: {msg.get('subject', 'No subject')}")
    
    # クリーンアップ
    if imap_client:
        imap_client.disconnect()
    
    logger.info(f"Processing completed ({len(filtered_messages)} messages processed)")


if __name__ == "__main__":
    main()
