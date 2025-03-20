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
            # すべてのデータを読み込み
            df = self.app_controller.data_loader.load_all_data()

            # データプロセッサーにデータを設定
            self.app_controller.data_processor.set_data(df)

            # データフィルターにデータを設定
            self.app_controller.data_filter.set_data(df)

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

            # 数値列かどうかを判定
            is_numeric = False
            if values:
                try:
                    # 最初の値が数値に変換できるかチェック
                    float(values[0])
                    is_numeric = True
                except (ValueError, TypeError):
                    is_numeric = False

            # コントロールパネルの更新
            self.app_controller.main_window.control_panel.update_filter_values(values, is_numeric)

        except Exception as e:
            self.app_controller.show_error("フィルター値更新エラー", str(e))

    def add_value_filter(self, column, value):
        """
        値フィルターの追加

        Args:
            column (str): フィルター対象の列名
            value: フィルター値
        """
        try:
            # データフィルターに値フィルターを追加
            self.app_controller.data_filter.add_value_filter(column, value)

            # フィルタリングの適用
            self.app_controller.data_filter.apply_filters()

            # データプロセッサーにフィルタリング結果を設定
            filtered_data = self.app_controller.data_filter.get_filtered_data()
            self.app_controller.data_processor.set_data(filtered_data)

            # データの処理
            self.app_controller.data_processor.process_data()

            # プロットの更新
            self._update_plot()

            # ステータスバーの更新
            filter_summary = self.app_controller.data_filter.get_filter_summary()
            total_rows = filter_summary["total_rows"]
            filtered_rows = filter_summary["filtered_rows"]
            self.app_controller.update_status(f"フィルタリング: {filtered_rows}/{total_rows} 行 ({filtered_rows / total_rows * 100:.1f}%)")

        except Exception as e:
            self.app_controller.show_error("フィルター設定エラー", str(e))

    def add_range_filter(self, column, min_val, max_val):
        """
        範囲フィルターの追加

        Args:
            column (str): フィルター対象の列名
            min_val (float): 最小値
            max_val (float): 最大値
        """
        try:
            # データフィルターに範囲フィルターを追加
            self.app_controller.data_filter.add_range_filter(column, min_val, max_val)

            # フィルタリングの適用
            self.app_controller.data_filter.apply_filters()

            # データプロセッサーにフィルタリング結果を設定
            filtered_data = self.app_controller.data_filter.get_filtered_data()
            self.app_controller.data_processor.set_data(filtered_data)

            # データの処理
            self.app_controller.data_processor.process_data()

            # プロットの更新
            self._update_plot()

            # ステータスバーの更新
            filter_summary = self.app_controller.data_filter.get_filter_summary()
            total_rows = filter_summary["total_rows"]
            filtered_rows = filter_summary["filtered_rows"]
            self.app_controller.update_status(f"フィルタリング: {filtered_rows}/{total_rows} 行 ({filtered_rows / total_rows * 100:.1f}%)")

        except Exception as e:
            self.app_controller.show_error("フィルター設定エラー", str(e))

    def clear_filters(self, column=None):
        """
        フィルターのクリア

        Args:
            column (str, optional): クリアする列名。Noneの場合はすべてクリア。
        """
        try:
            # データフィルターのクリア
            self.app_controller.data_filter.clear_filters(column)

            # フィルタリングの適用
            self.app_controller.data_filter.apply_filters()

            # データプロセッサーにフィルタリング結果を設定
            filtered_data = self.app_controller.data_filter.get_filtered_data()
            self.app_controller.data_processor.set_data(filtered_data)

            # データの処理
            self.app_controller.data_processor.process_data()

            # プロットの更新
            self._update_plot()

            # ステータスバーの更新
            if column:
                self.app_controller.update_status(f"フィルター '{column}' をクリアしました。")
            else:
                self.app_controller.update_status("すべてのフィルターをクリアしました。")

        except Exception as e:
            self.app_controller.show_error("フィルタークリアエラー", str(e))

    def get_filter_summary(self):
        """
        フィルター概要の取得

        Returns:
            dict: フィルター概要
        """
        try:
            return self.app_controller.data_filter.get_filter_summary()
        except Exception as e:
            self.app_controller.show_error("フィルター情報取得エラー", str(e))
            return {"value_filters": {}, "range_filters": {}, "filtered_rows": 0, "total_rows": 0}

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

    def set_colormap(self, colormap):
        """
        カラーマップの設定

        Args:
            colormap (str): カラーマップ名
        """
        try:
            # プロットパネルにカラーマップを設定
            self.app_controller.main_window.plot_panel.set_colormap(colormap)

        except Exception as e:
            self.app_controller.show_error("カラーマップ設定エラー", str(e))

    def set_scale(self, log_scale):
        """
        スケールの設定

        Args:
            log_scale (bool): 対数スケールの場合はTrue
        """
        try:
            # プロットパネルにスケールを設定
            self.app_controller.main_window.plot_panel.set_scale(log_scale)

        except Exception as e:
            self.app_controller.show_error("スケール設定エラー", str(e))

    def set_ranges(self, x_range, y_range, value_range):
        """
        表示範囲の設定

        Args:
            x_range (tuple): X軸の範囲 (min, max)
            y_range (tuple): Y軸の範囲 (min, max)
            value_range (tuple): 値の範囲 (min, max)
        """
        try:
            # プロットパネルに範囲を設定
            self.app_controller.main_window.plot_panel.set_ranges(
                x_range, y_range, value_range
            )

        except Exception as e:
            self.app_controller.show_error("範囲設定エラー", str(e))

    def reset_view(self):
        """表示のリセット"""
        try:
            # データプロセッサーから範囲を取得
            x_range = self.app_controller.data_processor.get_axis_range('x')
            y_range = self.app_controller.data_processor.get_axis_range('y')
            value_range = self.app_controller.data_processor.get_value_range()

            # プロットパネルに範囲を設定
            self.app_controller.main_window.plot_panel.set_ranges(
                x_range, y_range, value_range
            )

            # コントロールパネルの更新
            self.app_controller.main_window.control_panel.update_ranges(
                x_range, y_range, value_range
            )

        except Exception as e:
            self.app_controller.show_error("表示リセットエラー", str(e))

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
