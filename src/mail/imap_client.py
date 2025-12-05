"""IMAPクライアントモジュール

IMAPサーバーに接続してメールを取得する。
"""

import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Any
import datetime
import logging


# IMAPサーバーへの接続・メール取得・既読化を担当するクラス
class IMAPClient:
    def __init__(self, host: str, port: int, user: str, password: str):
        """
        IMAPクライアントを初期化
        Args:
            host: IMAPサーバーのホスト名
            port: ポート番号
            user: メールアカウントのユーザー名
            password: メールアカウントのパスワード
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.conn = None
        self.logger = logging.getLogger("imap")

    def connect(self):
        """
        IMAPサーバーへSSL接続しログイン
        """
        self.conn = imaplib.IMAP4_SSL(self.host, self.port)
        self.conn.login(self.user, self.password)
        self.logger.info(f"Connected to {self.host}:{self.port}")

    def disconnect(self):
        """
        IMAPサーバーから切断
        """
        if self.conn:
            self.conn.logout()
            self.logger.info("Disconnected")

    def get_recent_emails(self, period_minutes: int) -> List[Dict[str, Any]]:
        """
        指定期間内に受信したメールを取得
        Args:
            period_minutes: 何分前まで遡るか
        Returns:
            dictのリスト（各メール情報）
        """
        self.conn.select("INBOX")
        since = (datetime.datetime.now() - datetime.timedelta(minutes=period_minutes)).strftime('%d-%b-%Y')
        typ, data = self.conn.search(None, f'(SINCE "{since}")')
        emails = []
        for num in data[0].split():
            typ, msg_data = self.conn.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            subject, encoding = decode_header(msg.get("Subject"))[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8", errors="ignore")
            from_ = email.utils.parseaddr(msg.get("From"))[1]
            date = msg.get("Date")
            # メール本文を抽出
            body = self._extract_body(msg)
            emails.append({
                "id": num,
                "subject": subject,
                "from": from_,
                "date": date,
                "body": body,
                "raw": msg,
            })
        self.logger.info(f"Found {len(emails)} emails in the last {period_minutes} minutes")
        return emails

    def _extract_body(self, msg) -> str:
        """
        メールから本文を抽出
        テキスト部分を優先、HTMLのみの場合はHTMLをテキスト化
        Args:
            msg: email.message.Message オブジェクト
        Returns:
            本文テキスト
        """
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                # テキスト部分を抽出
                if content_type == "text/plain":
                    charset = part.get_content_charset() or "utf-8"
                    body = part.get_payload(decode=True).decode(charset, errors="ignore")
                    break
                # HTMLのみの場合はHTMLを使用
                elif content_type == "text/html" and not body:
                    charset = part.get_content_charset() or "utf-8"
                    body = part.get_payload(decode=True).decode(charset, errors="ignore")
        else:
            # マルチパートではない場合
            charset = msg.get_content_charset() or "utf-8"
            body = msg.get_payload(decode=True).decode(charset, errors="ignore")
        # 改行を統一し、最初の1000文字を取得（Spreadsheet保存用）
        body = body.replace("\r\n", "\n").strip()[:1000]
        return body

    def mark_as_read(self, email_id):
        """
        指定メールを既読にする
        Args:
            email_id: メールID
        """
        self.conn.store(email_id, '+FLAGS', '\\Seen')
        self.logger.info(f"Marked email {email_id} as read")
