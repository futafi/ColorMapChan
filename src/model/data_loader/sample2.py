"""
Sample2データローダーモジュール

Sample2形式のCSVファイル（B1500Atext2csv形式）を読み込むためのモジュールです。
"""

import logging
from typing import List, Optional, Tuple
import pandas as pd
from .base import BaseDataLoader

# ロガーの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Sample2DataLoader(BaseDataLoader):
    """
    Sample2データローダークラス

    Sample2形式のCSVファイル（B1500Atext2csv形式）を読み込むためのクラスです。
    """

    def __init__(self, file_path: Optional[str] = None):
        """
        Sample2データローダーの初期化

        Args:
            file_path (Optional[str]): CSVファイルのパス
        """
        super().__init__(file_path)
        self.data_start_index: Optional[int] = None

        if file_path:
            self._analyze_file()

    def _analyze_file(self) -> None:
        """
        ファイルを解析し、ヘッダー情報とデータ構造を取得します。
        """
        if not self.file_path:
            raise ValueError("ファイルパスが設定されていません。")

        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='replace') as f:
                raw_data = f.readlines()
                self.total_rows = len(raw_data)

            # ヘッダー解析
            self._parse_header(raw_data)

            # データ抽出
            self.df = self._extract_data(raw_data)
            self.columns = list(self.df.columns)
            self.data_columns = self.columns

            logger.info(f"Sample2形式ファイル '{self.file_path}' を解析しました。列数: {len(self.columns)}, 行数: {len(self.df)}")
        except Exception as e:
            logger.error(f"ファイル '{self.file_path}' の解析中にエラーが発生しました: {str(e)}")
            raise ValueError(f"Sample2形式ファイルの解析に失敗しました: {str(e)}")

    def _parse_header(self, raw_data: List[str]) -> None:
        """
        ヘッダー部分の解析

        Args:
            raw_data (List[str]): ファイルの生データ
        """
        try:
            for i, line in enumerate(raw_data):
                if line.startswith('DataName'):
                    self.data_start_index = i
                    break

                if line.startswith('TestParameter') or \
                   line.startswith('MetaData') or \
                   line.startswith('AnalysisSetup'):
                    parts = line.strip().split(',', 1)
                    if len(parts) == 2:
                        key, value = parts
                        self.header_info[key.strip()] = value.strip()

            if self.data_start_index is None:
                raise ValueError("データセクションが見つかりませんでした")

        except Exception as e:
            logger.error(f"ヘッダー解析中にエラーが発生しました: {str(e)}")
            raise ValueError(f"ヘッダーの解析に失敗しました: {str(e)}")

    def _extract_data(self, raw_data: List[str]) -> pd.DataFrame:
        """
        測定データ部分の抽出

        Args:
            raw_data (List[str]): ファイルの生データ

        Returns:
            pd.DataFrame: 抽出されたデータフレーム
        """
        try:
            # カラム名の取得
            columns = [col.strip() for col in raw_data[self.data_start_index].strip().split(',')[1:]]

            # データの抽出
            data_lines = []
            for line in raw_data[self.data_start_index + 1:]:
                if line.startswith('DataValue'):
                    values = line.strip().split(',')[1:]
                    # 空の文字列を0に変換
                    values = [v if v.strip() else '0' for v in values]
                    data_lines.append(values)

            # DataFrameの作成
            df = pd.DataFrame(data_lines, columns=columns)

            # データ型の変換
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            return df

        except Exception as e:
            logger.error(f"データ抽出中にエラーが発生しました: {str(e)}")
            raise ValueError(f"データの抽出に失敗しました: {str(e)}")

    def get_chunk(self, start: int, size: Optional[int] = None) -> Tuple[pd.DataFrame, bool]:
        """
        指定された位置からデータのチャンクを読み込みます。

        Args:
            start (int): 開始位置（行番号）
            size (Optional[int]): チャンクサイズ（指定がない場合はデフォルト値を使用）

        Returns:
            Tuple[pd.DataFrame, bool]: (データチャンク, 最後のチャンクかどうか)
        """
        if self.df is None:
            raise ValueError("データが読み込まれていません。")

        chunk_size = size if size is not None else 1000
        end = min(start + chunk_size, len(self.df))

        # データフレームから指定範囲を切り出し
        chunk = self.df.iloc[start:end].copy()

        # 最後のチャンクかどうかを判定
        is_last = end >= len(self.df)

        return chunk, is_last

    def load_all_data(self) -> pd.DataFrame:
        """
        ファイルからすべてのデータを読み込みます。
        Sample2形式の場合は、すでに解析時に全データが読み込まれているため、
        そのデータフレームを返します。

        Returns:
            pd.DataFrame: 読み込まれた全データのデータフレーム
        """
        if self.df is None:
            if not self.file_path:
                raise ValueError("ファイルパスが設定されていません。")

            # ファイルを解析して全データを読み込む
            self._analyze_file()

        logger.info(f"Sample2形式ファイル '{self.file_path}' の全データを返します: {len(self.df)}行")
        return self.df.copy()
