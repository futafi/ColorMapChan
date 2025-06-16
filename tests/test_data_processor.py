"""
Tests for data_processor module
Phase 5.1: Basic filtering functionality tests
"""

import unittest
import pandas as pd
import numpy as np
from core.data_processor import (
    DataProcessor, FilterManager, ValueFilter, RangeFilter
)


class TestValueFilter(unittest.TestCase):
    """Test ValueFilter class"""
    
    def setUp(self):
        """Set up test data"""
        self.data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50],
            'C': ['x', 'y', 'z', 'x', 'y']
        })
    
    def test_numeric_value_filter(self):
        """Test filtering with numeric values"""
        filter_obj = ValueFilter('A', 3)
        result = filter_obj.apply(self.data)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['A'], 3)
        self.assertEqual(result.iloc[0]['B'], 30)
    
    def test_string_value_filter(self):
        """Test filtering with string values"""
        filter_obj = ValueFilter('C', 'x')
        result = filter_obj.apply(self.data)
        
        self.assertEqual(len(result), 2)
        self.assertTrue(all(result['C'] == 'x'))
    
    def test_no_matches(self):
        """Test filtering with no matches"""
        filter_obj = ValueFilter('A', 10)
        result = filter_obj.apply(self.data)
        
        self.assertEqual(len(result), 0)
    
    def test_invalid_column(self):
        """Test filtering with invalid column"""
        filter_obj = ValueFilter('INVALID', 1)
        
        with self.assertRaises(ValueError):
            filter_obj.apply(self.data)
    
    def test_get_description(self):
        """Test filter description"""
        filter_obj = ValueFilter('A', 3)
        description = filter_obj.get_description()
        
        self.assertEqual(description, "A == 3")


class TestRangeFilter(unittest.TestCase):
    """Test RangeFilter class"""
    
    def setUp(self):
        """Set up test data"""
        self.data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50],
            'C': [1.1, 2.2, 3.3, 4.4, 5.5]
        })
    
    def test_range_filter(self):
        """Test basic range filtering"""
        filter_obj = RangeFilter('A', 2, 4)
        result = filter_obj.apply(self.data)
        
        self.assertEqual(len(result), 3)
        self.assertTrue(all(result['A'] >= 2))
        self.assertTrue(all(result['A'] <= 4))
    
    def test_range_filter_float(self):
        """Test range filtering with float values"""
        filter_obj = RangeFilter('C', 2.0, 4.0)
        result = filter_obj.apply(self.data)
        
        self.assertEqual(len(result), 2)  # 2.2 and 3.3
        self.assertTrue(all(result['C'] >= 2.0))
        self.assertTrue(all(result['C'] <= 4.0))
    
    def test_range_filter_edge_cases(self):
        """Test range filtering edge cases"""
        # Single value range
        filter_obj = RangeFilter('A', 3, 3)
        result = filter_obj.apply(self.data)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['A'], 3)
    
    def test_no_matches_range(self):
        """Test range filtering with no matches"""
        filter_obj = RangeFilter('A', 10, 20)
        result = filter_obj.apply(self.data)
        
        self.assertEqual(len(result), 0)
    
    def test_invalid_range(self):
        """Test invalid range (min > max)"""
        with self.assertRaises(ValueError):
            RangeFilter('A', 5, 2)
    
    def test_invalid_column_range(self):
        """Test range filtering with invalid column"""
        filter_obj = RangeFilter('INVALID', 1, 5)
        
        with self.assertRaises(ValueError):
            filter_obj.apply(self.data)
    
    def test_get_description_range(self):
        """Test range filter description"""
        filter_obj = RangeFilter('A', 2, 4)
        description = filter_obj.get_description()
        
        self.assertEqual(description, "2 <= A <= 4")


class TestFilterManager(unittest.TestCase):
    """Test FilterManager class"""
    
    def setUp(self):
        """Set up test data"""
        self.data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50],
            'C': ['x', 'y', 'z', 'x', 'y']
        })
        self.manager = FilterManager()
        self.manager.set_data(self.data)
    
    def test_add_single_filter(self):
        """Test adding a single filter"""
        filter_obj = ValueFilter('A', 3)
        self.manager.add_filter(filter_obj)
        
        result = self.manager.get_filtered_data()
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['A'], 3)
    
    def test_add_multiple_filters(self):
        """Test adding multiple filters"""
        filter1 = RangeFilter('A', 2, 4)
        filter2 = ValueFilter('C', 'x')
        
        self.manager.add_filter(filter1)
        self.manager.add_filter(filter2)
        
        result = self.manager.get_filtered_data()
        self.assertEqual(len(result), 1)  # Only A=4, C='x' matches both
        self.assertEqual(result.iloc[0]['A'], 4)
        self.assertEqual(result.iloc[0]['C'], 'x')
    
    def test_remove_filter(self):
        """Test removing a filter"""
        filter1 = ValueFilter('A', 3)
        filter2 = ValueFilter('C', 'x')
        
        self.manager.add_filter(filter1)
        self.manager.add_filter(filter2)
        
        # Should have no results (A=3 has C='z', not 'x')
        result = self.manager.get_filtered_data()
        self.assertEqual(len(result), 0)
        
        # Remove one filter
        self.manager.remove_filter(filter2.id)
        result = self.manager.get_filtered_data()
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['A'], 3)
    
    def test_clear_all_filters(self):
        """Test clearing all filters"""
        filter1 = ValueFilter('A', 3)
        filter2 = RangeFilter('B', 20, 40)
        
        self.manager.add_filter(filter1)
        self.manager.add_filter(filter2)
        
        self.assertTrue(self.manager.has_filters())
        
        self.manager.clear_all_filters()
        
        self.assertFalse(self.manager.has_filters())
        result = self.manager.get_filtered_data()
        self.assertEqual(len(result), len(self.data))  # Should be original data
    
    def test_get_filter_statistics(self):
        """Test filter statistics"""
        filter_obj = RangeFilter('A', 2, 4)
        self.manager.add_filter(filter_obj)
        
        stats = self.manager.get_filter_statistics()
        
        self.assertEqual(stats['original_count'], 5)
        self.assertEqual(stats['filtered_count'], 3)
        self.assertEqual(stats['removed_count'], 2)
        self.assertAlmostEqual(stats['filtered_percentage'], 60.0)
        self.assertAlmostEqual(stats['removed_percentage'], 40.0)
    
    def test_get_filter_descriptions(self):
        """Test getting filter descriptions"""
        filter1 = ValueFilter('A', 3)
        filter2 = RangeFilter('B', 20, 40)
        
        self.manager.add_filter(filter1)
        self.manager.add_filter(filter2)
        
        descriptions = self.manager.get_filter_descriptions()
        
        self.assertEqual(len(descriptions), 2)
        self.assertIn("A == 3", descriptions)
        self.assertIn("20 <= B <= 40", descriptions)
    
    def test_get_available_columns(self):
        """Test getting available columns"""
        columns = self.manager.get_available_columns()
        
        self.assertEqual(len(columns), 3)
        self.assertIn('A', columns)
        self.assertIn('B', columns)
        self.assertIn('C', columns)


