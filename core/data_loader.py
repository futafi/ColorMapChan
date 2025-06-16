"""
Data loader for CSV files
Phase 1: PlainCSV format only
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any


class DataLoader:
    """Handles loading and parsing of CSV data files"""
    
    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        self.columns: List[str] = []
        self.file_path: Optional[Path] = None
    
    def load_plain_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load PlainCSV format data
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            pandas DataFrame with loaded data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            # Read CSV with header row
            df = pd.read_csv(path)
            
            # Validate data
            if df.empty:
                raise ValueError("CSV file is empty")
                
            # Store loaded data
            self.data = df
            self.columns = list(df.columns)
            self.file_path = path
            
            return df
            
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty or has no data")
        except pd.errors.ParserError as e:
            raise ValueError(f"Failed to parse CSV file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading CSV file: {e}")
    
    def get_data(self) -> Optional[pd.DataFrame]:
        """Get currently loaded data"""
        return self.data
    
    def get_columns(self) -> List[str]:
        """Get column names from loaded data"""
        return self.columns
    
    def get_info(self) -> Dict[str, Any]:
        """Get basic information about loaded data"""
        if self.data is None:
            return {"loaded": False}
            
        return {
            "loaded": True,
            "file_path": str(self.file_path),
            "rows": len(self.data),
            "columns": len(self.columns),
            "column_names": self.columns,
            "data_types": dict(self.data.dtypes.astype(str))
        }