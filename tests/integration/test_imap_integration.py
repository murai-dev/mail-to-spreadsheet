"""メール取得の統合テスト

実際のIMAPサーバーに接続してメールを取得するテスト。
環境変数 RUN_INTEGRATION_TESTS=true で有効化されます。
"""

import pytest
from src.mail.imap_client import IMAPClient
from tests.integration.conftest import skip_integration
import os


@skip_integration
class TestIMAPClientIntegration:
    """IMAPClient統合テスト"""

    def test_connect_and_fetch_emails(self):
        """実際のIMAPサーバーに接続してメールを取得"""
        # 環境変数から認証情報を取得
        host = os.getenv("MAIL_HOST", "imap.gmail.com")
        port = int(os.getenv("MAIL_PORT", "993"))
        user = os.getenv("MAIL_USER")
        password = os.getenv("MAIL_PASSWORD")
        
        if not user or not password:
            pytest.skip("MAIL_USERとMAIL_PASSWORDが設定されていません")
        
        # IMAP接続
        client = IMAPClient(host, port, user, password)
        client.connect()
        
        # メール取得
        emails = client.get_recent_emails(60)
        
        # メールが取得できることを確認（件数は問わない）
        assert isinstance(emails, list)
        
        # メールが存在する場合、構造を確認
        if len(emails) > 0:
            mail = emails[0]
            assert "id" in mail
            assert "subject" in mail
            assert "from" in mail
            assert "date" in mail
        
        # 切断
        client.disconnect()
