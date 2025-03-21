"""
プロットパネルモジュール

matplotlibを使用したプロット表示を提供します。
"""

from matplotlib.colors import LogNorm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use('TkAgg')


class PlotPanel:
    """
    プロットパネルクラス

    matplotlibを使用したプロット表示を提供します。
    """

    def __init__(self, parent, controller):
        """
        プロットパネルの初期化

        Args:
            parent: 親ウィジェット
            controller: アプリケーションコントローラー
        """
        self.parent = parent
        self.controller = controller

        # プロットの状態
        self.data = None
        self.x_data = None
        self.y_data = None
        self.z_data = None
        self.colormap = 'plasma'  # デフォルトのカラーマップ
        self.log_scale = False    # デフォルトは線形スケール
        self.colorbar = None      # カラーバーの参照
        self.profile_mode = False # 断面表示モード

        self._create_widgets()

    def _create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Figureの作成
        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)

        # キャンバスの作成
        self.canvas = FigureCanvasTkAgg(self.figure, self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # ツールバーの作成
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # マウスイベントの設定
        self.canvas.mpl_connect('button_press_event', self._on_click)
        self.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.canvas.mpl_connect('button_release_event', self._on_release)

        # 選択領域の初期化
        self.selection_rect = None
        self.start_point = None

    def plot_heatmap(self, x_data, y_data, z_data, x_label, y_label, title=None, vmin=None, vmax=None):
        """
        ヒートマップの描画

        Args:
            x_data (numpy.ndarray): X軸のデータ
            y_data (numpy.ndarray): Y軸のデータ
            z_data (numpy.ndarray): Z軸のデータ（カラーマップの値）
            x_label (str): X軸のラベル
            y_label (str): Y軸のラベル
            title (str, optional): プロットのタイトル
            vmin (float, optional): カラーマップの最小値
            vmax (float, optional): カラーマップの最大値
        """
        self.x_data = x_data
        self.y_data = y_data
        self.z_data = z_data

        # Figureを完全にクリア
        self.figure.clear()

        # 新しいAxesを作成
        self.ax = self.figure.add_subplot(111)

        # カラーマップの設定
        if self.log_scale:
            # 対数スケールの場合、0以下の値を扱えないため、最小値を調整
            if vmin is not None and vmin <= 0:
                vmin = z_data[z_data > 0].min() if z_data.size > 0 else 1e-10
            if vmax is not None and vmax <= 0:
                vmax = z_data.max()
            norm = LogNorm(vmin=vmin, vmax=vmax)
        else:
            norm = None

        # ヒートマップの描画
        im = self.ax.pcolormesh(
            x_data, y_data, z_data,
            cmap=self.colormap,
            norm=norm,
            vmin=vmin if not self.log_scale else None,
            vmax=vmax if not self.log_scale else None,
            shading='auto'
        )

        # カラーバーの追加と参照の保持
        self.colorbar = self.figure.colorbar(im, ax=self.ax, label='電流値')

        # 軸ラベルの設定
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)

        # タイトルの設定（指定があれば）
        if title:
            self.ax.set_title(title)

        # グリッドの表示
        self.ax.grid(True, linestyle='--', alpha=0.7)

        # マウスイベントの再設定
        self.canvas.mpl_connect('button_press_event', self._on_click)
        self.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.canvas.mpl_connect('button_release_event', self._on_release)

        # キャンバスの更新
        self.canvas.draw()

    def set_profile_mode(self, enabled):
        """
        断面表示モードの設定

        Args:
            enabled (bool): 断面表示モードを有効にする場合はTrue
        """
        self.profile_mode = enabled

        # カーソルの変更
        if enabled:
            self.canvas.get_tk_widget().config(cursor="crosshair")
        else:
            self.canvas.get_tk_widget().config(cursor="")

    def set_colormap(self, colormap):
        """
        カラーマップの設定

        Args:
            colormap (str): カラーマップ名
        """
        self.colormap = colormap
        if self.z_data is not None:
            # 現在の値範囲を取得
            vmin = vmax = None
            if self.colorbar is not None:
                vmin = self.colorbar.norm.vmin if hasattr(self.colorbar.norm, 'vmin') else None
                vmax = self.colorbar.norm.vmax if hasattr(self.colorbar.norm, 'vmax') else None

            self.plot_heatmap(
                self.x_data, self.y_data, self.z_data,
                self.ax.get_xlabel(), self.ax.get_ylabel(),
                self.ax.get_title(),
                vmin=vmin,
                vmax=vmax
            )

    def set_scale(self, log_scale):
        """
        スケールの設定

        Args:
            log_scale (bool): 対数スケールの場合はTrue、線形スケールの場合はFalse
        """
        self.log_scale = log_scale
        if self.z_data is not None:
            # 現在の値範囲を取得
            vmin = vmax = None
            if self.colorbar is not None:
                vmin = self.colorbar.norm.vmin if hasattr(self.colorbar.norm, 'vmin') else None
                vmax = self.colorbar.norm.vmax if hasattr(self.colorbar.norm, 'vmax') else None

            self.plot_heatmap(
                self.x_data, self.y_data, self.z_data,
                self.ax.get_xlabel(), self.ax.get_ylabel(),
                self.ax.get_title(),
                vmin=vmin,
                vmax=vmax
            )

    def _on_click(self, event):
        """
        マウスクリック時の処理

        Args:
            event: マウスイベント
        """
        if event.inaxes != self.ax:
            return

        # 断面表示モードの場合
        if self.profile_mode:
            if event.button == 1:  # 左クリックの場合
                click_point = (event.xdata, event.ydata)
                self.controller.show_profiles(click_point)
            return

        # 通常モードの場合
        if event.button == 1:  # 左クリックの場合は選択開始
            self.start_point = (event.xdata, event.ydata)

            # 既存の選択領域があれば削除
            if self.selection_rect:
                self.selection_rect.remove()
                self.selection_rect = None

            # 新しい選択領域の作成
            self.selection_rect = matplotlib.patches.Rectangle(
                (event.xdata, event.ydata),
                0, 0,
                linewidth=1,
                edgecolor='r',
                facecolor='none',
                linestyle='--'
            )
            self.ax.add_patch(self.selection_rect)
            self.canvas.draw()

        # 右クリックの場合はリセット
        elif event.button == 3:
            self.controller.reset_view()

    def _on_motion(self, event):
        """
        マウス移動時の処理

        Args:
            event: マウスイベント
        """
        if event.inaxes != self.ax:
            return

        # カーソル位置の値を表示
        if self.z_data is not None:
            # 最も近いデータポイントを探す
            x_idx = np.abs(self.x_data[0, :] - event.xdata).argmin()
            y_idx = np.abs(self.y_data[:, 0] - event.ydata).argmin()

            if 0 <= x_idx < self.z_data.shape[1] and 0 <= y_idx < self.z_data.shape[0]:
                value = self.z_data[y_idx, x_idx]
                status_text = f"X: {event.xdata:.6g}, Y: {event.ydata:.6g}, 値: {value:.6g}"
                self.controller.update_status(status_text)

        # 選択領域の更新
        if self.start_point and self.selection_rect:
            x0, y0 = self.start_point
            width = event.xdata - x0
            height = event.ydata - y0

            self.selection_rect.set_width(width)
            self.selection_rect.set_height(height)
            self.canvas.draw()

    def _on_release(self, event):
        """
        マウスボタン解放時の処理

        Args:
            event: マウスイベント
        """
        if event.inaxes != self.ax or not self.start_point:
            return

        # 選択領域の確定
        x0, y0 = self.start_point
        x1, y1 = event.xdata, event.ydata

        # 選択領域のサイズが十分であれば拡大
        if abs(x1 - x0) > 0.01 and abs(y1 - y0) > 0.01:
            # X軸の範囲を設定
            xmin, xmax = min(x0, x1), max(x0, x1)
            # Y軸の範囲を設定
            ymin, ymax = min(y0, y1), max(y0, y1)

            # 選択領域に拡大
            self.ax.set_xlim(xmin, xmax)
            self.ax.set_ylim(ymin, ymax)
            self.canvas.draw()

        # 選択領域のリセット
        self.start_point = None
        if self.selection_rect:
            self.selection_rect.remove()
            self.selection_rect = None
            self.canvas.draw()
