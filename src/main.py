#!/usr/bin/env python3
"""
カラープロットちゃん - メインモジュール

アプリケーションのエントリーポイントです。
"""

from src.view.main_window import MainWindow
from src.controller.app_controller import AppController
import sys
import os

# 親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """メイン関数"""
    # アプリケーションコントローラーの作成
    app_controller = AppController()

    # メインウィンドウの作成
    main_window = MainWindow(app_controller)

    # コントローラーにメインウィンドウを設定
    app_controller.set_main_window(main_window)

    # アプリケーションの実行
    app_controller.run()


if __name__ == "__main__":
    main()
