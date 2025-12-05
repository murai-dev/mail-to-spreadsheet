# 標準ライブラリ
import os
# サードパーティ
import yaml
from dotenv import load_dotenv


# 設定ファイル（YAML）と環境変数（.env）を読み込む設定管理クラス
class Config:
    def __init__(self, settings_path: str = "config/settings.yaml"):
        """
        設定を初期化
        Args:
            settings_path: settings.yamlのパス（デフォルト: config/settings.yaml）
        """
        # .envファイルを読み込む（環境変数を利用可能に）
        load_dotenv()
        self.settings_path = settings_path
        self._settings = self._load_settings()  # YAML設定を辞書として保持

    def _load_settings(self):
        """
        YAML設定ファイルを読み込む
        Returns:
            dict: 設定内容
        """
        with open(self.settings_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)


    @property
    def mail(self):
        """
        メール関連の設定（IMAPホスト・ポート等）
        Returns:
            dict
        """
        return self._settings.get("mail", {})


    @property
    def filters(self):
        """
        メールフィルタ条件リスト
        Returns:
            list
        """
        return self._settings.get("filters", [])


    @property
    def spreadsheet(self):
        """
        Google Spreadsheet関連の設定
        Returns:
            dict
        """
        return self._settings.get("spreadsheet", {})

    @property
    def log(self):
        """
        ログ設定
        Returns:
            dict
        """
        return self._settings.get("log", {
            "level": "INFO",
            "file": "/var/log/mail-to-spreadsheet.log"
        })

    @property
    def line(self):
        """
        LINE設定
        Returns:
            dict
        """
        return self._settings.get("line", {
            "enabled": False,
        })

    @property
    def env(self):
        """
        機密情報や環境依存値を環境変数から取得
        Returns:
            dict
        """
        return {
            "MAIL_USER": os.getenv("MAIL_USER"),  # メールアカウント
            "MAIL_PASSWORD": os.getenv("MAIL_PASSWORD"),  # メールパスワード
            "GOOGLE_SERVICE_ACCOUNT_FILE": os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE"),  # サービスアカウント認証ファイル
            "LINE_CHANNEL_ACCESS_TOKEN": os.getenv("LINE_CHANNEL_ACCESS_TOKEN"),  # LINE Channel Access Token
            "LINE_CHANNEL_SECRET": os.getenv("LINE_CHANNEL_SECRET"),  # LINE Channel Secret
        }
