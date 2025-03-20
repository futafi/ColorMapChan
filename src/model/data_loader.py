"""
データローダーモジュール

CSVファイルからデータを読み込み、効率的に処理するためのモジュールです。
大規模なデータセットを扱うため、チャンク読み込みを実装しています。
複数の形式のCSVファイルに対応しています。
"""

import os
import logging
from typing import Dict, Optional, List, Tuple
import pandas as pd
import numpy as np
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
            with open(self.file_path, 'r') as f:
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
            with open(self.file_path, 'r', encoding='utf-8') as f:
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


class DataLoaderFactory:
    """
    データローダーファクトリークラス

    ファイル形式を自動検出し、適切なデータローダーを作成します。
    """

    # ファイル形式の定数
    FORMAT_STANDARD = "standard"
    FORMAT_SAMPLE2 = "sample2"
    FORMAT_SAMPLE3 = "sample3"

    @staticmethod
    def create_data_loader(file_path: str, format_type: Optional[str] = None) -> BaseDataLoader:
        """
        適切なデータローダーを作成します。

        Args:
            file_path (str): CSVファイルのパス
            format_type (Optional[str]): 手動で指定するファイル形式
                                        (None, "standard", "sample2", "sample3")

        Returns:
            BaseDataLoader: 適切なデータローダーのインスタンス
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")

        if format_type:
            # 手動指定された形式に基づいてローダーを作成
            if format_type == DataLoaderFactory.FORMAT_STANDARD:
                return StandardDataLoader(file_path)
            elif format_type == DataLoaderFactory.FORMAT_SAMPLE2:
                return Sample2DataLoader(file_path)
            elif format_type == DataLoaderFactory.FORMAT_SAMPLE3:
                return Sample3DataLoader(file_path)
            else:
                raise ValueError(f"不明なファイル形式: {format_type}")
        else:
            # 自動検出
            return DataLoaderFactory._detect_and_create(file_path)

    @staticmethod
    def _detect_and_create(file_path: str) -> BaseDataLoader:
        """
        ファイル内容を分析して適切なローダーを作成

        Args:
            file_path (str): CSVファイルのパス

        Returns:
            BaseDataLoader: 適切なデータローダーのインスタンス
        """
        try:
            # ファイルの先頭部分を読み込む
            with open(file_path, 'r', encoding='utf-8') as f:
                header_lines = [f.readline() for _ in range(20)]  # 先頭20行を読み込む

            # Sample2形式の特徴を検出
            if any(line.startswith('DataName') for line in header_lines):
                logger.info(f"ファイル '{file_path}' はSample2形式と判定されました")
                return Sample2DataLoader(file_path)

            # Sample3形式の特徴を検出
            if any(line.startswith('AutoAnalysis.Marker.Data.StartCondition') for line in header_lines):
                logger.info(f"ファイル '{file_path}' はSample3形式と判定されました")
                return Sample3DataLoader(file_path)

            # 上記に該当しない場合は標準CSV形式と判断
            logger.info(f"ファイル '{file_path}' は標準CSV形式と判定されました")
            return StandardDataLoader(file_path)

        except Exception as e:
            logger.error(f"ファイル形式の検出中にエラーが発生しました: {str(e)}")
            # エラーが発生した場合は標準形式を試す
            logger.info("標準CSV形式として読み込みを試みます")
            return StandardDataLoader(file_path)


# 後方互換性のためのエイリアス
DataLoader = StandardDataLoader
