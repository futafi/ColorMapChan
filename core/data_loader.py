"""
Data loader for CSV files
Phase 2: Support for PlainCSV, ParameterCSV, and AnalysisCSV formats
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
import re


class DataLoader:
    """Handles loading and parsing of CSV data files"""
    
    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        self.columns: List[str] = []
        self.file_path: Optional[Path] = None
        self.metadata: Dict[str, Any] = {}
        self.format_type: Optional[str] = None
    
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
            self.format_type = "plain_csv"
            
            return df
            
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty or has no data")
        except pd.errors.ParserError as e:
            raise ValueError(f"Failed to parse CSV file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading CSV file: {e}")
    
    def load_parameter_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load ParameterCSV format data (B1500A text2csv format)
        
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
            # Read all lines to parse metadata and find data section
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Parse metadata and find DataName line
            metadata = {}
            data_start_line = None
            columns = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                parts = [part.strip() for part in line.split(',')]
                
                # Store metadata
                if parts[0] in ['SetupTitle', 'PrimitiveTest']:
                    metadata[parts[0]] = parts[1] if len(parts) > 1 else ''
                elif parts[0] == 'TestParameter':
                    key = f"TestParameter.{parts[1]}" if len(parts) > 1 else "TestParameter"
                    metadata[key] = parts[2:] if len(parts) > 2 else []
                elif parts[0] == 'MetaData':
                    key = f"MetaData.{parts[1]}" if len(parts) > 1 else "MetaData" 
                    metadata[key] = parts[2] if len(parts) > 2 else ''
                
                # Find DataName line
                elif parts[0] == 'DataName':
                    columns = parts[1:]  # Skip 'DataName' itself
                    data_start_line = i + 1
                    break
            
            if data_start_line is None:
                raise ValueError("DataName section not found in ParameterCSV file")
            
            if not columns:
                raise ValueError("No column names found in DataName section")
            
            # Extract data rows (DataValue lines only)
            data_rows = []
            for i in range(data_start_line, len(lines)):
                line = lines[i].strip()
                if not line:
                    continue
                
                parts = [part.strip() for part in line.split(',')]
                if parts[0] == 'DataValue':
                    # Skip 'DataValue' and take the rest as data
                    data_values = parts[1:]
                    if len(data_values) == len(columns):
                        data_rows.append(data_values)
            
            if not data_rows:
                raise ValueError("No data rows found in ParameterCSV file")
            
            # Create DataFrame
            df = pd.DataFrame(data_rows, columns=columns)
            
            # Convert to numeric, handling scientific notation
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Store loaded data
            self.data = df
            self.columns = columns
            self.file_path = path
            self.metadata = metadata
            self.format_type = "parameter_csv"
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error loading ParameterCSV file: {e}")
    
    def load_analysis_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load AnalysisCSV format data (B1500A single file CSV format)
        
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
            # Read all lines to parse metadata and find data section
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Parse metadata and find AutoAnalysis section
            metadata = {}
            data_start_line = None
            columns = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # Check for AutoAnalysis marker
                if line == 'AutoAnalysis.Marker.Data.StartCondition,':
                    # Next line should contain column headers
                    if i + 1 < len(lines):
                        header_line = lines[i + 1].strip()
                        columns = [col.strip() for col in header_line.split(',')]
                        data_start_line = i + 2  # Data starts after header line
                        break
                else:
                    # Store metadata from header section
                    parts = [part.strip().strip('"') for part in line.split(',', 1)]
                    if len(parts) == 2:
                        metadata[parts[0]] = parts[1]
            
            if data_start_line is None:
                raise ValueError("AutoAnalysis.Marker.Data.StartCondition section not found")
            
            if not columns:
                raise ValueError("No column headers found after AutoAnalysis marker")
            
            # Extract data rows
            data_rows = []
            for i in range(data_start_line, len(lines)):
                line = lines[i].strip()
                if not line:
                    continue
                
                data_values = [val.strip().strip('"') for val in line.split(',')]
                if len(data_values) == len(columns):
                    data_rows.append(data_values)
            
            if not data_rows:
                raise ValueError("No data rows found in AnalysisCSV file")
            
            # Create DataFrame
            df = pd.DataFrame(data_rows, columns=columns)
            
            # Convert to numeric, handling scientific notation
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Store loaded data
            self.data = df
            self.columns = columns  
            self.file_path = path
            self.metadata = metadata
            self.format_type = "analysis_csv"
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error loading AnalysisCSV file: {e}")
    
    def load_auto(self, file_path: str) -> pd.DataFrame:
        """
        Automatically detect format and load CSV data
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            pandas DataFrame with loaded data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is unsupported
        """
        # Try formats in order: ParameterCSV -> AnalysisCSV -> PlainCSV
        format_attempts = [
            ("parameter_csv", self.load_parameter_csv),
            ("analysis_csv", self.load_analysis_csv),
            ("plain_csv", self.load_plain_csv)
        ]
        
        last_error = None
        
        for format_name, load_method in format_attempts:
            try:
                return load_method(file_path)
            except Exception as e:
                last_error = e
                continue
        
        # If all formats failed, raise the last error
        raise ValueError(f"Unsupported file format. Last error: {last_error}")
    
    def get_data(self) -> Optional[pd.DataFrame]:
        """Get currently loaded data"""
        return self.data
    
    def get_columns(self) -> List[str]:
        """Get column names from loaded data"""
        return self.columns
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata from loaded file"""
        return self.metadata
    
    def get_format_type(self) -> Optional[str]:
        """Get detected format type"""
        return self.format_type
    
    def get_info(self) -> Dict[str, Any]:
        """Get basic information about loaded data"""
        if self.data is None:
            return {"loaded": False}
            
        info = {
            "loaded": True,
            "file_path": str(self.file_path),
            "format_type": self.format_type,
            "rows": len(self.data),
            "columns": len(self.columns),
            "column_names": self.columns,
            "data_types": dict(self.data.dtypes.astype(str))
        }
        
        # Add metadata if available
        if self.metadata:
            info["metadata"] = self.metadata
            
        return info