"""Spreadsheet書き込みの統合テスト

実際のGoogle Spreadsheetに書き込むテスト。
環境変数 RUN_INTEGRATION_TESTS=true で有効化されます。
"""

import pytest
from src.writers.spreadsheet_writer import SpreadsheetWriter
from src.config import Config
from tests.integration.conftest import skip_integration
import os
from datetime import datetime


@skip_integration
class TestSpreadsheetWriterIntegration:
    """SpreadsheetWriter統合テスト"""

    def test_write_to_spreadsheet(self):
        """実際のSpreadsheetに書き込み"""
        # 設定ファイルから設定を取得
        config = Config()
        spreadsheet_conf = config.spreadsheet
        env = config.env
        
        spreadsheet_id = spreadsheet_conf.get("spreadsheet_id")
        sheet_name = spreadsheet_conf.get("sheet_name")
        service_account_file = env.get("GOOGLE_SERVICE_ACCOUNT_FILE")
        
        if not spreadsheet_id or not service_account_file:
            pytest.skip("settings.yamlまたは.envの設定が不足しています")
        
        # Spreadsheetライター初期化
        columns = ["from", "subject", "received_at"]
        writer = SpreadsheetWriter(
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            service_account_file=service_account_file,
            columns=columns
        )
        
        # 認証
        writer.authenticate()
        
        # テストデータを書き込み
        test_data = {
            "from": "test@example.com",
            "subject": f"統合テスト {datetime.now().isoformat()}",
            "received_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 書き込み実行
        writer.write(test_data)
        
        # エラーが発生しないことを確認（実際の書き込み結果の検証は手動で確認）
        assert True
