"""Configクラスの単体テスト"""

import pytest
import os
from pathlib import Path
from src.config import Config


class TestConfig:
    """Configクラスのテスト"""

    def test_load_settings(self, tmp_path):
        """設定ファイルが正しく読み込めるか"""
        # テスト用の設定ファイルを作成
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text("""
mail:
  host: imap.test.com
  port: 993
  check_period_minutes: 60
  check_interval_minutes: 30

filters:
  - type: "subject"
    condition: "prefix"
    value: "【テスト】"

spreadsheet:
  spreadsheet_id: "test-id"
  sheet_name: "テストシート"
  columns:
    - from
    - subject

log:
  level: "DEBUG"
  file: "/tmp/test.log"
""")
        
        config = Config(settings_path=str(settings_file))
        
        # メール設定の確認
        assert config.mail["host"] == "imap.test.com"
        assert config.mail["port"] == 993
        assert config.mail["check_period_minutes"] == 60
        
        # フィルタの確認
        assert len(config.filters) == 1
        assert config.filters[0]["type"] == "subject"
        
        # Spreadsheet設定の確認
        assert config.spreadsheet["spreadsheet_id"] == "test-id"
        assert config.spreadsheet["sheet_name"] == "テストシート"
        
        # ログ設定の確認
        assert config.log["level"] == "DEBUG"
        assert config.log["file"] == "/tmp/test.log"

    def test_env_variables(self, monkeypatch):
        """環境変数が正しく読み込めるか"""
        # 環境変数を設定
        monkeypatch.setenv("MAIL_USER", "test@example.com")
        monkeypatch.setenv("MAIL_PASSWORD", "testpass")
        
        # テスト用の設定ファイルを使用
        settings_file = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
        config = Config(settings_path=str(settings_file))
        
        env = config.env
        assert env["MAIL_USER"] == "test@example.com"
        assert env["MAIL_PASSWORD"] == "testpass"

    def test_default_log_values(self):
        """ログ設定のデフォルト値が設定されるか"""
        settings_file = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
        config = Config(settings_path=str(settings_file))
        
        log = config.log
        # settings.yamlにログ設定があればそれを使用、なければデフォルト値
        assert "level" in log
        assert "file" in log
