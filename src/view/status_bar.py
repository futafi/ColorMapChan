"""
ステータスバーモジュール

ステータスバーを提供します。
"""

import tkinter as tk
from tkinter import ttk


class StatusBar:
    """
    ステータスバークラス

    ステータスバーを提供します。
    """

    def __init__(self, parent):
        """
        ステータスバーの初期化

        Args:
            parent: 親ウィジェット
        """
        self.parent = parent
        self._create_widgets()

    def _create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        self.frame = ttk.Frame(self.parent, relief=tk.SUNKEN, borderwidth=1)
        self.frame.pack(fill=tk.X, side=tk.BOTTOM, padx=2, pady=2)

        # ステータスメッセージ
        self.status_var = tk.StringVar(value="準備完了")
        self.status_label = ttk.Label(self.frame, textvariable=self.status_var, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)

        # 座標表示
        self.coords_var = tk.StringVar(value="")
        self.coords_label = ttk.Label(self.frame, textvariable=self.coords_var, anchor=tk.E)
        self.coords_label.pack(side=tk.RIGHT, padx=5, pady=2)

    def set_message(self, message):
        """
        ステータスメッセージの設定

        Args:
            message (str): 表示するメッセージ
        """
        self.status_var.set(message)

    def set_coords(self, coords):
        """
        座標表示の設定

        Args:
            coords (str): 表示する座標情報
        """
        self.coords_var.set(coords)

    def clear(self):
        """ステータスバーのクリア"""
        self.status_var.set("")
        self.coords_var.set("")
