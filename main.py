#!/usr/bin/env python3
"""
カラープロットちゃん - 2D/3D heatmap visualization application
Entry point with GUI/CLI mode switching
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="カラープロットちゃん - 2D/3D heatmap visualization"
    )
    parser.add_argument(
        "--cli", 
        action="store_true", 
        help="Run in CLI mode (for testing)"
    )
    parser.add_argument(
        "--file", 
        type=str, 
        help="Input CSV file path"
    )
    
    args = parser.parse_args()
    
    if args.cli:
        # CLI mode
        from cli.interface import run_cli
        run_cli(args.file)
    else:
        # GUI mode (default)
        from gui.app import run_gui
        run_gui()


if __name__ == "__main__":
    main()