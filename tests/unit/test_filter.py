"""MailFilterクラスの単体テスト"""

import pytest
from src.mail.filter import MailFilter


class TestMailFilter:
    """MailFilterクラスのテスト"""

    def test_subject_prefix_match(self):
        """件名の前方一致フィルタが正しく動作するか"""
        filters = [
            {"type": "subject", "condition": "prefix", "value": "【重要】"}
        ]
        mail_filter = MailFilter(filters)
        
        # マッチするケース
        mail = {"subject": "【重要】会議のお知らせ", "from": "test@example.com"}
        assert mail_filter.match(mail) is True
        
        # マッチしないケース
        mail = {"subject": "通常のメール", "from": "test@example.com"}
        assert mail_filter.match(mail) is False

    def test_from_equals_match(self):
        """送信元メールアドレスの完全一致フィルタが正しく動作するか"""
        filters = [
            {"type": "from", "condition": "equals", "value": "test@example.com"}
        ]
        mail_filter = MailFilter(filters)
        
        # マッチするケース
        mail = {"subject": "テスト", "from": "test@example.com"}
        assert mail_filter.match(mail) is True
        
        # マッチしないケース
        mail = {"subject": "テスト", "from": "other@example.com"}
        assert mail_filter.match(mail) is False

    def test_from_contains_match(self):
        """送信元メールアドレスの部分一致フィルタが正しく動作するか"""
        filters = [
            {"type": "from", "condition": "contains", "value": "@example.com"}
        ]
        mail_filter = MailFilter(filters)
        
        # マッチするケース
        mail = {"subject": "テスト", "from": "test@example.com"}
        assert mail_filter.match(mail) is True
        
        mail = {"subject": "テスト", "from": "admin@example.com"}
        assert mail_filter.match(mail) is True
        
        # マッチしないケース
        mail = {"subject": "テスト", "from": "test@other.com"}
        assert mail_filter.match(mail) is False

    def test_multiple_filters_all_match(self):
        """複数のフィルタが全て満たされる場合"""
        filters = [
            {"type": "subject", "condition": "prefix", "value": "【重要】"},
            {"type": "from", "condition": "contains", "value": "@example.com"}
        ]
        mail_filter = MailFilter(filters)
        
        # 全て満たすケース
        mail = {"subject": "【重要】会議", "from": "test@example.com"}
        assert mail_filter.match(mail) is True
        
        # 一部だけ満たすケース（件名のみ）
        mail = {"subject": "【重要】会議", "from": "test@other.com"}
        assert mail_filter.match(mail) is False
        
        # 一部だけ満たすケース（送信元のみ）
        mail = {"subject": "通常のメール", "from": "test@example.com"}
        assert mail_filter.match(mail) is False

    def test_empty_filters(self):
        """フィルタが空の場合、全てのメールがマッチする"""
        mail_filter = MailFilter([])
        
        mail = {"subject": "テスト", "from": "test@example.com"}
        assert mail_filter.match(mail) is True

    def test_body_contains_match(self):
        """本文のキーワード部分一致フィルタが正しく動作するか"""
        filters = [
            {"type": "body", "condition": "contains", "value": "重要"}
        ]
        mail_filter = MailFilter(filters)
        
        # マッチするケース
        mail = {"subject": "テスト", "from": "test@example.com", "body": "これは重要なメールです"}
        assert mail_filter.match(mail) is True
        
        # 大文字小文字を区別しないテスト
        mail = {"subject": "テスト", "from": "test@example.com", "body": "This is 重要 message"}
        assert mail_filter.match(mail) is True
        
        # マッチしないケース
        mail = {"subject": "テスト", "from": "test@example.com", "body": "通常のメール内容"}
        assert mail_filter.match(mail) is False

    def test_body_equals_match(self):
        """本文のキーワード完全一致フィルタが正しく動作するか"""
        filters = [
            {"type": "body", "condition": "equals", "value": "警告"}
        ]
        mail_filter = MailFilter(filters)
        
        # マッチするケース
        mail = {"subject": "テスト", "from": "test@example.com", "body": "警告:エラーが発生しました"}
        assert mail_filter.match(mail) is True
        
        # マッチしないケース
        mail = {"subject": "テスト", "from": "test@example.com", "body": "通常のメール内容"}
        assert mail_filter.match(mail) is False

    def test_multiple_filters_with_body(self):
        """本文を含む複数のフィルタが正しく動作するか"""
        filters = [
            {"type": "subject", "condition": "prefix", "value": "【重要】"},
            {"type": "body", "condition": "contains", "value": "重要"}
        ]
        mail_filter = MailFilter(filters)
        
        # 全て満たすケース
        mail = {
            "subject": "【重要】会議のお知らせ",
            "from": "test@example.com",
            "body": "これは重要な会議です"
        }
        assert mail_filter.match(mail) is True
        
        # 件名は満たすが本文は満たさないケース
        mail = {
            "subject": "【重要】会議のお知らせ",
            "from": "test@example.com",
            "body": "通常の会議です"
        }
        assert mail_filter.match(mail) is False
