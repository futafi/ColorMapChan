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
        各形式を順に試して適切なローダーを作成

        Args:
            file_path (str): CSVファイルのパス

        Returns:
            BaseDataLoader: 適切なデータローダーのインスタンス

        Raises:
            ValueError: すべての形式で読み込みに失敗した場合
        """
        errors = []

        # Sample2形式を試す
        try:
            loader = Sample2DataLoader(file_path)
            # 読み込みテスト
            loader.get_columns()  # 読み込みが成功したかテスト
            logger.info(f"ファイル '{file_path}' はSample2形式として読み込みました")
            return loader
        except Exception as e:
            errors.append(f"Sample2形式として読み込み失敗: {str(e)}")
            logger.debug(f"Sample2形式として読み込み失敗: {str(e)}")

        # Sample3形式を試す
        try:
            loader = Sample3DataLoader(file_path)
            # 読み込みテスト
            loader.get_columns()
            logger.info(f"ファイル '{file_path}' はSample3形式として読み込みました")
            return loader
        except Exception as e:
            errors.append(f"Sample3形式として読み込み失敗: {str(e)}")
            logger.debug(f"Sample3形式として読み込み失敗: {str(e)}")

        # 標準形式を試す
        try:
            loader = StandardDataLoader(file_path)
            # 読み込みテスト
            loader.get_columns()
            logger.info(f"ファイル '{file_path}' は標準CSV形式として読み込みました")
            return loader
        except Exception as e:
            errors.append(f"標準CSV形式として読み込み失敗: {str(e)}")
            logger.debug(f"標準CSV形式として読み込み失敗: {str(e)}")

        # すべての形式で失敗した場合
        error_msg = f"ファイル '{file_path}' はすべての形式で読み込みに失敗しました:\n" + "\n".join(errors)
        logger.error(error_msg)
        raise ValueError(error_msg)
