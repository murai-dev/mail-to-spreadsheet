"""統合テスト用の設定とヘルパー

統合テストは実際のメールアカウントとSpreadsheetを使用します。
環境変数で切り替え可能にし、CI/CD環境では実行をスキップできます。
"""

import os
import pytest


def is_integration_test_enabled():
    """統合テストが有効かどうか"""
    return os.getenv("RUN_INTEGRATION_TESTS", "false").lower() == "true"


skip_integration = pytest.mark.skipif(
    not is_integration_test_enabled(),
    reason="統合テストはRUN_INTEGRATION_TESTS=trueの場合のみ実行されます"
)
