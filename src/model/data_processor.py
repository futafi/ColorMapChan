"""
データプロセッサーモジュール

データの処理、変換、正規化などを行うためのモジュールです。
"""

from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd


class DataProcessor:
    """
    データプロセッサークラス

    データの処理、変換、正規化などを行うためのクラスです。
    """

    def __init__(self):
        """データプロセッサーの初期化"""
        self.data: Optional[pd.DataFrame] = None
        self.processed_data: Optional[pd.DataFrame] = None
        self.x_column: Optional[str] = None
        self.y_column: Optional[str] = None
        self.value_column: Optional[str] = None
        self.filter_columns: Dict[str, float] = {}

    def set_data(self, data: pd.DataFrame) -> None:
        """
        処理対象のデータを設定します。

        Args:
            data (pd.DataFrame): 処理対象のデータフレーム
        """
        self.data = data.copy()
        self.processed_data = data.copy()

    def set_axes(self, x_column: str, y_column: str, value_column: str) -> None:
        """
        表示軸とデータ値の列を設定します。

        Args:
            x_column (str): X軸に表示する列名
            y_column (str): Y軸に表示する列名
            value_column (str): 値（カラーマップの色）として表示する列名
        """
        if self.data is None:
            raise ValueError("データが設定されていません。")

        if x_column not in self.data.columns:
            raise ValueError(f"X軸の列 '{x_column}' がデータに存在しません。")
        if y_column not in self.data.columns:
            raise ValueError(f"Y軸の列 '{y_column}' がデータに存在しません。")
        if value_column not in self.data.columns:
            raise ValueError(f"値の列 '{value_column}' がデータに存在しません。")

        self.x_column = x_column
        self.y_column = y_column
        self.value_column = value_column

    def set_filter(self, column: str, value: float) -> None:
        """
        フィルタリング条件を設定します。

        Args:
            column (str): フィルタリング対象の列名
            value (float): フィルタリング値
        """
        if self.data is None:
            raise ValueError("データが設定されていません。")

        if column not in self.data.columns:
            raise ValueError(f"フィルタ列 '{column}' がデータに存在しません。")

        self.filter_columns[column] = value

    def clear_filter(self, column: Optional[str] = None) -> None:
        """
        フィルタリング条件をクリアします。

        Args:
            column (Optional[str]): クリアする列名（Noneの場合はすべてクリア）
        """
        if column is None:
            self.filter_columns.clear()
        elif column in self.filter_columns:
            del self.filter_columns[column]

    def process_data(self) -> pd.DataFrame:
        """
        設定された条件に基づいてデータを処理します。

        Returns:
            pd.DataFrame: 処理後のデータフレーム
        """
        if self.data is None:
            raise ValueError("データが設定されていません。")

        if self.x_column is None or self.y_column is None or self.value_column is None:
            raise ValueError("軸と値の列が設定されていません。")

        # フィルタリング条件の適用
        filtered_data = self.data.copy()
        for column, value in self.filter_columns.items():
            # 近似値でフィルタリング（完全一致だと浮動小数点の誤差で問題が発生する可能性がある）
            filtered_data = filtered_data[np.isclose(filtered_data[column], value)]

        self.processed_data = filtered_data
        return self.processed_data

    def get_heatmap_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        ヒートマップ表示用のデータを取得します。

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: (X軸の値, Y軸の値, Z軸の値)
        """
        if self.processed_data is None or len(self.processed_data) == 0:
            raise ValueError("処理済みデータが存在しません。")

        if self.x_column is None or self.y_column is None or self.value_column is None:
            raise ValueError("軸と値の列が設定されていません。")

        # ユニークなX軸、Y軸の値を取得
        x_values = sorted(self.processed_data[self.x_column].unique())
        y_values = sorted(self.processed_data[self.y_column].unique())

        # メッシュグリッドの作成
        X, Y = np.meshgrid(x_values, y_values)

        # Z値の初期化（NaNで埋める）
        Z = np.full(X.shape, np.nan)

        # データポイントをマッピング
        for idx, row in self.processed_data.iterrows():
            x_idx = np.where(x_values == row[self.x_column])[0]
            y_idx = np.where(y_values == row[self.y_column])[0]
            if len(x_idx) > 0 and len(y_idx) > 0:
                Z[y_idx[0], x_idx[0]] = row[self.value_column]

        return X, Y, Z

    def get_value_range(self) -> Tuple[float, float]:
        """
        値（カラーマップの色）の範囲を取得します。

        Returns:
            Tuple[float, float]: (最小値, 最大値)
        """
        if self.processed_data is None or len(self.processed_data) == 0:
            raise ValueError("処理済みデータが存在しません。")

        if self.value_column is None:
            raise ValueError("値の列が設定されていません。")

        min_val = self.processed_data[self.value_column].min()
        max_val = self.processed_data[self.value_column].max()
        return min_val, max_val

    def get_axis_range(self, axis: str) -> Tuple[float, float]:
        """
        指定された軸の値の範囲を取得します。

        Args:
            axis (str): 軸の種類（'x' または 'y'）

        Returns:
            Tuple[float, float]: (最小値, 最大値)
        """
        if self.processed_data is None or len(self.processed_data) == 0:
            raise ValueError("処理済みデータが存在しません。")

        if axis.lower() == 'x':
            if self.x_column is None:
                raise ValueError("X軸の列が設定されていません。")
            column = self.x_column
        elif axis.lower() == 'y':
            if self.y_column is None:
                raise ValueError("Y軸の列が設定されていません。")
            column = self.y_column
        else:
            raise ValueError("軸の種類は 'x' または 'y' を指定してください。")

        min_val = self.processed_data[column].min()
        max_val = self.processed_data[column].max()
        return min_val, max_val
