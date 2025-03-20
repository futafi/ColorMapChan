"""
データフィルターモジュール

データのフィルタリングを行うためのモジュールです。
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd


class DataFilter:
    """
    データフィルタークラス

    データのフィルタリングを行うためのクラスです。
    """

    def __init__(self):
        """データフィルターの初期化"""
        self.data: Optional[pd.DataFrame] = None
        self.filtered_data: Optional[pd.DataFrame] = None
        self.filter_conditions: Dict[str, Any] = {}
        self.range_filters: Dict[str, Tuple[float, float]] = {}

    def set_data(self, data: pd.DataFrame) -> None:
        """
        フィルタリング対象のデータを設定します。

        Args:
            data (pd.DataFrame): フィルタリング対象のデータフレーム
        """
        self.data = data.copy()
        self.filtered_data = data.copy()

    def add_value_filter(self, column: str, value: Any) -> None:
        """
        特定の値でフィルタリングする条件を追加します。

        Args:
            column (str): フィルタリング対象の列名
            value (Any): フィルタリング値
        """
        if self.data is None:
            raise ValueError("データが設定されていません。")

        if column not in self.data.columns:
            raise ValueError(f"フィルタ列 '{column}' がデータに存在しません。")

        self.filter_conditions[column] = value

    def add_range_filter(self, column: str, min_val: float, max_val: float) -> None:
        """
        値の範囲でフィルタリングする条件を追加します。

        Args:
            column (str): フィルタリング対象の列名
            min_val (float): 最小値
            max_val (float): 最大値
        """
        if self.data is None:
            raise ValueError("データが設定されていません。")

        if column not in self.data.columns:
            raise ValueError(f"フィルタ列 '{column}' がデータに存在しません。")

        if min_val > max_val:
            min_val, max_val = max_val, min_val

        self.range_filters[column] = (min_val, max_val)

    def clear_filters(self, column: Optional[str] = None) -> None:
        """
        フィルタリング条件をクリアします。

        Args:
            column (Optional[str]): クリアする列名（Noneの場合はすべてクリア）
        """
        if column is None:
            self.filter_conditions.clear()
            self.range_filters.clear()
        else:
            if column in self.filter_conditions:
                del self.filter_conditions[column]
            if column in self.range_filters:
                del self.range_filters[column]

    def apply_filters(self) -> pd.DataFrame:
        """
        設定されたフィルタリング条件を適用します。

        Returns:
            pd.DataFrame: フィルタリング後のデータフレーム
        """
        if self.data is None:
            raise ValueError("データが設定されていません。")

        filtered_data = self.data.copy()

        # 値フィルタの適用
        for column, value in self.filter_conditions.items():
            if isinstance(value, (int, float)):
                # 数値の場合は近似値でフィルタリング
                filtered_data = filtered_data[np.isclose(filtered_data[column], value)]
            else:
                # その他の型は完全一致でフィルタリング
                filtered_data = filtered_data[filtered_data[column] == value]

        # 範囲フィルタの適用
        for column, (min_val, max_val) in self.range_filters.items():
            filtered_data = filtered_data[
                (filtered_data[column] >= min_val) & (filtered_data[column] <= max_val)
            ]

        self.filtered_data = filtered_data
        return self.filtered_data

    def get_unique_values(self, column: str) -> List[Any]:
        """
        指定された列のユニークな値のリストを取得します。

        Args:
            column (str): 列名

        Returns:
            List[Any]: ユニークな値のリスト
        """
        if self.data is None:
            raise ValueError("データが設定されていません。")

        if column not in self.data.columns:
            raise ValueError(f"列 '{column}' がデータに存在しません。")

        return sorted(self.data[column].unique().tolist())

    def get_column_range(self, column: str) -> Tuple[float, float]:
        """
        指定された列の値の範囲を取得します。

        Args:
            column (str): 列名

        Returns:
            Tuple[float, float]: (最小値, 最大値)
        """
        if self.data is None:
            raise ValueError("データが設定されていません。")

        if column not in self.data.columns:
            raise ValueError(f"列 '{column}' がデータに存在しません。")

        if not pd.api.types.is_numeric_dtype(self.data[column]):
            raise ValueError(f"列 '{column}' は数値型ではありません。")

        min_val = self.data[column].min()
        max_val = self.data[column].max()
        return min_val, max_val

    def get_filtered_data(self) -> pd.DataFrame:
        """
        現在のフィルタリング結果を取得します。

        Returns:
            pd.DataFrame: フィルタリング後のデータフレーム
        """
        if self.filtered_data is None:
            raise ValueError("フィルタリング結果が存在しません。")

        return self.filtered_data.copy()

    def get_filter_summary(self) -> Dict[str, Any]:
        """
        現在のフィルタリング条件の概要を取得します。

        Returns:
            Dict[str, Any]: フィルタリング条件の概要
        """
        summary = {
            "value_filters": self.filter_conditions.copy(),
            "range_filters": self.range_filters.copy(),
            "filtered_rows": len(self.filtered_data) if self.filtered_data is not None else 0,
            "total_rows": len(self.data) if self.data is not None else 0
        }
        return summary
