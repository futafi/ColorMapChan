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

    def _on_frame_configure(self, event):
        """
        フレームサイズが変更されたときの処理

        Args:
            event: イベント情報
        """
        # キャンバスのスクロール領域を更新
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """
        キャンバスサイズが変更されたときの処理

        Args:
            event: イベント情報
        """
        # キャンバス内のフレームの幅を調整
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        """
        マウスホイール操作時の処理

        Args:
            event: イベント情報
        """
        # マウスホイールの方向に応じてスクロール
        # Windows: event.delta, macOS: event.num
        if event.delta:
            # Windows
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 4:
            # Linux: マウスホイール上回転
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            # Linux: マウスホイール下回転
            self.canvas.yview_scroll(1, "units")

    def _create_widgets(self):
        """ウィジェットの作成"""
        # 外側のフレーム
        self.outer_frame = ttk.Frame(self.parent)
        self.outer_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # スクロール可能なキャンバスを作成
        self.canvas = tk.Canvas(self.outer_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # スクロールバーを作成
        self.scrollbar = ttk.Scrollbar(self.outer_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # キャンバス内のフレーム
        self.frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.frame, anchor=tk.NW)

        # フレームサイズが変更されたときにキャンバスのスクロール領域を更新
        self.frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # マウスホイールでのスクロールを有効化
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # Windows
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)    # Linux/macOS
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)    # Linux/macOS

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

        # フィルタタイプ選択
        filter_type_frame = ttk.Frame(filter_frame)
        filter_type_frame.pack(fill=tk.X, pady=2)
        self.filter_type = tk.StringVar(value="value")
        ttk.Radiobutton(filter_type_frame, text="値フィルタ", variable=self.filter_type,
                        value="value", command=self._on_filter_type_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(filter_type_frame, text="範囲フィルタ", variable=self.filter_type,
                        value="range", command=self._on_filter_type_change).pack(side=tk.LEFT, padx=5)

        # 値フィルタフレーム
        self.value_filter_frame = ttk.Frame(filter_frame)
        self.value_filter_frame.pack(fill=tk.X, pady=2)

        # 値選択用ドロップダウン
        dropdown_frame = ttk.Frame(self.value_filter_frame)
        dropdown_frame.pack(fill=tk.X, pady=2)
        ttk.Label(dropdown_frame, text="値を選択:").pack(side=tk.LEFT, padx=5)
        self.filter_value_combo = ttk.Combobox(dropdown_frame, state="readonly")
        self.filter_value_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # 値入力用フィールド
        entry_frame = ttk.Frame(self.value_filter_frame)
        entry_frame.pack(fill=tk.X, pady=2)
        ttk.Label(entry_frame, text="値を入力:").pack(side=tk.LEFT, padx=5)
        self.filter_value_entry = ttk.Entry(entry_frame)
        self.filter_value_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # 範囲フィルタフレーム
        self.range_filter_frame = ttk.Frame(filter_frame)
        self.range_filter_frame.pack(fill=tk.X, pady=2)
        self.range_filter_frame.pack_forget()  # 初期状態では非表示

        # 最小値
        min_frame = ttk.Frame(self.range_filter_frame)
        min_frame.pack(fill=tk.X, pady=2)
        ttk.Label(min_frame, text="最小値:").pack(side=tk.LEFT, padx=5)
        self.filter_min_value = tk.DoubleVar()
        self.filter_min_entry = ttk.Entry(min_frame, textvariable=self.filter_min_value)
        self.filter_min_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # 最大値
        max_frame = ttk.Frame(self.range_filter_frame)
        max_frame.pack(fill=tk.X, pady=2)
        ttk.Label(max_frame, text="最大値:").pack(side=tk.LEFT, padx=5)
        self.filter_max_value = tk.DoubleVar()
        self.filter_max_entry = ttk.Entry(max_frame, textvariable=self.filter_max_value)
        self.filter_max_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # フィルタ追加ボタン
        filter_button_frame = ttk.Frame(filter_frame)
        filter_button_frame.pack(fill=tk.X, pady=2)
        self.add_filter_button = ttk.Button(filter_button_frame, text="フィルタを追加", command=self._on_add_filter)
        self.add_filter_button.pack(fill=tk.X, padx=5, pady=2)

        # 適用中のフィルタリスト
        filter_list_frame = ttk.LabelFrame(filter_frame, text="適用中のフィルタ")
        filter_list_frame.pack(fill=tk.X, pady=2)

        # フィルタリストを表示するキャンバスとスクロールバー
        filter_canvas_frame = ttk.Frame(filter_list_frame)
        filter_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.filter_canvas = tk.Canvas(filter_canvas_frame, height=100)
        self.filter_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        filter_scrollbar = ttk.Scrollbar(filter_canvas_frame, orient=tk.VERTICAL, command=self.filter_canvas.yview)
        filter_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.filter_canvas.configure(yscrollcommand=filter_scrollbar.set)

        # フィルタリストを表示するフレーム
        self.filter_list_inner_frame = ttk.Frame(self.filter_canvas)
        self.filter_canvas.create_window((0, 0), window=self.filter_list_inner_frame, anchor=tk.NW)
        self.filter_list_inner_frame.bind("<Configure>", lambda e: self.filter_canvas.configure(
            scrollregion=self.filter_canvas.bbox("all")))

        # すべてクリアボタン
        clear_button_frame = ttk.Frame(filter_frame)
        clear_button_frame.pack(fill=tk.X, pady=2)
        self.clear_filters_button = ttk.Button(clear_button_frame, text="すべてクリア", command=self._on_clear_filters)
        self.clear_filters_button.pack(fill=tk.X, padx=5, pady=2)

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

        # 断面表示ボタン
        profile_frame = ttk.Frame(display_frame)
        profile_frame.pack(fill=tk.X, pady=2)
        self.profile_mode = tk.BooleanVar(value=False)
        self.profile_button = ttk.Checkbutton(
            profile_frame,
            text="断面表示モード",
            variable=self.profile_mode,
            command=self._on_profile_mode_change
        )
        self.profile_button.pack(side=tk.LEFT, padx=5)

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

    def update_filter_values(self, values, is_numeric):
        """
        フィルタ値リストの更新

        Args:
            values (list): フィルタ値のリスト
            is_numeric (bool): 数値列かどうか
        """
        if not values:
            return

        # 数値列かどうかを記録
        self.is_numeric_column = is_numeric

        # ドロップダウンの値を更新
        sorted_values = sorted(values)
        self.filter_value_combo["values"] = sorted_values
        if sorted_values:
            self.filter_value_combo.current(0)

        if is_numeric:
            # 数値列の場合
            min_val = min(values)
            max_val = max(values)

            # 範囲フィルタの初期値を設定
            self.filter_min_value.set(min_val)
            self.filter_max_value.set(max_val)

            # 入力フィールドの初期値を設定
            self.filter_value_entry.delete(0, tk.END)
            self.filter_value_entry.insert(0, str(min_val))
        else:
            # 非数値列の場合は範囲フィルタを無効化
            if self.filter_type.get() == "range":
                self.filter_type.set("value")
                self._on_filter_type_change()

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

    def _on_filter_type_change(self):
        """フィルタタイプ変更時の処理"""
        filter_type = self.filter_type.get()

        if filter_type == "value":
            # 値フィルタを表示
            self.value_filter_frame.pack(fill=tk.X, pady=2)
            self.range_filter_frame.pack_forget()
        else:
            # 範囲フィルタを表示（数値列の場合のみ）
            if hasattr(self, 'is_numeric_column') and self.is_numeric_column:
                self.value_filter_frame.pack_forget()
                self.range_filter_frame.pack(fill=tk.X, pady=2)
            else:
                # 非数値列の場合は値フィルタに戻す
                self.filter_type.set("value")
                messagebox.showwarning("警告", "範囲フィルタは数値列のみ使用できます。")
                self._on_filter_type_change()

    def _on_add_filter(self):
        """フィルタ追加時の処理"""
        column = self.filter_column.get()
        if not column:
            messagebox.showwarning("警告", "フィルタ列を選択してください。")
            return

        filter_type = self.filter_type.get()

        try:
            if filter_type == "value":
                # 値フィルタの場合
                # 入力フィールドとドロップダウンの両方をチェック
                entry_value = self.filter_value_entry.get().strip()
                combo_value = self.filter_value_combo.get()

                # 入力フィールドに値がある場合はそちらを優先
                if entry_value:
                    if hasattr(self, 'is_numeric_column') and self.is_numeric_column:
                        try:
                            value = float(entry_value)
                        except ValueError:
                            messagebox.showwarning("警告", "数値を入力してください。")
                            return
                    else:
                        value = entry_value
                # 入力フィールドが空の場合はドロップダウンの値を使用
                elif combo_value:
                    value = combo_value
                    # 数値列の場合は数値に変換
                    if hasattr(self, 'is_numeric_column') and self.is_numeric_column:
                        try:
                            value = float(value)
                        except ValueError:
                            pass  # 変換できない場合はそのまま使用
                else:
                    messagebox.showwarning("警告", "フィルタ値を選択または入力してください。")
                    return

                # コントローラーに通知
                self.controller.add_value_filter(column, value)
            else:
                # 範囲フィルタの場合
                min_val = self.filter_min_value.get()
                max_val = self.filter_max_value.get()

                if min_val > max_val:
                    messagebox.showwarning("警告", "最小値は最大値より小さくしてください。")
                    return

                # コントローラーに通知
                self.controller.add_range_filter(column, min_val, max_val)

            # フィルタリストを更新
            self._update_filter_list()

        except Exception as e:
            messagebox.showerror("エラー", str(e))

    def _on_clear_filters(self):
        """すべてのフィルタをクリア"""
        # コントローラーに通知
        self.controller.clear_filters()

        # フィルタリストを更新
        self._update_filter_list()

    def _update_filter_list(self):
        """フィルタリストの更新"""
        # 既存のフィルタリストをクリア
        for widget in self.filter_list_inner_frame.winfo_children():
            widget.destroy()

        # フィルタ情報を取得
        filter_summary = self.controller.get_filter_summary()

        # 値フィルタの表示
        for column, value in filter_summary["value_filters"].items():
            filter_frame = ttk.Frame(self.filter_list_inner_frame)
            filter_frame.pack(fill=tk.X, pady=1)

            # フィルタ情報のラベル
            filter_text = f"{column} = {value}"
            ttk.Label(filter_frame, text=filter_text).pack(side=tk.LEFT, padx=5)

            # 削除ボタン
            delete_button = ttk.Button(filter_frame, text="×", width=2,
                                       command=lambda col=column: self._on_delete_filter(col))
            delete_button.pack(side=tk.RIGHT, padx=5)

        # 範囲フィルタの表示
        for column, (min_val, max_val) in filter_summary["range_filters"].items():
            filter_frame = ttk.Frame(self.filter_list_inner_frame)
            filter_frame.pack(fill=tk.X, pady=1)

            # フィルタ情報のラベル
            filter_text = f"{column} = {min_val:.6g}～{max_val:.6g}"
            ttk.Label(filter_frame, text=filter_text).pack(side=tk.LEFT, padx=5)

            # 削除ボタン
            delete_button = ttk.Button(filter_frame, text="×", width=2,
                                       command=lambda col=column: self._on_delete_filter(col))
            delete_button.pack(side=tk.RIGHT, padx=5)

        # キャンバスの更新
        self.filter_canvas.update_idletasks()
        self.filter_canvas.configure(scrollregion=self.filter_canvas.bbox("all"))

    def _on_delete_filter(self, column):
        """
        フィルタ削除時の処理

        Args:
            column (str): 削除するフィルタの列名
        """
        # コントローラーに通知
        self.controller.clear_filters(column)

        # フィルタリストを更新
        self._update_filter_list()

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

    def _on_profile_mode_change(self):
        """断面表示モード変更時の処理"""
        enabled = self.profile_mode.get()
        self.controller.set_profile_mode(enabled)
        if enabled:
            self.controller.update_status("断面表示モード: ON - ヒートマップ上でクリックすると断面を表示します")
        else:
            self.controller.update_status("断面表示モード: OFF")

    def _on_reset(self):
        """リセット時の処理"""
        # 断面表示モードをOFFにする
        self.profile_mode.set(False)
        self._on_profile_mode_change()

        # コントローラーに通知
        self.controller.reset_view()
