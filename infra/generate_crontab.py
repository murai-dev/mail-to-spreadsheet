#!/usr/bin/env python3
"""crontab設定を自動生成するスクリプト

settings.yamlのcheck_interval_minutesに基づいて、
crontab実行パターンを自動生成する。
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import Config


def generate_cron_pattern(interval_minutes: int) -> str:
    """実行間隔に基づいてcronパターンを生成
    
    Args:
        interval_minutes: 実行間隔（分）
    
    Returns:
        str: cron形式のパターン（分フィールド）
    
    Raises:
        ValueError: サポートされていない間隔の場合
    """
    if interval_minutes <= 0:
        raise ValueError(f"実行間隔は1以上である必要があります: {interval_minutes}")
    
    # サポート間隔のチェック
    supported_intervals = [1, 15, 30, 60]
    if interval_minutes not in supported_intervals:
        raise ValueError(
            f"サポートされていない間隔です: {interval_minutes}分\n"
            f"サポート値: {', '.join(map(str, supported_intervals))}"
        )
    
    if interval_minutes == 1:
        return "*"
    elif interval_minutes == 60:
        return "0"
    else:
        return f"*/{interval_minutes}"


def generate_crontab_line(interval_minutes: int) -> str:
    """crontab実行行を生成
    
    Args:
        interval_minutes: 実行間隔（分）
    
    Returns:
        str: crontab実行行
    """
    cron_pattern = generate_cron_pattern(interval_minutes)
    
    # crontab行を生成
    # 形式: <分> <時> <日> <月> <曜日> root <コマンド>
    crontab_line = (
        f"{cron_pattern} * * * * root "
        f"cd /app && python -m src.main >> /var/log/mail-to-spreadsheet.log 2>&1"
    )
    
    return crontab_line


def main():
    """メイン処理"""
    try:
        # 設定を読み込み
        config = Config(settings_path=str(project_root / "config" / "settings.yaml"))
        interval = config.mail.get("check_interval_minutes")
        
        if interval is None:
            raise ValueError("check_interval_minutes が settings.yaml に見つかりません")
        
        # crontab行を生成
        crontab_line = generate_crontab_line(interval)
        
        # 標準出力に出力（シェルスクリプトから利用）
        print(crontab_line)
        
        return 0
        
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
