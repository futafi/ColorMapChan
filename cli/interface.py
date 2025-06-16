"""
CLI interface for testing
Phase 1: Basic file loading and info display
"""

from core.data_loader import DataLoader
from core.plotter import Plotter
import sys


def run_cli(file_path=None):
    """
    Run CLI interface
    
    Args:
        file_path: Optional path to CSV file
    """
    print("カラープロットちゃん - CLI Mode")
    print("=" * 40)
    
    if file_path is None:
        print("No file specified. Use --file option to specify a CSV file.")
        return
    
    try:
        # Load data
        loader = DataLoader()
        print(f"Loading file: {file_path}")
        data = loader.load_plain_csv(file_path)
        
        # Display basic info
        info = loader.get_info()
        print(f"\nFile loaded successfully!")
        print(f"Rows: {info['rows']}")
        print(f"Columns: {info['columns']}")
        print(f"Column names: {', '.join(info['column_names'])}")
        
        # Display data types
        print(f"\nData types:")
        for col, dtype in info['data_types'].items():
            print(f"  {col}: {dtype}")
        
        # Display sample data
        print(f"\nFirst 5 rows:")
        print(data.head().to_string())
        
        # Display basic statistics
        print(f"\nBasic statistics:")
        print(data.describe().to_string())
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)