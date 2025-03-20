"""
データローダーファクトリーモジュール

ファイル形式を自動検出し、適切なデータローダーを作成します。
"""

import os
import logging
from typing import Optional
from .base import BaseDataLoader
from .standard import StandardDataLoader
from .sample2 import Sample2DataLoader
from .sample3 import Sample3DataLoader

# ロガーの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
