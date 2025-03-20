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

        # キャッシュ用の変数
        self._cache: Dict[str, any] = {}
        self._cache_invalidated: bool = True

    def _invalidate_cache(self) -> None:
        """キャッシュを無効化します。"""
        self._cache.clear()
        self._cache_invalidated = True

    def set_data(self, data: pd.DataFrame) -> None:
        """
        処理対象のデータを設定します。

        Args:
            data (pd.DataFrame): 処理対象のデータフレーム
        """
        self.data = data.copy()
        self.processed_data = data.copy()
        self._invalidate_cache()

    def _get_cache_key(self, prefix: str) -> str:
        """
        キャッシュのキーを生成します。

        Args:
            prefix (str): キーのプレフィックス

        Returns:
            str: キャッシュキー
        """
        # 現在の状態に基づいてキーを生成
        key_parts = [prefix]

        if self.x_column:
            key_parts.append(f"x:{self.x_column}")
        if self.y_column:
            key_parts.append(f"y:{self.y_column}")
        if self.value_column:
            key_parts.append(f"v:{self.value_column}")

        # フィルター条件をキーに含める
        for column, value in sorted(self.filter_columns.items()):
            key_parts.append(f"f:{column}:{value}")

        # データのハッシュ値（データが変更されたかどうかを判断するため）
        if self.processed_data is not None:
            # データフレームのサイズと列名のハッシュを使用
            data_hash = hash((len(self.processed_data), tuple(self.processed_data.columns)))
            key_parts.append(f"data:{data_hash}")

        return ":".join(key_parts)

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

        # 軸が変更された場合はキャッシュを無効化
        if self.x_column != x_column or self.y_column != y_column or self.value_column != value_column:
            self._invalidate_cache()

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

        # フィルター条件が変更された場合はキャッシュを無効化
        if column not in self.filter_columns or self.filter_columns[column] != value:
            self._invalidate_cache()

        self.filter_columns[column] = value

    def clear_filter(self, column: Optional[str] = None) -> None:
        """
        フィルタリング条件をクリアします。

        Args:
            column (Optional[str]): クリアする列名（Noneの場合はすべてクリア）
        """
        # フィルターが存在する場合のみキャッシュを無効化
        if column is None:
            if self.filter_columns:
                self._invalidate_cache()
            self.filter_columns.clear()
        elif column in self.filter_columns:
            self._invalidate_cache()
            del self.filter_columns[column]

    def process_data(self) -> pd.DataFrame:
        """
        設定された条件に基づいてデータを処理します。
        ベクトル化処理を使用して高速化しています。

        Returns:
            pd.DataFrame: 処理後のデータフレーム
        """
        if self.data is None:
            raise ValueError("データが設定されていません。")

        if self.x_column is None or self.y_column is None or self.value_column is None:
            raise ValueError("軸と値の列が設定されていません。")

        # フィルタリング条件の適用（ベクトル化処理）
        if not self.filter_columns:
            # フィルタリング条件がない場合は元のデータをそのまま使用
            self.processed_data = self.data
        else:
            # すべてのフィルタリング条件を一度に適用するマスクを作成
            mask = np.ones(len(self.data), dtype=bool)
            for column, value in self.filter_columns.items():
                # 近似値でフィルタリング（完全一致だと浮動小数点の誤差で問題が発生する可能性がある）
                mask &= np.isclose(self.data[column].values, value)

            # マスクを適用してフィルタリング
            self.processed_data = self.data[mask]

        # データが変更されたのでキャッシュを無効化
        self._invalidate_cache()

        return self.processed_data

    def get_heatmap_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        ヒートマップ表示用のデータを取得します。
        NumPyのベクトル化処理とキャッシュを使用して高速化しています。

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: (X軸の値, Y軸の値, Z軸の値)
        """
        if self.processed_data is None or len(self.processed_data) == 0:
            raise ValueError("処理済みデータが存在しません。")

        if self.x_column is None or self.y_column is None or self.value_column is None:
            raise ValueError("軸と値の列が設定されていません。")

        # キャッシュキーの生成
        cache_key = self._get_cache_key("heatmap")

        # キャッシュにデータがある場合はそれを返す
        if cache_key in self._cache:
            return self._cache[cache_key]

        # ユニークなX軸、Y軸の値を取得（ソート済み）
        x_values = np.array(sorted(self.processed_data[self.x_column].unique()))
        y_values = np.array(sorted(self.processed_data[self.y_column].unique()))

        # メッシュグリッドの作成
        X, Y = np.meshgrid(x_values, y_values)

        # Z値の初期化（NaNで埋める）
        Z = np.full(X.shape, np.nan)

        # データポイントをマッピング（ベクトル化処理）
        # 1. 各データポイントのx, y, z値を抽出
        x_data = self.processed_data[self.x_column].values
        y_data = self.processed_data[self.y_column].values
        z_data = self.processed_data[self.value_column].values

        # 2. x値とy値のインデックスを高速に検索するための辞書を作成
        x_indices = {val: i for i, val in enumerate(x_values)}
        y_indices = {val: i for i, val in enumerate(y_values)}

        # 3. 各データポイントのインデックスを取得
        x_idx = np.array([x_indices.get(x, -1) for x in x_data])
        y_idx = np.array([y_indices.get(y, -1) for y in y_data])

        # 4. 有効なインデックスのみを使用してZ値を設定
        valid_indices = (x_idx >= 0) & (y_idx >= 0)
        Z[y_idx[valid_indices], x_idx[valid_indices]] = z_data[valid_indices]

        # 結果をキャッシュに保存
        result = (X, Y, Z)
        self._cache[cache_key] = result

        return result

    def get_value_range(self) -> Tuple[float, float]:
        """
        値（カラーマップの色）の範囲を取得します。
        キャッシュを使用して高速化しています。

        Returns:
            Tuple[float, float]: (最小値, 最大値)
        """
        if self.processed_data is None or len(self.processed_data) == 0:
            raise ValueError("処理済みデータが存在しません。")

        if self.value_column is None:
            raise ValueError("値の列が設定されていません。")

        # キャッシュキーの生成
        cache_key = self._get_cache_key("value_range")

        # キャッシュにデータがある場合はそれを返す
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 値の範囲を計算
        min_val = self.processed_data[self.value_column].min()
        max_val = self.processed_data[self.value_column].max()

        # 結果をキャッシュに保存
        result = (min_val, max_val)
        self._cache[cache_key] = result

        return result

    def get_axis_range(self, axis: str) -> Tuple[float, float]:
        """
        指定された軸の値の範囲を取得します。
        キャッシュを使用して高速化しています。

        Args:
            axis (str): 軸の種類（'x' または 'y'）

        Returns:
            Tuple[float, float]: (最小値, 最大値)
        """
        if self.processed_data is None or len(self.processed_data) == 0:
            raise ValueError("処理済みデータが存在しません。")

        # 軸の種類に応じた列名を取得
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

        # キャッシュキーの生成
        cache_key = self._get_cache_key(f"{axis}_range")

        # キャッシュにデータがある場合はそれを返す
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 軸の範囲を計算
        min_val = self.processed_data[column].min()
        max_val = self.processed_data[column].max()

        # 結果をキャッシュに保存
        result = (min_val, max_val)
        self._cache[cache_key] = result

        return result
