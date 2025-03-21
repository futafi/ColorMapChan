"""
Sample3データローダーモジュール

Sample3形式のCSVファイル（B1500aSingleFileCSV形式）を読み込むためのモジュールです。
"""

import logging
from typing import List, Optional, Tuple
import pandas as pd
import numpy as np
from .base import BaseDataLoader

# ロガーの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Sample3DataLoader(BaseDataLoader):
    """
    Sample3データローダークラス

    Sample3形式のCSVファイル（B1500aSingleFileCSV形式）を読み込むためのクラスです。
    """

    def __init__(self, file_path: Optional[str] = None):
        """
        Sample3データローダーの初期化

        Args:
            file_path (Optional[str]): CSVファイルのパス
        """
        super().__init__(file_path)
        self.raw_data: List[str] = []
        self.auto_analysis_start: int = -1
        self.data_section_start: int = -1

        if file_path:
            self._analyze_file()

    def _analyze_file(self) -> None:
        """
        ファイルを解析し、ヘッダー情報とデータ構造を取得します。
        """
        if not self.file_path:
            raise ValueError("ファイルパスが設定されていません。")

        try:
            self._read_file()
            self._parse_header()
            self._extract_data()
            self.columns = list(self.df.columns)
            self.data_columns = self.columns
            self.total_rows = len(self.df)

            logger.info(f"Sample3形式ファイル '{self.file_path}' を解析しました。列数: {len(self.columns)}, 行数: {self.total_rows}")
        except Exception as e:
            logger.error(f"ファイル '{self.file_path}' の解析中にエラーが発生しました: {str(e)}")
            raise ValueError(f"Sample3形式ファイルの解析に失敗しました: {str(e)}")

    def _read_file(self) -> None:
        """ファイルを読み込む"""
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='replace') as f:
                self.raw_data = f.readlines()
                self.total_rows = len(self.raw_data)
            logger.info(f"ファイル '{self.file_path}' を読み込みました。行数: {self.total_rows}")
        except Exception as e:
            logger.error(f"ファイル読み込み中にエラーが発生しました: {str(e)}")
            raise ValueError(f"ファイルの読み込みに失敗しました: {str(e)}")

    def _parse_header(self) -> None:
        """
        ヘッダー情報を解析する
        - AutoAnalysisまでの行をヘッダーとする
        - 行の形式は「キー,値」
        """
        try:
            for i, line in enumerate(self.raw_data):
                line = line.strip()

                # AutoAnalysis行でヘッダーセクションの終わりを検出
                if line.startswith('AutoAnalysis.Marker.Data.StartCondition,'):
                    self.auto_analysis_start = i

                # データセクションの開始行を検出
                if ',' in line and not self.columns and self.auto_analysis_start > 0 and i > self.auto_analysis_start:
                    potential_columns = [col.strip() for col in line.split(',')]
                    # データセクションの開始行は列名の行
                    if len(potential_columns) > 1:
                        self.columns = potential_columns
                        self.data_section_start = i
                        break

                # ヘッダー情報を抽出
                if ',' in line and self.auto_analysis_start < 0:
                    parts = line.split(',', 1)
                    if len(parts) == 2:
                        key, value = parts
                        self.header_info[key.strip()] = value.strip()

            if self.data_section_start < 0:
                raise ValueError("データセクションが見つかりませんでした")

            logger.info("ヘッダーを解析しました")

        except Exception as e:
            logger.error(f"ヘッダー解析中にエラーが発生しました: {str(e)}")
            raise ValueError(f"ヘッダーの解析に失敗しました: {str(e)}")

    def _extract_data(self) -> None:
        """
        データセクションからデータを抽出する
        - 列名の行の次の行からが実際のデータ
        """
        try:
            # データ行を抽出
            data_lines = []
            for line in self.raw_data[self.data_section_start + 1:]:
                line = line.strip()
                if line and ',' in line:
                    values = line.split(',')
                    values = [np.nan if v == '' else v for v in values]
                    data_lines.append(values)

            # DataFrameを作成
            self.df = pd.DataFrame(data_lines, columns=self.columns)

            # 数値データの列を数値型に変換
            for col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

            logger.info(f"データを抽出しました: {len(self.df)}行, {len(self.columns)}列")

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
        Sample3形式の場合は、すでに解析時に全データが読み込まれているため、
        そのデータフレームを返します。

        Returns:
            pd.DataFrame: 読み込まれた全データのデータフレーム
        """
        if self.df is None:
            if not self.file_path:
                raise ValueError("ファイルパスが設定されていません。")

            # ファイルを解析して全データを読み込む
            self._analyze_file()

        logger.info(f"Sample3形式ファイル '{self.file_path}' の全データを返します: {len(self.df)}行")
        return self.df.copy()
