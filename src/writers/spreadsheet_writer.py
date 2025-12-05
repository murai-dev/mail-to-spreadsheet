
# 標準ライブラリ
import logging
# サードパーティ
import gspread
from google.oauth2.service_account import Credentials
from .base import BaseWriter

# Google Spreadsheetへのデータ書き込みを担当するクラス
class SpreadsheetWriter(BaseWriter):
    def __init__(self, spreadsheet_id, sheet_name, service_account_file, columns):
        """
        SpreadsheetWriter初期化
        Args:
            spreadsheet_id: SpreadsheetのID
            sheet_name: シート名
            service_account_file: Google認証ファイルパス
            columns: 記録するカラム名のリスト
        """
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.service_account_file = service_account_file
        self.columns = columns
        self.gc = None  # gspreadクライアント
        self.sheet = None  # ワークシートオブジェクト
        self.logger = logging.getLogger("spreadsheet")

    def authenticate(self):
        """
        Google Sheets APIに認証・接続
        サービスアカウントのJSONファイルを使用
        """
        # Google APIのスコープを指定
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive',
        ]
        # サービスアカウントで認証
        creds = Credentials.from_service_account_file(self.service_account_file, scopes=scopes)
        self.gc = gspread.authorize(creds)
        # 指定されたSpreadsheetとシートを開く
        self.sheet = self.gc.open_by_key(self.spreadsheet_id).worksheet(self.sheet_name)
        self.logger.info("Connected to Google Sheets API")
        self.ensure_headers()

    def ensure_headers(self):
        """
        ヘッダー行を確認・作成
        既存のヘッダーがカラム定義と異なる場合は更新
        """
        headers = self.sheet.row_values(1)
        if headers != self.columns:
            # 古いヘッダーを削除して新規作成
            self.sheet.delete_rows(1)
            self.sheet.insert_row(self.columns, 1)
            self.logger.info("Headers updated")

    def write(self, data):
        """
        Spreadsheetに行を追加
        Args:
            data: 書き込むデータ（辞書）
        """
        # columnsで指定されたカラムの順序でデータを抽出
        row = [data.get(col, "") for col in self.columns]
        self.sheet.append_row(row)
        self.logger.info(f"Row written: {row}")
