"""
データコントローラーモジュール

データ操作の制御を担当します。
"""


class DataController:
    """
    データコントローラークラス

    データ操作の制御を担当します。
    """

    def __init__(self, app_controller):
        """
        データコントローラーの初期化

        Args:
            app_controller: アプリケーションコントローラーの参照
        """
        self.app_controller = app_controller

    def load_file(self, file_path):
        """
        ファイルの読み込み

        Args:
            file_path (str): ファイルパス
        """
        try:
            # データローダーにファイルを設定
            self.app_controller.data_loader.set_file(file_path)

            # 列情報の取得
            columns = self.app_controller.data_loader.get_columns()

            # コントロールパネルの更新
            self.app_controller.main_window.control_panel.update_columns(columns)

            # 初期データの読み込み
            self._load_initial_data()

            # ステータスバーの更新
            self.app_controller.update_status(f"ファイル '{file_path}' を読み込みました。")

        except Exception as e:
            self.app_controller.show_error("ファイル読み込みエラー", str(e))

    def _load_initial_data(self):
        """初期データの読み込み"""
        try:
            # 最初のチャンクを読み込み
            chunk, _ = self.app_controller.data_loader.get_chunk(0)

            # データプロセッサーにデータを設定
            self.app_controller.data_processor.set_data(chunk)

            # データフィルターにデータを設定
            self.app_controller.data_filter.set_data(chunk)

            # 軸の設定
            x_column = self.app_controller.main_window.control_panel.x_column.get()
            y_column = self.app_controller.main_window.control_panel.y_column.get()
            value_column = self.app_controller.main_window.control_panel.value_column.get()

            if x_column and y_column and value_column:
                self.set_axes(x_column, y_column, value_column)

        except Exception as e:
            self.app_controller.show_error("データ読み込みエラー", str(e))

    def set_axes(self, x_column, y_column, value_column):
        """
        表示軸の設定

        Args:
            x_column (str): X軸の列名
            y_column (str): Y軸の列名
            value_column (str): 値の列名
        """
        try:
            # データプロセッサーに軸を設定
            self.app_controller.data_processor.set_axes(x_column, y_column, value_column)

            # データの処理
            self.app_controller.data_processor.process_data()

            # プロットの更新
            self._update_plot()

        except Exception as e:
            self.app_controller.show_error("軸設定エラー", str(e))

    def set_filter(self, column, value):
        """
        フィルターの設定

        Args:
            column (str): フィルター対象の列名
            value (float): フィルター値
        """
        try:
            # データプロセッサーにフィルターを設定
            self.app_controller.data_processor.set_filter(column, value)

            # データの処理
            self.app_controller.data_processor.process_data()

            # プロットの更新
            self._update_plot()

        except Exception as e:
            self.app_controller.show_error("フィルター設定エラー", str(e))

    def update_filter_values(self, column):
        """
        フィルター値の更新

        Args:
            column (str): フィルター対象の列名
        """
        try:
            if not column:
                return

            # 列のユニークな値を取得
            values = self.app_controller.data_filter.get_unique_values(column)

            # コントロールパネルの更新
            self.app_controller.main_window.control_panel.update_filter_values(values)

        except Exception as e:
            self.app_controller.show_error("フィルター値更新エラー", str(e))

    def _update_plot(self):
        """プロットの更新"""
        try:
            # ヒートマップデータの取得
            x_data, y_data, z_data = self.app_controller.data_processor.get_heatmap_data()

            # 軸ラベルの取得
            x_label = self.app_controller.main_window.control_panel.x_column.get()
            y_label = self.app_controller.main_window.control_panel.y_column.get()

            # プロットの更新
            self.app_controller.main_window.plot_panel.plot_heatmap(
                x_data, y_data, z_data,
                x_label, y_label
            )

            # 範囲の取得
            x_range = self.app_controller.data_processor.get_axis_range('x')
            y_range = self.app_controller.data_processor.get_axis_range('y')
            value_range = self.app_controller.data_processor.get_value_range()

            # コントロールパネルの更新
            self.app_controller.main_window.control_panel.update_ranges(
                x_range, y_range, value_range
            )

        except Exception as e:
            self.app_controller.show_error("プロット更新エラー", str(e))

    def export_data(self, file_path, selected_only=False):
        """
        データのエクスポート

        Args:
            file_path (str): 出力ファイルパス
            selected_only (bool): 選択領域のみエクスポートする場合はTrue
        """
        try:
            # データの取得
            if selected_only and self.app_controller.plot_controller.x_range and self.app_controller.plot_controller.y_range:
                # 選択領域のデータを取得
                x_min, x_max = self.app_controller.plot_controller.x_range
                y_min, y_max = self.app_controller.plot_controller.y_range

                # フィルタリング条件の設定
                x_column = self.app_controller.main_window.control_panel.x_column.get()
                y_column = self.app_controller.main_window.control_panel.y_column.get()

                # データフィルターに範囲フィルターを設定
                self.app_controller.data_filter.add_range_filter(x_column, x_min, x_max)
                self.app_controller.data_filter.add_range_filter(y_column, y_min, y_max)

                # フィルタリングの適用
                filtered_data = self.app_controller.data_filter.apply_filters()

                # CSVとして保存
                filtered_data.to_csv(file_path, index=False)

                # フィルターのクリア
                self.app_controller.data_filter.clear_filters()

            else:
                # 全データを保存
                self.app_controller.data_processor.processed_data.to_csv(file_path, index=False)

            # ステータスバーの更新
            self.app_controller.update_status(f"データを '{file_path}' にエクスポートしました。")

        except Exception as e:
            self.app_controller.show_error("データエクスポートエラー", str(e))

    def export_image(self, file_path):
        """
        画像のエクスポート

        Args:
            file_path (str): 出力ファイルパス
        """
        try:
            # プロットを画像として保存
            self.app_controller.main_window.plot_panel.figure.savefig(
                file_path, dpi=300, bbox_inches='tight'
            )

            # ステータスバーの更新
            self.app_controller.update_status(f"画像を '{file_path}' にエクスポートしました。")

        except Exception as e:
            self.app_controller.show_error("画像エクスポートエラー", str(e))
