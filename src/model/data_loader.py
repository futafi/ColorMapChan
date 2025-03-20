"""
データローダーモジュール

CSVファイルからデータを読み込み、効率的に処理するためのモジュールです。
大規模なデータセットを扱うため、チャンク読み込みを実装しています。
"""

from typing import Dict, Optional, List, Tuple
import pandas as pd


class DataLoader:
    """
    データローダークラス

    CSVファイルからデータを読み込み、効率的に処理するためのクラスです。
    大規模なデータセットに対応するため、チャンク読み込みを実装しています。
    """

    def __init__(self):
        """データローダーの初期化"""
        self.file_path: Optional[str] = None
        self.chunk_size: int = 1000  # デフォルトのチャンクサイズ
        self.header_info: Dict = {}
        self.columns: List[str] = []
        self.data_columns: List[str] = []
        self.current_chunk: Optional[pd.DataFrame] = None
        self.total_rows: int = 0

    def set_file(self, file_path: str) -> None:
        """
        処理対象のファイルを設定します。

        Args:
            file_path (str): CSVファイルのパス
        """
        self.file_path = file_path
        self._analyze_file()

    def _analyze_file(self) -> None:
        """
        ファイルを解析し、ヘッダー情報とデータ構造を取得します。
        """
        if not self.file_path:
            raise ValueError("ファイルパスが設定されていません。")

        # ファイルの行数を取得
        with open(self.file_path, 'r') as f:
            self.total_rows = sum(1 for _ in f)

        # ヘッダー情報の解析
        chunk = pd.read_csv(self.file_path, nrows=1)
        self.columns = list(chunk.columns)
        self.data_columns = [col for col in self.columns]

    def get_chunk(self, start: int, size: Optional[int] = None) -> Tuple[pd.DataFrame, bool]:
        """
        指定された位置からデータのチャンクを読み込みます。

        Args:
            start (int): 開始位置（行番号）
            size (Optional[int]): チャンクサイズ（指定がない場合はデフォルト値を使用）

        Returns:
            Tuple[pd.DataFrame, bool]: (データチャンク, 最後のチャンクかどうか)
        """
        if not self.file_path:
            raise ValueError("ファイルパスが設定されていません。")

        chunk_size = size if size is not None else self.chunk_size

        # skiprowsで開始位置を指定し、nrowsでチャンクサイズを指定
        chunk = pd.read_csv(
            self.file_path,
            skiprows=range(1, start + 1) if start > 0 else None,
            nrows=chunk_size
        )

        # 最後のチャンクかどうかを判定
        is_last = (start + len(chunk)) >= self.total_rows

        return chunk, is_last

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
