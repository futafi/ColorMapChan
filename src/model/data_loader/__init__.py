"""
データローダーパッケージ

CSVファイルからデータを読み込み、効率的に処理するためのパッケージです。
大規模なデータセットを扱うため、チャンク読み込みを実装しています。
複数の形式のCSVファイルに対応しています。
"""

from src.model.data_loader.base import BaseDataLoader
from src.model.data_loader.standard import StandardDataLoader
from src.model.data_loader.sample2 import Sample2DataLoader
from src.model.data_loader.sample3 import Sample3DataLoader
from src.model.data_loader.factory import DataLoaderFactory

# 後方互換性のためのエイリアス
DataLoader = StandardDataLoader

__all__ = [
    'BaseDataLoader',
    'StandardDataLoader',
    'Sample2DataLoader',
    'Sample3DataLoader',
    'DataLoaderFactory',
    'DataLoader',
]
