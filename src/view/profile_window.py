"""
断面プロットウィンドウモジュール

X軸とY軸の断面プロットを表示します。
"""

import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import matplotlib.patches
import matplotlib.patches


class ProfileWindow:
    """

    X軸とY軸の断面プロットを表示します。
    """

    def __init__(self, parent, controller):
        """
        断面プロットウィンドウの初期化

        Args:
            parent: 親ウィンドウ
            controller: プロットコントローラー
        """
        self.window = tk.Toplevel(parent)
        self.window.title("断面プロット")
        self.window.geometry("800x600")
        self.controller = controller

        self._create_widgets()

    def _create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 上下に分割
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.VERTICAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # X軸断面フレーム
        self.x_frame = ttk.LabelFrame(self.paned_window, text="X軸断面")
        self.paned_window.add(self.x_frame, weight=1)

        # Y軸断面フレーム
        self.y_frame = ttk.LabelFrame(self.paned_window, text="Y軸断面")
        self.paned_window.add(self.y_frame, weight=1)

        # X軸断面プロット
        self.x_figure = Figure(figsize=(6, 3), dpi=100)
        self.x_ax = self.x_figure.add_subplot(111)
        self.x_canvas = FigureCanvasTkAgg(self.x_figure, self.x_frame)
        self.x_canvas.draw()
        self.x_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Y軸断面プロット
        self.y_figure = Figure(figsize=(6, 3), dpi=100)
        self.y_ax = self.y_figure.add_subplot(111)
        self.y_canvas = FigureCanvasTkAgg(self.y_figure, self.y_frame)
        self.y_canvas.draw()
        self.y_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # マウスイベントハンドラの設定
        self._setup_mouse_handlers()

        # 選択範囲の初期化
        self._zoom_start = None
        self._zoom_ax = None
        self._zoom_rect = None
        self._pan_start = None
        self._pan_ax = None

    def _setup_mouse_handlers(self):
        """マウスイベントハンドラの設定"""
        # X軸断面プロットのイベント
        self.x_canvas.mpl_connect('button_press_event', self._on_press)
        self.x_canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.x_canvas.mpl_connect('button_release_event', self._on_release)

        # Y軸断面プロットのイベント
        self.y_canvas.mpl_connect('button_press_event', self._on_press)
        self.y_canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.y_canvas.mpl_connect('button_release_event', self._on_release)

    def _on_press(self, event):
        """マウスボタン押下イベント処理"""
        if event.inaxes:
            if event.button == 1:  # 左ボタンの場合
                self._zoom_ax = event.inaxes
                self._zoom_start = (event.xdata, event.ydata)

                # 既存の選択範囲があれば削除
                if self._zoom_rect:
                    self._zoom_rect.remove()
                    self._zoom_rect = None

                # 新しい選択範囲の作成
                self._zoom_rect = matplotlib.patches.Rectangle(
                    (event.xdata, event.ydata),
                    0, 0,
                    linewidth=1,
                    edgecolor='r',
                    facecolor='none',
                    linestyle='--'
                )
                event.inaxes.add_patch(self._zoom_rect)
                event.canvas.draw_idle()

            elif event.button == 2:  # 中ボタンの場合
                self._pan_ax = event.inaxes
                self._pan_start = (event.xdata, event.ydata)
                event.canvas.get_tk_widget().config(cursor="fleur")

            elif event.button == 3:  # 右ボタンの場合
                self.reset_view(ax=event.inaxes)

    def _on_motion(self, event):
        """マウス移動イベント処理"""
        if event.inaxes:
            # ズーム処理（左ボタンドラッグ）
            if self._zoom_start and self._zoom_rect:
                # 選択範囲の更新
                x0, y0 = self._zoom_start
                x1, y1 = event.xdata, event.ydata
                width = x1 - x0
                height = y1 - y0

                self._zoom_rect.set_width(width)
                self._zoom_rect.set_height(height)
                event.canvas.draw_idle()

            # パン処理（中ボタンドラッグ）
            elif self._pan_start:
                # パン処理
                dx = event.xdata - self._pan_start[0]
                dy = event.ydata - self._pan_start[1]

                xlim = self._pan_ax.get_xlim()
                ylim = self._pan_ax.get_ylim()

                self._pan_ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
                self._pan_ax.set_ylim(ylim[0] - dy, ylim[1] - dy)

                self._pan_start = (event.xdata, event.ydata)
                event.canvas.draw_idle()

    def _on_release(self, event):
        """マウスボタン解放イベント処理"""
        if event.inaxes:
            # ズーム処理（左ボタンドラッグ）
            if self._zoom_start:
                # 選択範囲の確定
                x0, y0 = self._zoom_start
                x1, y1 = event.xdata, event.ydata

                # 選択範囲のサイズが十分であれば拡大
                if abs(x1 - x0) > 0.01 and abs(y1 - y0) > 0.01:
                    xmin, xmax = min(x0, x1), max(x0, x1)
                    ymin, ymax = min(y0, y1), max(y0, y1)

                    self._zoom_ax.set_xlim(xmin, xmax)
                    self._zoom_ax.set_ylim(ymin, ymax)
                    self._zoom_ax.figure.canvas.draw()

                # 選択範囲の削除
                if self._zoom_rect:
                    self._zoom_rect.remove()
                    self._zoom_rect = None

                self._zoom_start = None
                self._zoom_ax = None
                event.canvas.draw_idle()

            # パン終了（中ボタンドラッグ）
            elif self._pan_start:
                # パン終了
                self._pan_start = None
                self._pan_ax = None
                event.canvas.get_tk_widget().config(cursor="")

    def reset_view(self, ax=None):
        """
        表示範囲のリセット

        Args:
            ax: リセットする軸（Noneの場合は両方）
        """
        if ax:
            # 指定された軸のみリセット
            ax.autoscale(True)
            ax.relim()
            ax.autoscale_view()
            ax.figure.canvas.draw_idle()
        else:
            # 両方の軸をリセット
            if hasattr(self, 'x_ax') and self.x_ax:
                self.x_ax.autoscale(True)
                self.x_ax.relim()
                self.x_ax.autoscale_view()
                self.x_canvas.draw_idle()

            if hasattr(self, 'y_ax') and self.y_ax:
                self.y_ax.autoscale(True)
                self.y_ax.relim()
                self.y_ax.autoscale_view()
                self.y_canvas.draw_idle()

    def plot_profiles(self, x_data, x_values, y_data, y_values, click_point, x_label, y_label, value_label):
        """
        断面プロットの描画

        Args:
            x_data (array): X軸の座標値
            x_values (array): X軸断面の値
            y_data (array): Y軸の座標値
            y_values (array): Y軸断面の値
            click_point (tuple): クリックした点の座標 (x, y)
            x_label (str): X軸のラベル
            y_label (str): Y軸のラベル
            value_label (str): 値のラベル
        """
        # ウィンドウタイトルの更新
        self.window.title(f"断面プロット - 座標: ({click_point[0]:.6g}, {click_point[1]:.6g})")

        # X軸断面プロット
        self.x_ax.clear()
        self.x_ax.plot(x_data, x_values, 'b-o', markersize=4)
        self.x_ax.set_xlabel(x_label)
        self.x_ax.set_ylabel(value_label)
        self.x_ax.set_title(f'{y_label} = {click_point[1]:.6g} での断面')
        self.x_ax.grid(True)

        # クリックした点をマーク
        idx = np.abs(x_data - click_point[0]).argmin()
        if idx < len(x_values):
            self.x_ax.plot(click_point[0], x_values[idx], 'ro', markersize=6)

        # Y軸断面プロット
        self.y_ax.clear()
        self.y_ax.plot(y_data, y_values, 'g-o', markersize=4)
        self.y_ax.set_xlabel(y_label)
        self.y_ax.set_ylabel(value_label)
        self.y_ax.set_title(f'{x_label} = {click_point[0]:.6g} での断面')
        self.y_ax.grid(True)

        # クリックした点をマーク
        idx = np.abs(y_data - click_point[1]).argmin()
        if idx < len(y_values):
            self.y_ax.plot(click_point[1], y_values[idx], 'ro', markersize=6)

        # キャンバスの更新
        self.x_figure.tight_layout()
        self.x_canvas.draw()

        self.y_figure.tight_layout()
        self.y_canvas.draw()
