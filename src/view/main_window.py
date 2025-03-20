"""
メインウィンドウモジュール

アプリケーションのメインウィンドウを提供します。
"""

from .status_bar import StatusBar
from .control_panel import ControlPanel
from .plot_panel import PlotPanel
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib
matplotlib.use('TkAgg')  # バックエンドの設定


class MainWindow:
    """
    メインウィンドウクラス

    アプリケーションのメインウィンドウを提供します。
    """

    def __init__(self, controller):
        """
        メインウィンドウの初期化

        Args:
            controller: アプリケーションコントローラー
        """
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("カラープロットちゃん")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        self._create_menu()
        self._create_layout()

        # ウィンドウが閉じられたときの処理
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_menu(self):
        """メニューバーの作成"""
        self.menu_bar = tk.Menu(self.root)

        # ファイルメニュー
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="開く", command=self._on_file_open)
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self._on_closing)
        self.menu_bar.add_cascade(label="ファイル", menu=file_menu)

        # 表示メニュー
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        view_menu.add_command(label="リセット表示", command=self._on_reset_view)
        self.menu_bar.add_cascade(label="表示", menu=view_menu)

        # ヘルプメニュー
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="バージョン情報", command=self._on_about)
        self.menu_bar.add_cascade(label="ヘルプ", menu=help_menu)

        self.root.config(menu=self.menu_bar)

    def _create_layout(self):
        """レイアウトの作成"""
        # メインフレーム
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 左右のペイン
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # 左側：コントロールパネル
        self.control_frame = ttk.Frame(self.paned_window, width=300)
        self.paned_window.add(self.control_frame, weight=1)

        # 右側：プロットパネル
        self.plot_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.plot_frame, weight=3)

        # ステータスバー
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, padx=5, pady=2)

        # 各コンポーネントの作成
        self.control_panel = ControlPanel(self.control_frame, self.controller)
        self.plot_panel = PlotPanel(self.plot_frame, self.controller)
        self.status_bar = StatusBar(self.status_frame)

    def run(self):
        """アプリケーションの実行"""
        self.root.mainloop()

    def _on_file_open(self):
        """ファイルを開くメニューの処理"""
        file_path = filedialog.askopenfilename(
            title="データファイルを開く",
            filetypes=[("CSVファイル", "*.csv"), ("すべてのファイル", "*.*")]
        )
        if file_path:
            try:
                # ファイル形式の取得
                file_format = self.control_panel.file_format.get()

                # ファイル形式の変換
                format_type = None
                if file_format == "標準CSV":
                    format_type = "standard"
                elif file_format == "Sample2形式":
                    format_type = "sample2"
                elif file_format == "Sample3形式":
                    format_type = "sample3"
                # 自動検出の場合はNoneのまま

                # ファイルの読み込み
                self.controller.load_file(file_path, format_type)
            except Exception as e:
                messagebox.showerror("エラー", f"ファイルの読み込みに失敗しました：{str(e)}")

    def _on_reset_view(self):
        """表示のリセット処理"""
        self.controller.reset_view()

    def _on_about(self):
        """バージョン情報の表示"""
        messagebox.showinfo(
            "バージョン情報",
            "カラープロットちゃん\nバージョン 0.1.0\n\n"
            "MOSFETの低温動作時に発生するクーロンブロッケード現象を分析するための\n"
            "対話型データ可視化アプリケーションです。"
        )

    def _on_closing(self):
        """ウィンドウが閉じられるときの処理"""
        if messagebox.askokcancel("終了確認", "アプリケーションを終了しますか？"):
            self.root.destroy()

    def update_status(self, message):
        """
        ステータスバーの更新

        Args:
            message (str): 表示するメッセージ
        """
        self.status_bar.set_message(message)

    def show_error(self, title, message):
        """
        エラーメッセージの表示

        Args:
            title (str): エラーのタイトル
            message (str): エラーメッセージ
        """
        messagebox.showerror(title, message)

    def show_info(self, title, message):
        """
        情報メッセージの表示

        Args:
            title (str): 情報のタイトル
            message (str): 情報メッセージ
        """
        messagebox.showinfo(title, message)
