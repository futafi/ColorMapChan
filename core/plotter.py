"""
Plotting functionality using matplotlib
Phase 1: Basic 2D heatmap only
"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pandas as pd
from typing import Optional, Tuple, List


class Plotter:
    """Handles matplotlib-based plotting functionality"""
    
    def __init__(self):
        self.figure: Optional[plt.Figure] = None
        self.axes: Optional[plt.Axes] = None
        self.colorbar = None
        
    def create_2d_heatmap(
        self, 
        data: pd.DataFrame, 
        x_col: str, 
        y_col: str, 
        z_col: str,
        colormap: str = 'plasma'
    ) -> plt.Figure:
        """
        Create 2D heatmap plot
        
        Args:
            data: DataFrame containing the data
            x_col: Column name for X axis
            y_col: Column name for Y axis  
            z_col: Column name for color values (Z axis)
            colormap: Matplotlib colormap name
            
        Returns:
            matplotlib Figure object
        """
        # Validate columns exist
        required_cols = [x_col, y_col, z_col]
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing columns: {missing_cols}")
        
        # Extract data
        x = data[x_col].values
        y = data[y_col].values
        z = data[z_col].values
        
        # Create pivot table for heatmap
        pivot_data = data.pivot_table(
            index=y_col, 
            columns=x_col, 
            values=z_col, 
            fill_value=np.nan
        )
        
        # Create figure and plot
        self.figure, self.axes = plt.subplots(figsize=(10, 8))
        
        # Create heatmap
        im = self.axes.imshow(
            pivot_data.values,
            aspect='auto',
            origin='lower',
            extent=[
                pivot_data.columns.min(), pivot_data.columns.max(),
                pivot_data.index.min(), pivot_data.index.max()
            ],
            cmap=colormap
        )
        
        # Add colorbar
        if self.colorbar is not None:
            self.colorbar.remove()
        self.colorbar = plt.colorbar(im, ax=self.axes)
        self.colorbar.set_label(z_col)
        
        # Set labels and title
        self.axes.set_xlabel(x_col)
        self.axes.set_ylabel(y_col)
        self.axes.set_title(f'2D Heatmap: {z_col}')
        
        # Enable interactive features
        self.axes.grid(True, alpha=0.3)
        
        return self.figure
    
    def get_figure(self) -> Optional[plt.Figure]:
        """Get current figure"""
        return self.figure
    
    def clear(self):
        """Clear current plot"""
        if self.figure is not None:
            plt.close(self.figure)
            self.figure = None
            self.axes = None
            self.colorbar = None
    
    def save_png(self, filepath: str, dpi: int = 300):
        """
        Save current plot as PNG
        
        Args:
            filepath: Output file path
            dpi: Resolution in dots per inch
        """
        if self.figure is None:
            raise ValueError("No figure to save")
            
        self.figure.savefig(filepath, dpi=dpi, bbox_inches='tight')
    
    def get_available_colormaps(self) -> List[str]:
        """Get list of available colormap names"""
        return ['plasma', 'viridis', 'jet', 'hot', 'cool', 'gray']