"""
Tests for data_loader module
Phase 2: Tests for all CSV formats (PlainCSV, ParameterCSV, AnalysisCSV)
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
        self.test_plain_csv = Path("test_data/test_plain_csv.csv")
        self.test_parameter_csv = Path("test_data/test_parameter_csv.csv")
        self.test_analysis_csv = Path("test_data/test_analysis_csv.csv")
    
    def test_load_plain_csv_success(self):
        """Test successful loading of PlainCSV file"""
        df = self.loader.load_plain_csv(str(self.test_plain_csv))
        
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
        self.loader.load_plain_csv(str(self.test_plain_csv))
        data = self.loader.get_data()
        assert data is not None
        assert isinstance(data, pd.DataFrame)
    
    def test_get_columns_after_loading(self):
        """Test get_columns returns column list after loading"""
        self.loader.load_plain_csv(str(self.test_plain_csv))
        columns = self.loader.get_columns()
        assert isinstance(columns, list)
        assert len(columns) > 0
    
    def test_get_info_before_loading(self):
        """Test get_info returns not loaded status"""
        info = self.loader.get_info()
        assert info["loaded"] is False
    
    def test_get_info_after_loading(self):
        """Test get_info returns detailed info after loading"""
        self.loader.load_plain_csv(str(self.test_plain_csv))
        info = self.loader.get_info()
        
        assert info["loaded"] is True
        assert "file_path" in info
        assert "format_type" in info
        assert "rows" in info
        assert "columns" in info
        assert "column_names" in info
        assert "data_types" in info
        assert info["rows"] > 0
        assert info["columns"] > 0
        assert info["format_type"] == "plain_csv"
    
    # ParameterCSV format tests
    def test_load_parameter_csv_success(self):
        """Test successful loading of ParameterCSV file"""
        df = self.loader.load_parameter_csv(str(self.test_parameter_csv))
        
        # Check data is loaded
        assert df is not None
        assert not df.empty
        assert len(df) == 36  # Expected 36 rows from test data
        
        # Check expected columns exist
        expected_columns = ['VG1', 'VG2', 'VD', 'ID', 'IG1', 'IG2', 'IS']
        assert list(df.columns) == expected_columns
        
        # Check format type
        assert self.loader.get_format_type() == "parameter_csv"
        
        # Check metadata is available
        metadata = self.loader.get_metadata()
        assert isinstance(metadata, dict)
        assert len(metadata) > 0
        assert 'SetupTitle' in metadata
    
    def test_load_analysis_csv_success(self):
        """Test successful loading of AnalysisCSV file"""
        df = self.loader.load_analysis_csv(str(self.test_analysis_csv))
        
        # Check data is loaded
        assert df is not None
        assert not df.empty
        assert len(df) == 36  # Expected 36 rows from test data
        
        # Check expected columns exist
        expected_columns = ['VG1', 'VG2', 'VD', 'ID', 'IG1', 'IG2', 'IS', 'VB', 'IB']
        assert list(df.columns) == expected_columns
        
        # Check format type
        assert self.loader.get_format_type() == "analysis_csv"
        
        # Check metadata is available
        metadata = self.loader.get_metadata()
        assert isinstance(metadata, dict)
        assert len(metadata) > 0
        assert 'Setup title' in metadata
    
    # Auto-detection tests
    def test_load_auto_plain_csv(self):
        """Test auto-detection correctly identifies PlainCSV"""
        df = self.loader.load_auto(str(self.test_plain_csv))
        assert df is not None
        assert self.loader.get_format_type() == "plain_csv"
        assert len(df.columns) == 6
    
    def test_load_auto_parameter_csv(self):
        """Test auto-detection correctly identifies ParameterCSV"""
        df = self.loader.load_auto(str(self.test_parameter_csv))
        assert df is not None
        assert self.loader.get_format_type() == "parameter_csv"
        assert len(df.columns) == 7
        assert len(df) == 36
    
    def test_load_auto_analysis_csv(self):
        """Test auto-detection correctly identifies AnalysisCSV"""
        df = self.loader.load_auto(str(self.test_analysis_csv))
        assert df is not None
        assert self.loader.get_format_type() == "analysis_csv"
        assert len(df.columns) == 9
        assert len(df) == 36
    
    # Error handling tests
    def test_load_parameter_csv_invalid_file(self):
        """Test ParameterCSV loader with invalid file"""
        with pytest.raises(ValueError, match="DataName section not found"):
            self.loader.load_parameter_csv(str(self.test_plain_csv))
    
    def test_load_analysis_csv_invalid_file(self):
        """Test AnalysisCSV loader with invalid file"""
        with pytest.raises(ValueError, match="AutoAnalysis.Marker.Data.StartCondition section not found"):
            self.loader.load_analysis_csv(str(self.test_plain_csv))
    
    def test_load_auto_nonexistent_file(self):
        """Test auto-loader with non-existent file"""
        with pytest.raises(ValueError, match="Unsupported file format"):
            self.loader.load_auto("nonexistent_file.csv")
    
    # Metadata and format tests
    def test_get_metadata_plain_csv(self):
        """Test metadata retrieval for PlainCSV (should be empty)"""
        self.loader.load_plain_csv(str(self.test_plain_csv))
        metadata = self.loader.get_metadata()
        assert isinstance(metadata, dict)
        assert len(metadata) == 0  # PlainCSV has no metadata
    
    def test_get_metadata_parameter_csv(self):
        """Test metadata retrieval for ParameterCSV"""
        self.loader.load_parameter_csv(str(self.test_parameter_csv))
        metadata = self.loader.get_metadata()
        assert isinstance(metadata, dict)
        assert len(metadata) > 0
        assert 'SetupTitle' in metadata
        assert 'PrimitiveTest' in metadata
    
    def test_get_metadata_analysis_csv(self):
        """Test metadata retrieval for AnalysisCSV"""
        self.loader.load_analysis_csv(str(self.test_analysis_csv))
        metadata = self.loader.get_metadata()
        assert isinstance(metadata, dict)
        assert len(metadata) > 0
        assert 'Setup title' in metadata
        assert 'Classic test name' in metadata