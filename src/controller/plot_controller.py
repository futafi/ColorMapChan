"""
プロットコントローラーモジュール

プロット操作の制御を担当します。
"""


class PlotController:
    """
    プロットコントローラークラス

    プロット操作の制御を担当します。
    """

    def __init__(self, app_controller):
        """
        プロットコントローラーの初期化

        Args:
            app_controller: アプリケーションコントローラーの参照
        """
        self.app_controller = app_controller

        # プロットの状態
        self.x_range = None
        self.y_range = None
        self.value_range = None
        self.profile_window = None  # 断面プロットウィンドウの参照

    def set_ranges(self, x_range, y_range, value_range):
        """
        表示範囲の設定

        Args:
            x_range (tuple): X軸の範囲 (min, max)
            y_range (tuple): Y軸の範囲 (min, max)
            value_range (tuple): 値の範囲 (min, max)
        """
        self.x_range = x_range
        self.y_range = y_range
        self.value_range = value_range

        # プロットの更新
        self._update_plot()

    def reset_ranges(self):
        """表示範囲のリセット"""
        self.x_range = None
        self.y_range = None
        self.value_range = None

        # プロットの更新
        self._update_plot()

    def _update_plot(self):
        """プロットの更新"""
        # データプロセッサーからデータを取得
        try:
            x_data, y_data, z_data = self.app_controller.data_processor.get_heatmap_data()

            # 軸ラベルの取得
            x_label = self.app_controller.main_window.control_panel.x_column.get()
            y_label = self.app_controller.main_window.control_panel.y_column.get()

            # プロットの更新
            self.app_controller.main_window.plot_panel.plot_heatmap(
                x_data, y_data, z_data,
                x_label, y_label,
                vmin=self.value_range[0] if self.value_range else None,
                vmax=self.value_range[1] if self.value_range else None
            )

            # 範囲の設定
            if self.x_range and self.y_range:
                self.app_controller.main_window.plot_panel.ax.set_xlim(self.x_range)
                self.app_controller.main_window.plot_panel.ax.set_ylim(self.y_range)
                self.app_controller.main_window.plot_panel.canvas.draw()

        except Exception as e:
            self.app_controller.show_error("プロット更新エラー", str(e))

    def zoom_to_selection(self, x_min, x_max, y_min, y_max):
        """
        選択領域へのズーム

        Args:
            x_min (float): X軸の最小値
            x_max (float): X軸の最大値
            y_min (float): Y軸の最小値
            y_max (float): Y軸の最大値
        """
        self.x_range = (x_min, x_max)
        self.y_range = (y_min, y_max)

        # プロットの更新
        self._update_plot()

        # ステータスバーの更新
        self.app_controller.update_status(
            f"選択領域にズーム: X={x_min:.6g}～{x_max:.6g}, Y={y_min:.6g}～{y_max:.6g}"
        )

    def pan(self, dx, dy):
        """
        プロットのパン（移動）

        Args:
            dx (float): X軸方向の移動量
            dy (float): Y軸方向の移動量
        """
        if not self.x_range or not self.y_range:
            return

        x_min, x_max = self.x_range
        y_min, y_max = self.y_range

        # 範囲の更新
        self.x_range = (x_min + dx, x_max + dx)
        self.y_range = (y_min + dy, y_max + dy)

        # プロットの更新
        self._update_plot()

    def set_profile_mode(self, enabled):
        """
        断面表示モードの設定

        Args:
            enabled (bool): 断面表示モードを有効にする場合はTrue
        """
        self.app_controller.main_window.plot_panel.set_profile_mode(enabled)

    def show_profiles(self, click_point):
        """
        クリックした点での断面プロットを表示します。

        Args:
            click_point (tuple): クリックした点の座標 (x, y)
        """
        try:
            # X軸断面データの取得
            x_data, x_values = self.app_controller.data_processor.get_x_profile(click_point[1])

            # Y軸断面データの取得
            y_data, y_values = self.app_controller.data_processor.get_y_profile(click_point[0])

            # 軸ラベルの取得
            x_label = self.app_controller.main_window.control_panel.x_column.get()
            y_label = self.app_controller.main_window.control_panel.y_column.get()
            value_label = self.app_controller.main_window.control_panel.value_column.get()

            # 断面プロットウィンドウの表示
            if not self.profile_window or not self.profile_window.window.winfo_exists():
                self.profile_window = ProfileWindow(self.app_controller.main_window.root, self)

            # 断面プロットの描画
            self.profile_window.plot_profiles(
                x_data, x_values, y_data, y_values, click_point,
                x_label, y_label, value_label
            )

            # ステータスバーの更新
            self.app_controller.update_status(
                f"断面プロット表示: 座標 ({click_point[0]:.6g}, {click_point[1]:.6g})"
            )

        except Exception as e:
            self.app_controller.show_error("断面プロットエラー", str(e))

    def set_colormap(self, colormap):
        """
        カラーマップの設定

        Args:
            colormap (str): カラーマップ名
        """
        # プロットパネルにカラーマップを設定
        self.app_controller.main_window.plot_panel.set_colormap(colormap)

    def set_scale(self, log_scale):
        """
        スケールの設定

        Args:
            log_scale (bool): 対数スケールの場合はTrue、線形スケールの場合はFalse
        """
        # プロットパネルにスケールを設定
        self.app_controller.main_window.plot_panel.set_scale(log_scale)
