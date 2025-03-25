"""
プロットコントローラーモジュール

プロット操作の制御を担当します。
"""

from src.view.profile_window import ProfileWindow


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
        self.plot_mode = "2d"      # 表示モード（'2d'または'3d'）

    def set_plot_mode(self, mode):
        """
        表示モードの設定

        Args:
            mode (str): 表示モード（'2d'または'3d'）
        """
        # メインウィンドウの表示モードを切り替え
        self.app_controller.main_window.set_plot_mode(mode)
        
        # 現在のモードを記録
        self.plot_mode = mode
        
        # プロットの更新
        self._update_plot()

    def set_3d_axes(self, x_column, y_column, z_column, color_column=None):
        """
        3D表示用の軸とカラー値の設定

        Args:
            x_column (str): X軸に表示する列名
            y_column (str): Y軸に表示する列名
            z_column (str): Z軸（高さ）に表示する列名
            color_column (str, optional): カラー値として表示する列名
        """
        try:
            # データプロセッサーに3D軸を設定
            self.app_controller.data_processor.set_3d_axes(
                x_column, y_column, z_column, color_column
            )
            
            # プロットの更新
            self._update_plot()
        except Exception as e:
            self.app_controller.show_error("軸設定エラー", str(e))

    def set_wireframe(self, wireframe):
        """
        ワイヤーフレーム表示の設定

        Args:
            wireframe (bool): ワイヤーフレーム表示の場合はTrue
        """
        # 3Dプロットパネルにワイヤーフレーム設定を適用
        self.app_controller.main_window.plot_3d_panel.set_wireframe(wireframe)

    def set_view_angle(self, elevation, azimuth):
        """
        視点角度の設定

        Args:
            elevation (float): 仰角（度）
            azimuth (float): 方位角（度）
        """
        # 3Dプロットパネルに視点角度を設定
        self.app_controller.main_window.plot_3d_panel.set_view_angle(elevation, azimuth)

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
        # 現在の表示モードに応じてプロットを更新
        if self.plot_mode == "3d":
            self._update_3d_plot()
        else:
            self._update_2d_plot()

    def _update_2d_plot(self):
        """2Dプロットの更新"""
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
            self.app_controller.show_error("2Dプロット更新エラー", str(e))

    def _update_3d_plot(self):
        """3Dプロットの更新"""
        # データプロセッサーからデータを取得
        try:
            x_data, y_data, z_data, c_data = self.app_controller.data_processor.get_3d_plot_data()

            # 軸ラベルの取得
            x_label = self.app_controller.main_window.control_panel.x_column.get()
            y_label = self.app_controller.main_window.control_panel.y_column.get()
            z_label = self.app_controller.main_window.control_panel.z_column.get()
            c_label = self.app_controller.main_window.control_panel.color_column.get()

            # プロットの更新
            self.app_controller.main_window.plot_3d_panel.plot_3d_surface(
                x_data, y_data, z_data, c_data,
                x_label, y_label, z_label, c_label
            )

        except Exception as e:
            self.app_controller.show_error("3Dプロット更新エラー", str(e))

    def update_plot_ranges(self, x_range, y_range):
        """
        プロット範囲の更新（matplotlibのズーム・パン操作後に呼ばれる）

        Args:
            x_range (tuple): X軸の範囲 (min, max)
            y_range (tuple): Y軸の範囲 (min, max)
        """
        self.x_range = x_range
        self.y_range = y_range

        # コントロールパネルの表示を更新
        if hasattr(self.app_controller.main_window, 'control_panel'):
            self.app_controller.main_window.control_panel.update_ranges(
                x_range, y_range, self.value_range
            )

        # ステータスバーの更新
        self.app_controller.update_status(
            f"表示範囲: X={x_range[0]:.6g}～{x_range[1]:.6g}, Y={y_range[0]:.6g}～{y_range[1]:.6g}"
        )

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
