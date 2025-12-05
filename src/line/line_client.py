"""LINE Bot APIクライアントモジュール

LINE Official Account経由でメッセージを取得する。
Webhook形式で受信したメッセージを処理します。
"""

import logging
from typing import List, Dict, Any
from datetime import datetime


# LINE Botからのメッセージを処理するクラス
class LineClient:
    def __init__(self, channel_access_token: str, channel_secret: str):
        """
        LINEクライアントを初期化
        Args:
            channel_access_token: LINE Channel Access Token
            channel_secret: LINE Channel Secret
        """
        self.channel_access_token = channel_access_token
        self.channel_secret = channel_secret
        self.logger = logging.getLogger("line")
        # Webhook経由で受信したメッセージを保持
        self._messages = []

    def add_message(self, user_id: str, user_name: str, text: str) -> None:
        """
        Webhookで受信したメッセージを追加
        Args:
            user_id: LINE ユーザーID
            user_name: 送信者の表示名（アカウント名）
            text: メッセージ本文
        """
        message = {
            "id": len(self._messages),  # シンプルなID生成
            "from": user_name,  # 送信者名を「from」に設定
            "subject": "",  # LINEメッセージは件名なし
            "body": text,  # メッセージ本文
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user_id,
            "type": "line",
        }
        self._messages.append(message)
        self.logger.info(f"Message added from {user_name}: {text[:50]}...")

    def get_messages(self) -> List[Dict[str, Any]]:
        """
        保持しているメッセージを取得
        Returns:
            メッセージリスト
        """
        return self._messages

    def clear_messages(self) -> None:
        """
        処理済みメッセージをクリア
        """
        self._messages = []
        self.logger.info("Messages cleared")
