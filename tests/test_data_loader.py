"""
Tests for data_loader module
Phase 1: PlainCSV format tests
"""

import pytest
import pandas as pd
from pathlib import Path
from core.data_loader import DataLoader


class TestDataLoader:
    """Test cases for DataLoader class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.loader = DataLoader()
        self.test_file = Path("test_data/test_plain_csv.csv")
    
    def test_load_plain_csv_success(self):
        """Test successful loading of PlainCSV file"""
        df = self.loader.load_plain_csv(str(self.test_file))
        
        # Check data is loaded
        assert df is not None
        assert not df.empty
        assert len(df) > 0
        
        # Check expected columns exist
        expected_columns = ['VG1', 'VG2', 'VD', 'ID', 'IG1', 'IG2']
        for col in expected_columns:
            assert col in df.columns
    
    def test_load_nonexistent_file(self):
        """Test loading non-existent file raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            self.loader.load_plain_csv("nonexistent_file.csv")
    
    def test_get_data_before_loading(self):
        """Test get_data returns None when no data loaded"""
        assert self.loader.get_data() is None
    
    def test_get_data_after_loading(self):
        """Test get_data returns DataFrame after loading"""
        self.loader.load_plain_csv(str(self.test_file))
        data = self.loader.get_data()
        assert data is not None
        assert isinstance(data, pd.DataFrame)
    
    def test_get_columns_after_loading(self):
        """Test get_columns returns column list after loading"""
        self.loader.load_plain_csv(str(self.test_file))
        columns = self.loader.get_columns()
        assert isinstance(columns, list)
        assert len(columns) > 0
    
    def test_get_info_before_loading(self):
        """Test get_info returns not loaded status"""
        info = self.loader.get_info()
        assert info["loaded"] is False
    
    def test_get_info_after_loading(self):
        """Test get_info returns detailed info after loading"""
        self.loader.load_plain_csv(str(self.test_file))
        info = self.loader.get_info()
        
        assert info["loaded"] is True
        assert "file_path" in info
        assert "rows" in info
        assert "columns" in info
        assert "column_names" in info
        assert "data_types" in info
        assert info["rows"] > 0
        assert info["columns"] > 0