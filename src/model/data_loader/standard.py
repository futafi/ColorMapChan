"""
標準データローダーモジュール

標準的なCSVファイルを読み込むためのモジュールです。
"""

import logging
from typing import Optional, Tuple
import pandas as pd
from .base import BaseDataLoader

# ロガーの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StandardDataLoader(BaseDataLoader):
    """
    標準データローダークラス

    標準的なCSVファイルを読み込むためのクラスです。
    大規模なデータセットに対応するため、チャンク読み込みを実装しています。
    """

    def __init__(self, file_path: Optional[str] = None):
        """
        標準データローダーの初期化

        Args:
            file_path (Optional[str]): CSVファイルのパス
        """
        super().__init__(file_path)
        self.chunk_size: int = 1000  # デフォルトのチャンクサイズ
        self.current_chunk: Optional[pd.DataFrame] = None

        if file_path:
            self._analyze_file()

    def _analyze_file(self) -> None:
        """
        ファイルを解析し、ヘッダー情報とデータ構造を取得します。
        """
        if not self.file_path:
            raise ValueError("ファイルパスが設定されていません。")

        try:
            # ファイルの行数を取得
            with open(self.file_path, 'r') as f:
                self.total_rows = sum(1 for _ in f)

            # ヘッダー情報の解析
            chunk = pd.read_csv(self.file_path, nrows=1)
            self.columns = list(chunk.columns)
            self.data_columns = [col for col in self.columns]

            logger.info(f"標準CSVファイル '{self.file_path}' を解析しました。列数: {len(self.columns)}, 行数: {self.total_rows}")
        except Exception as e:
            logger.error(f"ファイル '{self.file_path}' の解析中にエラーが発生しました: {str(e)}")
            raise ValueError(f"ファイルの解析に失敗しました: {str(e)}")

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

        try:
            # skiprowsで開始位置を指定し、nrowsでチャンクサイズを指定
            chunk = pd.read_csv(
                self.file_path,
                skiprows=range(1, start + 1) if start > 0 else None,
                nrows=chunk_size
            )

            # 最後のチャンクかどうかを判定
            is_last = (start + len(chunk)) >= self.total_rows

            return chunk, is_last
        except Exception as e:
            logger.error(f"チャンク読み込み中にエラーが発生しました: {str(e)}")
            raise ValueError(f"データの読み込みに失敗しました: {str(e)}")

    def load_all_data(self) -> pd.DataFrame:
        """
        ファイルからすべてのデータを読み込みます。

        Returns:
            pd.DataFrame: 読み込まれた全データのデータフレーム
        """
        if not self.file_path:
            raise ValueError("ファイルパスが設定されていません。")

        try:
            logger.info(f"ファイル '{self.file_path}' の全データを読み込みます。")

            # 一度にすべてのデータを読み込む
            df = pd.read_csv(self.file_path)

            logger.info(f"全データを読み込みました: {len(df)}行, {len(df.columns)}列")
            return df

        except Exception as e:
            logger.error(f"全データ読み込み中にエラーが発生しました: {str(e)}")
            raise ValueError(f"全データの読み込みに失敗しました: {str(e)}")
