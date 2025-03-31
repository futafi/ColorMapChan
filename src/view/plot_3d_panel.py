"""
3Dプロットパネルモジュール

matplotlib.mplot3dを使用した3Dプロット表示を提供します。
"""

import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib
matplotlib.use('TkAgg')


class Plot3DPanel:
    """
    3Dプロットパネルクラス

    matplotlib.mplot3dを使用した3Dプロット表示を提供します。
    """

    def __init__(self, parent, controller):
        """
        3Dプロットパネルの初期化

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
        self.c_data = None
        self.colormap = 'plasma'  # デフォルトのカラーマップ
        self.wireframe = False    # ワイヤーフレーム表示
        self.surface = None       # サーフェスプロットの参照
        self.colorbar = None      # カラーバーの参照

        self._create_widgets()

    def _create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Figureの作成
        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figure.add_subplot(111, projection='3d')

        # キャンバスの作成
        self.canvas = FigureCanvasTkAgg(self.figure, self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # ツールバーの作成
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # マウスイベントの設定
        self.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.canvas.mpl_connect('button_press_event', self._on_click)

    def plot_3d_surface(self, x_data, y_data, z_data, c_data=None, x_label=None, y_label=None, z_label=None, c_label=None, title=None):
        """
        3Dサーフェスプロットの描画

        Args:
            x_data (numpy.ndarray): X軸のデータ
            y_data (numpy.ndarray): Y軸のデータ
            z_data (numpy.ndarray): Z軸のデータ（高さ）
            c_data (numpy.ndarray, optional): カラーマップの値（省略時はz_dataを使用）
            x_label (str, optional): X軸のラベル
            y_label (str, optional): Y軸のラベル
            z_label (str, optional): Z軸のラベル
            c_label (str, optional): カラー値のラベル
            title (str, optional): プロットのタイトル
        """
        self.x_data = x_data
        self.y_data = y_data
        self.z_data = z_data
        self.c_data = c_data if c_data is not None else z_data

        # Figureを完全にクリア
        self.figure.clear()

        # 新しいAxesを作成
        self.ax = self.figure.add_subplot(111, projection='3d')

        # 無効な値（NaN）を含む場合はマスク
        mask = ~np.isnan(z_data)
        if not np.any(mask):
            self.ax.text(0.5, 0.5, 0.5, "有効なデータがありません", ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return

        # サーフェスプロットの描画
        if self.wireframe:
            # ワイヤーフレーム表示
            self.surface = self.ax.plot_wireframe(
                x_data, y_data, z_data,
                rstride=1, cstride=1,
                linewidth=0.5
            )
            # 別途カラーマップを表示
            self.surface = self.ax.scatter(
                x_data.flatten(), y_data.flatten(), z_data.flatten(),
                c=self.c_data.flatten(),
                cmap=self.colormap,
                s=10
            )
        else:
            # サーフェス表示
            self.surface = self.ax.plot_surface(
                x_data, y_data, z_data,
                facecolors=matplotlib.cm.get_cmap(self.colormap)(
                    (self.c_data - np.nanmin(self.c_data)) / (np.nanmax(self.c_data) - np.nanmin(self.c_data))
                ),
                rstride=1, cstride=1,
                linewidth=0,
                antialiased=True,
                shade=True
            )

        # カラーバーの追加
        norm = matplotlib.colors.Normalize(vmin=np.nanmin(self.c_data), vmax=np.nanmax(self.c_data))
        sm = matplotlib.cm.ScalarMappable(cmap=self.colormap, norm=norm)
        sm.set_array([])
        self.colorbar = self.figure.colorbar(sm, ax=self.ax, label=c_label or '値')

        # 軸ラベルの設定
        self.ax.set_xlabel(x_label or 'X')
        self.ax.set_ylabel(y_label or 'Y')
        self.ax.set_zlabel(z_label or 'Z')

        # タイトルの設定（指定があれば）
        if title:
            self.ax.set_title(title)

        # キャンバスの更新
        self.canvas.draw()

    def set_colormap(self, colormap):
        """
        カラーマップの設定

        Args:
            colormap (str): カラーマップ名
        """
        self.colormap = colormap
        if self.z_data is not None:
            self.plot_3d_surface(
                self.x_data, self.y_data, self.z_data, self.c_data,
                self.ax.get_xlabel(), self.ax.get_ylabel(), self.ax.get_zlabel(),
                self.colorbar.ax.get_ylabel() if self.colorbar else None,
                self.ax.get_title()
            )

    def set_wireframe(self, wireframe):
        """
        ワイヤーフレーム表示の設定

        Args:
            wireframe (bool): ワイヤーフレーム表示の場合はTrue
        """
        self.wireframe = wireframe
        if self.z_data is not None:
            self.plot_3d_surface(
                self.x_data, self.y_data, self.z_data, self.c_data,
                self.ax.get_xlabel(), self.ax.get_ylabel(), self.ax.get_zlabel(),
                self.colorbar.ax.get_ylabel() if self.colorbar else None,
                self.ax.get_title()
            )

    def set_view_angle(self, elevation, azimuth):
        """
        視点角度の設定

        Args:
            elevation (float): 仰角（度）
            azimuth (float): 方位角（度）
        """
        if self.ax:
            self.ax.view_init(elev=elevation, azim=azimuth)
            self.canvas.draw()

    def _on_motion(self, event):
        """
        マウス移動時の処理

        Args:
            event: マウスイベント
        """
        if event.inaxes != self.ax:
            return

        # 3Dプロットではカーソル位置の値表示は複雑なため、
        # 現在の視点角度を表示する
        if hasattr(self.ax, 'elev') and hasattr(self.ax, 'azim'):
            status_text = f"視点: 仰角={self.ax.elev:.1f}°, 方位角={self.ax.azim:.1f}°"
            self.controller.update_status(status_text)

    def _on_click(self, event):
        """
        マウスクリック時の処理

        Args:
            event: マウスイベント
        """
        if event.inaxes != self.ax:
            return

        # 右クリックの場合はリセット
        if event.button == 3:
            self.controller.reset_view()
