"""
Data processor for filtering and transformations
Phase 5: Filtering functionality
Phase 6: Data transformation functionality
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Union
from abc import ABC, abstractmethod


class Transformation(ABC):
    """Abstract base class for data transformations"""
    
    def __init__(self, source_column: str, name: str):
        self.source_column = source_column
        self.name = name
        self.result_column = f"{source_column}_{name}"
    
    @abstractmethod
    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply transformation to data and return DataFrame with new column"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get human-readable description of transformation"""
        pass
    
    def validate_column(self, data: pd.DataFrame) -> None:
        """Validate that source column exists and is numeric"""
        if self.source_column not in data.columns:
            raise ValueError(f"Column '{self.source_column}' not found in data")
        
        if not pd.api.types.is_numeric_dtype(data[self.source_column]):
            raise ValueError(f"Column '{self.source_column}' is not numeric")


class AbsTransformation(Transformation):
    """Transformation for absolute value calculation"""
    
    def __init__(self, source_column: str):
        super().__init__(source_column, "abs")
    
    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply absolute value transformation"""
        self.validate_column(data)
        
        result_data = data.copy()
        result_data[self.result_column] = np.abs(data[self.source_column])
        
        return result_data
    
    def get_description(self) -> str:
        """Get transformation description"""
        return f"abs({self.source_column}) → {self.result_column}"


class DiffTransformation(Transformation):
    """Transformation for difference calculation"""
    
    def __init__(self, source_column: str, order: int = 1):
        self.order = max(1, int(order))  # Ensure positive integer
        super().__init__(source_column, f"diff{self.order}")
    
    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply difference transformation"""
        self.validate_column(data)
        
        result_data = data.copy()
        
        # Calculate difference
        diff_values = np.diff(data[self.source_column].values, n=self.order)
        
        # Pad with NaN to maintain original length
        padded_diff = np.full(len(data), np.nan)
        padded_diff[self.order:] = diff_values
        
        result_data[self.result_column] = padded_diff
        
        return result_data
    
    def get_description(self) -> str:
        """Get transformation description"""
        if self.order == 1:
            return f"diff({self.source_column}) → {self.result_column}"
        else:
            return f"diff{self.order}({self.source_column}) → {self.result_column}"


class Filter(ABC):
    """Abstract base class for data filters"""
    
    def __init__(self, column: str, name: str):
        self.column = column
        self.name = name
        self.id = f"{name}_{column}"
    
    @abstractmethod
    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply filter to data and return filtered DataFrame"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get human-readable description of filter"""
        pass


class ValueFilter(Filter):
    """Filter for exact value matching"""
    
    def __init__(self, column: str, value: Union[str, float, int]):
        super().__init__(column, "value")
        self.value = value
        self.id = f"value_{column}_{value}"
    
    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply exact value filter"""
        if self.column not in data.columns:
            raise ValueError(f"Column '{self.column}' not found in data")
        
        return data[data[self.column] == self.value].copy()
    
    def get_description(self) -> str:
        """Get filter description"""
        return f"{self.column} == {self.value}"


class RangeFilter(Filter):
    """Filter for range-based filtering (min <= value <= max)"""
    
    def __init__(self, column: str, min_value: float, max_value: float):
        super().__init__(column, "range")
        self.min_value = min_value
        self.max_value = max_value
        self.id = f"range_{column}_{min_value}_{max_value}"
        
        if min_value > max_value:
            raise ValueError(f"min_value ({min_value}) cannot be greater than max_value ({max_value})")
    
    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply range filter"""
        if self.column not in data.columns:
            raise ValueError(f"Column '{self.column}' not found in data")
        
        mask = (data[self.column] >= self.min_value) & (data[self.column] <= self.max_value)
        return data[mask].copy()
    
    def get_description(self) -> str:
        """Get filter description"""
        return f"{self.min_value} <= {self.column} <= {self.max_value}"


class FilterManager:
    """Manages multiple filters and applies them to data"""
    
    def __init__(self):
        self.filters: Dict[str, Filter] = {}
        self.original_data: Optional[pd.DataFrame] = None
        self.filtered_data: Optional[pd.DataFrame] = None
    
    def set_data(self, data: pd.DataFrame) -> None:
        """Set original data for filtering"""
        self.original_data = data.copy()
        self.filtered_data = data.copy()
    
    def add_filter(self, filter_obj: Filter) -> None:
        """Add a new filter"""
        self.filters[filter_obj.id] = filter_obj
        self._apply_all_filters()
    
    def remove_filter(self, filter_id: str) -> None:
        """Remove a filter by ID"""
        if filter_id in self.filters:
            del self.filters[filter_id]
            self._apply_all_filters()
    
    def clear_all_filters(self) -> None:
        """Remove all filters"""
        self.filters.clear()
        self._apply_all_filters()
    
    def _apply_all_filters(self) -> None:
        """Apply all filters to original data"""
        if self.original_data is None:
            return
        
        # Start with original data
        filtered_data = self.original_data.copy()
        
        # Apply each filter sequentially
        for filter_obj in self.filters.values():
            filtered_data = filter_obj.apply(filtered_data)
        
        self.filtered_data = filtered_data
    
    def get_filtered_data(self) -> Optional[pd.DataFrame]:
        """Get currently filtered data"""
        return self.filtered_data
    
    def get_filter_descriptions(self) -> List[str]:
        """Get descriptions of all active filters"""
        return [filter_obj.get_description() for filter_obj in self.filters.values()]
    
    def get_filter_list(self) -> List[Dict[str, str]]:
        """Get list of filters with id and description"""
        return [
            {
                'id': filter_id,
                'description': filter_obj.get_description(),
                'column': filter_obj.column,
                'type': filter_obj.name
            }
            for filter_id, filter_obj in self.filters.items()
        ]
    
    def get_filter_statistics(self) -> Dict[str, Any]:
        """Get statistics about filtering results"""
        if self.original_data is None or self.filtered_data is None:
            return {}
        
        original_count = len(self.original_data)
        filtered_count = len(self.filtered_data)
        
        return {
            'original_count': original_count,
            'filtered_count': filtered_count,
            'filtered_percentage': (filtered_count / original_count * 100) if original_count > 0 else 0,
            'removed_count': original_count - filtered_count,
            'removed_percentage': ((original_count - filtered_count) / original_count * 100) if original_count > 0 else 0
        }
    
    def has_filters(self) -> bool:
        """Check if any filters are active"""
        return len(self.filters) > 0
    
    def get_available_columns(self) -> List[str]:
        """Get list of available columns for filtering"""
        if self.original_data is None:
            return []
        return list(self.original_data.columns)


