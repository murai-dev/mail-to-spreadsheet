"""generate_crontabモジュールの単体テスト"""

import pytest
from infra.generate_crontab import generate_cron_pattern, generate_crontab_line


class TestGenerateCrontab:
    """crontab生成機能のテスト"""

    def test_generate_cron_pattern_1min(self):
        """1分間隔のcronパターン生成"""
        assert generate_cron_pattern(1) == "*"

    def test_generate_cron_pattern_15min(self):
        """15分間隔のcronパターン生成"""
        assert generate_cron_pattern(15) == "*/15"

    def test_generate_cron_pattern_30min(self):
        """30分間隔のcronパターン生成"""
        assert generate_cron_pattern(30) == "*/30"

    def test_generate_cron_pattern_60min(self):
        """60分間隔のcronパターン生成"""
        assert generate_cron_pattern(60) == "0"

    def test_generate_cron_pattern_invalid(self):
        """サポートされていない間隔の場合はエラー"""
        with pytest.raises(ValueError):
            generate_cron_pattern(0)
        
        with pytest.raises(ValueError):
            generate_cron_pattern(-1)
        
        with pytest.raises(ValueError):
            generate_cron_pattern(45)

    def test_generate_crontab_line(self):
        """crontab行が正しく生成されるか"""
        line = generate_crontab_line(30)
        assert "*/30 * * * *" in line
        assert "root" in line
        assert "python -m src.main" in line
        assert "/var/log/mail-to-spreadsheet.log" in line
