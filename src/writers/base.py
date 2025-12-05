
from abc import ABC, abstractmethod

# データ書き込み機能の共通インターフェイスを定義する抽象クラス
# SpreadsheetWriter等が継承し、各媒体への書き込みを実装
class BaseWriter(ABC):
    @abstractmethod
    def write(self, data):
        """
        データを書き込む抽象メソッド
        各サブクラスで実装必須
        Args:
            data: 書き込むデータ
        """
        pass
