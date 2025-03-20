"""
基本データローダーモジュール

データローダーの基底クラスを定義します。
"""

import logging
from typing import Dict, Optional, List, Tuple
import pandas as pd
from abc import ABC, abstractmethod

# ロガーの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseDataLoader(ABC):
    """
    基本データローダー抽象クラス

    すべてのデータローダーの基底クラスです。
    共通の属性とメソッドを定義します。
    """

    def __init__(self, file_path: Optional[str] = None):
        """
        基本データローダーの初期化

        Args:
            file_path (Optional[str]): CSVファイルのパス
        """
        self.file_path: Optional[str] = file_path
        self.header_info: Dict = {}
        self.columns: List[str] = []
        self.data_columns: List[str] = []
        self.total_rows: int = 0
        self.df: Optional[pd.DataFrame] = None

    def set_file(self, file_path: str) -> None:
        """
        処理対象のファイルを設定します。

        Args:
            file_path (str): CSVファイルのパス
        """
        self.file_path = file_path
        self._analyze_file()

    @abstractmethod
    def _analyze_file(self) -> None:
        """
        ファイルを解析し、ヘッダー情報とデータ構造を取得します。
        派生クラスでオーバーライドする必要があります。
        """
        pass

    def get_columns(self) -> List[str]:
        """
        データの列名リストを取得します。

        Returns:
            List[str]: 列名のリスト
        """
        return self.columns

    def get_total_rows(self) -> int:
        """
        データの総行数を取得します。

        Returns:
            int: データの総行数
        """
        return self.total_rows

    def get_header_info(self) -> Dict:
        """
        ヘッダー情報を取得します。

        Returns:
            Dict: ヘッダー情報の辞書
        """
        return self.header_info

    @abstractmethod
    def load_all_data(self) -> pd.DataFrame:
        """
        ファイルからすべてのデータを読み込みます。
        派生クラスでオーバーライドする必要があります。

        Returns:
            pd.DataFrame: 読み込まれた全データのデータフレーム
        """
        pass

    @abstractmethod
    def get_chunk(self, start: int, size: Optional[int] = None) -> Tuple[pd.DataFrame, bool]:
        """
        指定された位置からデータのチャンクを読み込みます。
        派生クラスでオーバーライドする必要があります。

        Args:
            start (int): 開始位置（行番号）
            size (Optional[int]): チャンクサイズ（指定がない場合はデフォルト値を使用）

        Returns:
            Tuple[pd.DataFrame, bool]: (データチャンク, 最後のチャンクかどうか)
        """
        pass