class DataProcessor:
    """Main data processor class with filtering and transformation capabilities"""
    
    def __init__(self):
        self.filter_manager = FilterManager()
        self.transformations: Dict[str, Transformation] = {}
        self.transformed_data: Optional[pd.DataFrame] = None
    
    def set_data(self, data: pd.DataFrame) -> None:
        """Set data for processing"""
        self.filter_manager.set_data(data)
        self.transformations.clear()
        self.transformed_data = data.copy()
    
    def add_value_filter(self, column: str, value: Union[str, float, int]) -> None:
        """Add value filter"""
        filter_obj = ValueFilter(column, value)
        self.filter_manager.add_filter(filter_obj)
    
    def add_range_filter(self, column: str, min_value: float, max_value: float) -> None:
        """Add range filter"""
        filter_obj = RangeFilter(column, min_value, max_value)
        self.filter_manager.add_filter(filter_obj)
    
    def remove_filter(self, filter_id: str) -> None:
        """Remove filter by ID"""
        self.filter_manager.remove_filter(filter_id)
    
    def clear_all_filters(self) -> None:
        """Clear all filters"""
        self.filter_manager.clear_all_filters()
    
    def get_processed_data(self) -> Optional[pd.DataFrame]:
        """Get processed (filtered) data"""
        return self.filter_manager.get_filtered_data()
    
    def add_abs_transformation(self, column: str) -> str:
        """Add absolute value transformation"""
        if self.transformed_data is None:
            raise ValueError("No data loaded")
        
        transformation = AbsTransformation(column)
        self.transformed_data = transformation.apply(self.transformed_data)
        self.transformations[transformation.result_column] = transformation
        
        # Update filter manager with new data
        self.filter_manager.set_data(self.transformed_data)
        
        return transformation.result_column
    
    def add_diff_transformation(self, column: str, order: int = 1) -> str:
        """Add difference transformation"""
        if self.transformed_data is None:
            raise ValueError("No data loaded")
        
        transformation = DiffTransformation(column, order)
        self.transformed_data = transformation.apply(self.transformed_data)
        self.transformations[transformation.result_column] = transformation
        
        # Update filter manager with new data
        self.filter_manager.set_data(self.transformed_data)
        
        return transformation.result_column
    
    def remove_transformation(self, result_column: str) -> None:
        """Remove a transformation by result column name"""
        if result_column in self.transformations:
            del self.transformations[result_column]
            self._rebuild_transformed_data()
    
    def clear_all_transformations(self) -> None:
        """Clear all transformations"""
        self.transformations.clear()
        self._rebuild_transformed_data()
    
    def _rebuild_transformed_data(self) -> None:
        """Rebuild transformed data from original data and active transformations"""
        if self.filter_manager.original_data is None:
            return
        
        # Start with original data
        self.transformed_data = self.filter_manager.original_data.copy()
        
        # Apply all transformations
        for transformation in self.transformations.values():
            self.transformed_data = transformation.apply(self.transformed_data)
        
        # Update filter manager with transformed data
        self.filter_manager.set_data(self.transformed_data)
    
    def get_transformation_info(self) -> Dict[str, Any]:
        """Get transformation information"""
        return {
            'transformations': [
                {
                    'result_column': result_column,
                    'description': transformation.get_description(),
                    'source_column': transformation.source_column,
                    'type': transformation.name
                }
                for result_column, transformation in self.transformations.items()
            ],
            'has_transformations': len(self.transformations) > 0,
            'available_columns': list(self.transformed_data.columns) if self.transformed_data is not None else []
        }
    
    def get_filter_info(self) -> Dict[str, Any]:
        """Get comprehensive filter information"""
        return {
            'descriptions': self.filter_manager.get_filter_descriptions(),
            'filter_list': self.filter_manager.get_filter_list(),
            'statistics': self.filter_manager.get_filter_statistics(),
            'has_filters': self.filter_manager.has_filters(),
            'available_columns': self.filter_manager.get_available_columns()
        }