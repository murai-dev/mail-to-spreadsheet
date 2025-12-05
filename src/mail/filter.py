
from typing import List, Dict, Any

# メールフィルタ条件を管理し、各メールが条件に合致するか判定するクラス
class MailFilter:
    def __init__(self, filters: List[Dict[str, Any]]):
        """
        フィルタ条件リストを初期化
        Args:
            filters: フィルタ条件のリスト
        """
        self.filters = filters

    def match(self, mail: Dict[str, Any]) -> bool:
        """
        メールが全てのフィルタ条件を満たすか判定
        Args:
            mail: メール情報の辞書
        Returns:
            bool: 条件を満たせばTrue
        """
        for f in self.filters:
            # 件名の前方一致フィルタ
            if f["type"] == "subject" and f["condition"] == "prefix":
                if not mail["subject"].startswith(f["value"]):
                    return False
            # 送信元メールアドレスの完全一致フィルタ
            elif f["type"] == "from" and f["condition"] == "equals":
                if mail["from"] != f["value"]:
                    return False
            # 送信元メールアドレスの部分一致フィルタ
            elif f["type"] == "from" and f["condition"] == "contains":
                if f["value"] not in mail["from"]:
                    return False
            # 本文のキーワード完全一致フィルタ
            elif f["type"] == "body" and f["condition"] == "equals":
                if f["value"] not in mail.get("body", ""):
                    return False
            # 本文のキーワード部分一致フィルタ
            elif f["type"] == "body" and f["condition"] == "contains":
                if f["value"].lower() not in mail.get("body", "").lower():
                    return False
        return True
