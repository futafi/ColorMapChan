"""
コントロールパネルモジュール

軸選択、フィルタリングなどのコントロールを提供します。
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class ControlPanel:
    """
    コントロールパネルクラス

    軸選択、フィルタリングなどのコントロールを提供します。
    """

    def __init__(self, parent, controller):
        """
        コントロールパネルの初期化

        Args:
            parent: 親ウィジェット
            controller: アプリケーションコントローラー
        """
        self.parent = parent
        self.controller = controller

        # データの状態
        self.columns = []
        self.x_column = tk.StringVar()
        self.y_column = tk.StringVar()
        self.value_column = tk.StringVar()
        self.filter_column = tk.StringVar()
        self.filter_value = tk.DoubleVar()
        self.colormap = tk.StringVar(value="plasma")  # デフォルトのカラーマップ
        self.log_scale = tk.BooleanVar(value=False)   # デフォルトは線形スケール
        self.file_format = tk.StringVar(value="auto")  # デフォルトは自動検出

        # 表示範囲
        self.x_min = tk.DoubleVar()
        self.x_max = tk.DoubleVar()
        self.y_min = tk.DoubleVar()
        self.y_max = tk.DoubleVar()
        self.value_min = tk.DoubleVar()
        self.value_max = tk.DoubleVar()

        self._create_widgets()

    def _create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # タイトル
        title_label = ttk.Label(self.frame, text="コントロールパネル", font=("", 12, "bold"))
        title_label.pack(pady=5)

        # 区切り線
        separator = ttk.Separator(self.frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=5)

        # ファイル形式フレーム
        format_frame = ttk.LabelFrame(self.frame, text="ファイル形式")
        format_frame.pack(fill=tk.X, pady=5)

        # ファイル形式選択
        format_select_frame = ttk.Frame(format_frame)
        format_select_frame.pack(fill=tk.X, pady=2)
        ttk.Label(format_select_frame, text="形式:").pack(side=tk.LEFT, padx=5)
        self.format_combo = ttk.Combobox(format_select_frame, textvariable=self.file_format, state="readonly")
        self.format_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.format_combo["values"] = ("自動検出", "標準CSV", "Sample2形式", "Sample3形式")
        self.format_combo.current(0)

        # 区切り線
        separator = ttk.Separator(self.frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=5)

        # 軸設定フレーム
        axis_frame = ttk.LabelFrame(self.frame, text="軸設定")
        axis_frame.pack(fill=tk.X, pady=5)

        # X軸選択
        x_frame = ttk.Frame(axis_frame)
        x_frame.pack(fill=tk.X, pady=2)
        ttk.Label(x_frame, text="X軸:").pack(side=tk.LEFT, padx=5)
        self.x_combo = ttk.Combobox(x_frame, textvariable=self.x_column, state="readonly")
        self.x_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.x_combo.bind("<<ComboboxSelected>>", self._on_axis_change)

        # Y軸選択
        y_frame = ttk.Frame(axis_frame)
        y_frame.pack(fill=tk.X, pady=2)
        ttk.Label(y_frame, text="Y軸:").pack(side=tk.LEFT, padx=5)
        self.y_combo = ttk.Combobox(y_frame, textvariable=self.y_column, state="readonly")
        self.y_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.y_combo.bind("<<ComboboxSelected>>", self._on_axis_change)

        # 値選択
        value_frame = ttk.Frame(axis_frame)
        value_frame.pack(fill=tk.X, pady=2)
        ttk.Label(value_frame, text="値:").pack(side=tk.LEFT, padx=5)
        self.value_combo = ttk.Combobox(value_frame, textvariable=self.value_column, state="readonly")
        self.value_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.value_combo.bind("<<ComboboxSelected>>", self._on_axis_change)

        # 軸入れ替えボタン
        swap_button = ttk.Button(axis_frame, text="X軸とY軸を入れ替え", command=self._on_swap_axes)
        swap_button.pack(fill=tk.X, padx=5, pady=5)

        # 区切り線
        separator = ttk.Separator(self.frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=5)

        # フィルタリングフレーム
        filter_frame = ttk.LabelFrame(self.frame, text="フィルタリング")
        filter_frame.pack(fill=tk.X, pady=5)

        # フィルタ列選択
        filter_col_frame = ttk.Frame(filter_frame)
        filter_col_frame.pack(fill=tk.X, pady=2)
        ttk.Label(filter_col_frame, text="フィルタ列:").pack(side=tk.LEFT, padx=5)
        self.filter_combo = ttk.Combobox(filter_col_frame, textvariable=self.filter_column, state="readonly")
        self.filter_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.filter_combo.bind("<<ComboboxSelected>>", self._on_filter_column_change)

        # フィルタ値選択
        filter_val_frame = ttk.Frame(filter_frame)
        filter_val_frame.pack(fill=tk.X, pady=2)
        ttk.Label(filter_val_frame, text="フィルタ値:").pack(side=tk.LEFT, padx=5)
        self.filter_scale = ttk.Scale(filter_val_frame, variable=self.filter_value, from_=0, to=100, orient=tk.HORIZONTAL)
        self.filter_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.filter_scale.bind("<ButtonRelease-1>", self._on_filter_value_change)

        # フィルタ値表示
        self.filter_value_label = ttk.Label(filter_val_frame, text="0.0")
        self.filter_value_label.pack(side=tk.LEFT, padx=5)

        # 区切り線
        separator = ttk.Separator(self.frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=5)

        # 表示オプションフレーム
        display_frame = ttk.LabelFrame(self.frame, text="表示オプション")
        display_frame.pack(fill=tk.X, pady=5)

        # カラーマップ選択
        colormap_frame = ttk.Frame(display_frame)
        colormap_frame.pack(fill=tk.X, pady=2)
        ttk.Label(colormap_frame, text="カラーマップ:").pack(side=tk.LEFT, padx=5)
        self.colormap_combo = ttk.Combobox(colormap_frame, textvariable=self.colormap, state="readonly")
        self.colormap_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.colormap_combo["values"] = ("plasma", "viridis", "jet", "hot", "cool", "gray")
        self.colormap_combo.current(0)
        self.colormap_combo.bind("<<ComboboxSelected>>", self._on_colormap_change)

        # スケール選択
        scale_frame = ttk.Frame(display_frame)
        scale_frame.pack(fill=tk.X, pady=2)
        self.log_check = ttk.Checkbutton(scale_frame, text="対数スケール", variable=self.log_scale, command=self._on_scale_change)
        self.log_check.pack(side=tk.LEFT, padx=5)

        # 区切り線
        separator = ttk.Separator(self.frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=5)

        # 表示範囲フレーム
        range_frame = ttk.LabelFrame(self.frame, text="表示範囲")
        range_frame.pack(fill=tk.X, pady=5)

        # X軸範囲
        x_range_frame = ttk.Frame(range_frame)
        x_range_frame.pack(fill=tk.X, pady=2)
        ttk.Label(x_range_frame, text="X範囲:").pack(side=tk.LEFT, padx=5)
        self.x_min_entry = ttk.Entry(x_range_frame, textvariable=self.x_min, width=8)
        self.x_min_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(x_range_frame, text="～").pack(side=tk.LEFT)
        self.x_max_entry = ttk.Entry(x_range_frame, textvariable=self.x_max, width=8)
        self.x_max_entry.pack(side=tk.LEFT, padx=2)

        # Y軸範囲
        y_range_frame = ttk.Frame(range_frame)
        y_range_frame.pack(fill=tk.X, pady=2)
        ttk.Label(y_range_frame, text="Y範囲:").pack(side=tk.LEFT, padx=5)
        self.y_min_entry = ttk.Entry(y_range_frame, textvariable=self.y_min, width=8)
        self.y_min_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(y_range_frame, text="～").pack(side=tk.LEFT)
        self.y_max_entry = ttk.Entry(y_range_frame, textvariable=self.y_max, width=8)
        self.y_max_entry.pack(side=tk.LEFT, padx=2)

        # 値範囲
        value_range_frame = ttk.Frame(range_frame)
        value_range_frame.pack(fill=tk.X, pady=2)
        ttk.Label(value_range_frame, text="値範囲:").pack(side=tk.LEFT, padx=5)
        self.value_min_entry = ttk.Entry(value_range_frame, textvariable=self.value_min, width=8)
        self.value_min_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(value_range_frame, text="～").pack(side=tk.LEFT)
        self.value_max_entry = ttk.Entry(value_range_frame, textvariable=self.value_max, width=8)
        self.value_max_entry.pack(side=tk.LEFT, padx=2)

        # 範囲適用ボタン
        apply_button = ttk.Button(range_frame, text="範囲を適用", command=self._on_apply_range)
        apply_button.pack(fill=tk.X, padx=5, pady=5)

        # 区切り線
        separator = ttk.Separator(self.frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=5)

        # リセットボタン
        reset_button = ttk.Button(self.frame, text="表示をリセット", command=self._on_reset)
        reset_button.pack(fill=tk.X, padx=5, pady=5)

    def update_columns(self, columns):
        """
        列リストの更新

        Args:
            columns (list): 列名のリスト
        """
        self.columns = columns

        # コンボボックスの更新
        self.x_combo["values"] = columns
        self.y_combo["values"] = columns
        self.value_combo["values"] = columns
        self.filter_combo["values"] = columns

        # デフォルト値の設定
        if len(columns) >= 3:
            self.x_combo.current(0)
            self.y_combo.current(1)
            self.value_combo.current(2)
            self.filter_combo.current(0)

    def update_filter_values(self, values):
        """
        フィルタ値リストの更新

        Args:
            values (list): フィルタ値のリスト
        """
        if not values:
            return

        # スケールの範囲を更新
        min_val = min(values)
        max_val = max(values)
        self.filter_scale.configure(from_=min_val, to=max_val)

        # デフォルト値の設定
        self.filter_value.set(min_val)
        self.filter_value_label.configure(text=f"{min_val:.6g}")

    def update_ranges(self, x_range, y_range, value_range):
        """
        表示範囲の更新

        Args:
            x_range (tuple): X軸の範囲 (min, max)
            y_range (tuple): Y軸の範囲 (min, max)
            value_range (tuple): 値の範囲 (min, max)
        """
        # X軸範囲
        self.x_min.set(x_range[0])
        self.x_max.set(x_range[1])

        # Y軸範囲
        self.y_min.set(y_range[0])
        self.y_max.set(y_range[1])

        # 値範囲
        self.value_min.set(value_range[0])
        self.value_max.set(value_range[1])

    def _on_axis_change(self, event):
        """
        軸変更時の処理

        Args:
            event: イベント情報
        """
        # 同じ列が選択されていないか確認
        if self.x_column.get() == self.y_column.get():
            messagebox.showwarning("警告", "X軸とY軸に同じ列を選択することはできません。")
            return

        # コントローラーに通知
        self.controller.set_axes(
            self.x_column.get(),
            self.y_column.get(),
            self.value_column.get()
        )

    def _on_swap_axes(self):
        """軸入れ替え時の処理"""
        # X軸とY軸の値を入れ替え
        x_val = self.x_column.get()
        y_val = self.y_column.get()

        self.x_column.set(y_val)
        self.y_column.set(x_val)

        # コントローラーに通知
        self.controller.set_axes(
            self.x_column.get(),
            self.y_column.get(),
            self.value_column.get()
        )

    def _on_filter_column_change(self, event):
        """
        フィルタ列変更時の処理

        Args:
            event: イベント情報
        """
        # コントローラーに通知
        self.controller.update_filter_values(self.filter_column.get())

    def _on_filter_value_change(self, event):
        """
        フィルタ値変更時の処理

        Args:
            event: イベント情報
        """
        # 値表示の更新
        value = self.filter_value.get()
        self.filter_value_label.configure(text=f"{value:.6g}")

        # コントローラーに通知
        self.controller.set_filter(
            self.filter_column.get(),
            value
        )

    def _on_colormap_change(self, event):
        """
        カラーマップ変更時の処理

        Args:
            event: イベント情報
        """
        # コントローラーに通知
        self.controller.set_colormap(self.colormap.get())

    def _on_scale_change(self):
        """スケール変更時の処理"""
        # コントローラーに通知
        self.controller.set_scale(self.log_scale.get())

    def _on_apply_range(self):
        """範囲適用時の処理"""
        try:
            # 入力値の取得
            x_min = float(self.x_min.get())
            x_max = float(self.x_max.get())
            y_min = float(self.y_min.get())
            y_max = float(self.y_max.get())
            value_min = float(self.value_min.get())
            value_max = float(self.value_max.get())

            # 範囲の妥当性チェック
            if x_min >= x_max:
                raise ValueError("X軸の最小値は最大値より小さくしてください。")
            if y_min >= y_max:
                raise ValueError("Y軸の最小値は最大値より小さくしてください。")
            if value_min >= value_max:
                raise ValueError("値の最小値は最大値より小さくしてください。")

            # コントローラーに通知
            self.controller.set_ranges(
                (x_min, x_max),
                (y_min, y_max),
                (value_min, value_max)
            )

        except ValueError as e:
            messagebox.showerror("エラー", str(e))

    def _on_reset(self):
        """リセット時の処理"""
        # コントローラーに通知
        self.controller.reset_view()
