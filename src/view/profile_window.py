"""
断面プロットウィンドウモジュール

X軸とY軸の断面プロットを表示します。
"""

import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np


class ProfileWindow:
    """
    断面プロットウィンドウクラス

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

        # X軸断面ツールバー
        self.x_toolbar = NavigationToolbar2Tk(self.x_canvas, self.x_frame)
        self.x_toolbar.update()

        # Y軸断面プロット
        self.y_figure = Figure(figsize=(6, 3), dpi=100)
        self.y_ax = self.y_figure.add_subplot(111)
        self.y_canvas = FigureCanvasTkAgg(self.y_figure, self.y_frame)
        self.y_canvas.draw()
        self.y_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Y軸断面ツールバー
        self.y_toolbar = NavigationToolbar2Tk(self.y_canvas, self.y_frame)
        self.y_toolbar.update()

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