class TestDataProcessor(unittest.TestCase):
    """Test DataProcessor class"""
    
    def setUp(self):
        """Set up test data"""
        self.data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50],
            'C': ['x', 'y', 'z', 'x', 'y']
        })
        self.processor = DataProcessor()
        self.processor.set_data(self.data)
    
    def test_add_value_filter(self):
        """Test adding value filter through processor"""
        self.processor.add_value_filter('A', 3)
        
        result = self.processor.get_processed_data()
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['A'], 3)
    
    def test_add_range_filter(self):
        """Test adding range filter through processor"""
        self.processor.add_range_filter('A', 2, 4)
        
        result = self.processor.get_processed_data()
        self.assertEqual(len(result), 3)
        self.assertTrue(all(result['A'] >= 2))
        self.assertTrue(all(result['A'] <= 4))
    
    def test_get_filter_info(self):
        """Test getting filter information"""
        self.processor.add_value_filter('A', 3)
        
        info = self.processor.get_filter_info()
        
        self.assertTrue(info['has_filters'])
        self.assertEqual(len(info['descriptions']), 1)
        self.assertIn("A == 3", info['descriptions'])
        self.assertEqual(info['statistics']['filtered_count'], 1)
        self.assertEqual(len(info['available_columns']), 3)
        
        # Test filter_list functionality
        self.assertEqual(len(info['filter_list']), 1)
        filter_item = info['filter_list'][0]
        self.assertEqual(filter_item['column'], 'A')
        self.assertEqual(filter_item['type'], 'value')
        self.assertEqual(filter_item['description'], 'A == 3')
    
    def test_clear_all_filters_processor(self):
        """Test clearing all filters through processor"""
        self.processor.add_value_filter('A', 3)
        self.processor.add_range_filter('B', 20, 40)
        
        info = self.processor.get_filter_info()
        self.assertTrue(info['has_filters'])
        
        self.processor.clear_all_filters()
        
        info = self.processor.get_filter_info()
        self.assertFalse(info['has_filters'])
        
        result = self.processor.get_processed_data()
        self.assertEqual(len(result), len(self.data))


class TestFilterManagerAdvanced(unittest.TestCase):
    """Test advanced FilterManager functionality for Phase 5.2"""
    
    def setUp(self):
        """Set up test data"""
        self.data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50],
            'C': ['x', 'y', 'z', 'x', 'y']
        })
        self.manager = FilterManager()
        self.manager.set_data(self.data)
    
    def test_get_filter_list(self):
        """Test getting detailed filter list"""
        filter1 = ValueFilter('A', 3)
        filter2 = RangeFilter('B', 20, 40)
        
        self.manager.add_filter(filter1)
        self.manager.add_filter(filter2)
        
        filter_list = self.manager.get_filter_list()
        
        self.assertEqual(len(filter_list), 2)
        
        # Check first filter
        self.assertIn('id', filter_list[0])
        self.assertIn('description', filter_list[0])
        self.assertIn('column', filter_list[0])
        self.assertIn('type', filter_list[0])
        
        # Verify filter details
        value_filter = next(f for f in filter_list if f['type'] == 'value')
        range_filter = next(f for f in filter_list if f['type'] == 'range')
        
        self.assertEqual(value_filter['column'], 'A')
        self.assertEqual(value_filter['description'], 'A == 3')
        
        self.assertEqual(range_filter['column'], 'B')
        self.assertEqual(range_filter['description'], '20 <= B <= 40')
    
    def test_filter_list_empty(self):
        """Test filter list when no filters are active"""
        filter_list = self.manager.get_filter_list()
        self.assertEqual(len(filter_list), 0)
    
    def test_filter_list_after_removal(self):
        """Test filter list after removing filters"""
        filter1 = ValueFilter('A', 3)
        filter2 = RangeFilter('B', 20, 40)
        
        self.manager.add_filter(filter1)
        self.manager.add_filter(filter2)
        
        # Initially should have 2 filters
        filter_list = self.manager.get_filter_list()
        self.assertEqual(len(filter_list), 2)
        
        # Remove one filter
        self.manager.remove_filter(filter1.id)
        
        # Should now have 1 filter
        filter_list = self.manager.get_filter_list()
        self.assertEqual(len(filter_list), 1)
        self.assertEqual(filter_list[0]['type'], 'range')


if __name__ == '__main__':
    unittest.main()