"""
アプリケーションコントローラーモジュール

アプリケーション全体の制御を担当します。
"""

from .data_controller import DataController
from .plot_controller import PlotController
from ..model.data_loader import DataLoader
from ..model.data_processor import DataProcessor
from ..model.data_filter import DataFilter


class AppController:
    """
    アプリケーションコントローラークラス

    アプリケーション全体の制御を担当します。
    """

    def __init__(self):
        """アプリケーションコントローラーの初期化"""
        # モデルの初期化
        self.data_loader = DataLoader()
        self.data_processor = DataProcessor()
        self.data_filter = DataFilter()

        # コントローラーの初期化
        self.data_controller = DataController(self)
        self.plot_controller = PlotController(self)

        # ビューの参照
        self.main_window = None

    def set_main_window(self, main_window):
        """
        メインウィンドウの設定

        Args:
            main_window: メインウィンドウの参照
        """
        self.main_window = main_window

    def run(self):
        """アプリケーションの実行"""
        if self.main_window:
            self.main_window.run()
        else:
            raise RuntimeError("メインウィンドウが設定されていません。")

    def load_file(self, file_path):
        """
        ファイルの読み込み

        Args:
            file_path (str): ファイルパス
        """
        # データローダーにファイルを設定
        self.data_loader.set_file(file_path)

        # 列情報の取得
        columns = self.data_loader.get_columns()

        # コントロールパネルの更新
        self.main_window.control_panel.update_columns(columns)

        # 初期データの読み込み
        self._load_initial_data()

        # ステータスバーの更新
        self.update_status(f"ファイル '{file_path}' を読み込みました。")

    def _load_initial_data(self):
        """初期データの読み込み"""
        # 最初のチャンクを読み込み
        chunk, _ = self.data_loader.get_chunk(0)

        # データプロセッサーにデータを設定
        self.data_processor.set_data(chunk)

        # データフィルターにデータを設定
        self.data_filter.set_data(chunk)

        # 軸の設定
        x_column = self.main_window.control_panel.x_column.get()
        y_column = self.main_window.control_panel.y_column.get()
        value_column = self.main_window.control_panel.value_column.get()

        if x_column and y_column and value_column:
            self.set_axes(x_column, y_column, value_column)

    def set_axes(self, x_column, y_column, value_column):
        """
        表示軸の設定

        Args:
            x_column (str): X軸の列名
            y_column (str): Y軸の列名
            value_column (str): 値の列名
        """
        # データプロセッサーに軸を設定
        self.data_processor.set_axes(x_column, y_column, value_column)

        # データの処理
        self.data_processor.process_data()

        # プロットの更新
        self._update_plot()

    def set_filter(self, column, value):
        """
        フィルターの設定

        Args:
            column (str): フィルター対象の列名
            value (float): フィルター値
        """
        # データプロセッサーにフィルターを設定
        self.data_processor.set_filter(column, value)

        # データの処理
        self.data_processor.process_data()

        # プロットの更新
        self._update_plot()

    def update_filter_values(self, column):
        """
        フィルター値の更新

        Args:
            column (str): フィルター対象の列名
        """
        if not column:
            return

        # 列のユニークな値を取得
        values = self.data_filter.get_unique_values(column)

        # コントロールパネルの更新
        self.main_window.control_panel.update_filter_values(values)

    def set_colormap(self, colormap):
        """
        カラーマップの設定

        Args:
            colormap (str): カラーマップ名
        """
        # プロットパネルにカラーマップを設定
        self.main_window.plot_panel.set_colormap(colormap)

    def set_scale(self, log_scale):
        """
        スケールの設定

        Args:
            log_scale (bool): 対数スケールの場合はTrue、線形スケールの場合はFalse
        """
        # プロットパネルにスケールを設定
        self.main_window.plot_panel.set_scale(log_scale)

    def set_ranges(self, x_range, y_range, value_range):
        """
        表示範囲の設定

        Args:
            x_range (tuple): X軸の範囲 (min, max)
            y_range (tuple): Y軸の範囲 (min, max)
            value_range (tuple): 値の範囲 (min, max)
        """
        # プロットコントローラーに範囲を設定
        self.plot_controller.set_ranges(x_range, y_range, value_range)

    def reset_view(self):
        """表示のリセット"""
        # データの再処理
        self.data_processor.process_data()

        # プロットの更新
        self._update_plot()

        # ステータスバーの更新
        self.update_status("表示をリセットしました。")

    def _update_plot(self):
        """プロットの更新"""
        # ヒートマップデータの取得
        try:
            x_data, y_data, z_data = self.data_processor.get_heatmap_data()

            # 軸ラベルの取得
            x_label = self.main_window.control_panel.x_column.get()
            y_label = self.main_window.control_panel.y_column.get()

            # プロットの更新
            self.main_window.plot_panel.plot_heatmap(
                x_data, y_data, z_data,
                x_label, y_label
            )

            # 範囲の取得
            x_range = self.data_processor.get_axis_range('x')
            y_range = self.data_processor.get_axis_range('y')
            value_range = self.data_processor.get_value_range()

            # コントロールパネルの更新
            self.main_window.control_panel.update_ranges(
                x_range, y_range, value_range
            )

        except Exception as e:
            self.show_error("プロット更新エラー", str(e))

    def update_status(self, message):
        """
        ステータスバーの更新

        Args:
            message (str): 表示するメッセージ
        """
        if self.main_window:
            self.main_window.update_status(message)

    def show_error(self, title, message):
        """
        エラーメッセージの表示

        Args:
            title (str): エラーのタイトル
            message (str): エラーメッセージ
        """
        if self.main_window:
            self.main_window.show_error(title, message)

    def show_info(self, title, message):
        """
        情報メッセージの表示

        Args:
            title (str): 情報のタイトル
            message (str): 情報メッセージ
        """
        if self.main_window:
            self.main_window.show_info(title, message)
