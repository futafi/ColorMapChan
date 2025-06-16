"""
GUI application using tkinter
Phase 3: Enhanced GUI with real-time coordinate display
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np

from core.data_loader import DataLoader
from core.plotter import Plotter


class ColorMapApp:
    """Main GUI application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("カラープロットちゃん")
        self.root.geometry("1200x800")
        
        # Initialize core components
        self.data_loader = DataLoader()
        self.plotter = Plotter()
        
        # GUI variables
        self.x_var = tk.StringVar()
        self.y_var = tk.StringVar()
        self.z_var = tk.StringVar()
        self.colormap_var = tk.StringVar(value='plasma')
        
        # Coordinate display variables
        self.coord_var = tk.StringVar(value="Ready")
        self.current_axes = None
        
        # Setup GUI
        self.setup_gui()
        
    def setup_gui(self):
        """Setup GUI layout"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File selection
        file_frame = ttk.Frame(control_frame)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            file_frame, 
            text="Load CSV File", 
            command=self.load_file
        ).pack(side=tk.LEFT)
        
        self.file_label = ttk.Label(file_frame, text="No file loaded")
        self.file_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Axis selection
        axis_frame = ttk.Frame(control_frame)
        axis_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(axis_frame, text="X:").grid(row=0, column=0, padx=(0, 5))
        self.x_combo = ttk.Combobox(axis_frame, textvariable=self.x_var, width=15)
        self.x_combo.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(axis_frame, text="Y:").grid(row=0, column=2, padx=(0, 5))
        self.y_combo = ttk.Combobox(axis_frame, textvariable=self.y_var, width=15)
        self.y_combo.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(axis_frame, text="Color:").grid(row=0, column=4, padx=(0, 5))
        self.z_combo = ttk.Combobox(axis_frame, textvariable=self.z_var, width=15)
        self.z_combo.grid(row=0, column=5, padx=(0, 10))
        
        # Colormap selection
        ttk.Label(axis_frame, text="Colormap:").grid(row=0, column=6, padx=(0, 5))
        colormap_combo = ttk.Combobox(
            axis_frame, 
            textvariable=self.colormap_var, 
            values=self.plotter.get_available_colormaps(),
            width=10,
            state="readonly"
        )
        colormap_combo.grid(row=0, column=7, padx=(0, 10))
        
        # Plot button
        ttk.Button(
            axis_frame, 
            text="Create Plot", 
            command=self.create_plot
        ).grid(row=0, column=8)
        
        # Plot area
        plot_frame = ttk.LabelFrame(main_frame, text="Plot", padding=5)
        plot_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add navigation toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        toolbar.update()
        
        # Add status bar for coordinate display
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(status_frame, text="Coordinates:").pack(side=tk.LEFT, padx=(5, 0))
        coord_label = ttk.Label(status_frame, textvariable=self.coord_var, relief=tk.SUNKEN)
        coord_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
    def load_file(self):
        """Load CSV file"""
        filename = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Load data using auto-detection
                self.data_loader.load_auto(filename)
                
                # Get file info
                info = self.data_loader.get_info()
                format_type = info.get('format_type', 'unknown')
                
                # Update file label with format info
                self.file_label.config(text=f"Loaded: {filename} ({format_type})")
                
                # Update column combo boxes
                columns = self.data_loader.get_columns()
                self.x_combo['values'] = columns
                self.y_combo['values'] = columns
                self.z_combo['values'] = columns
                
                # Set default selections if enough columns
                if len(columns) >= 3:
                    self.x_var.set(columns[0])
                    self.y_var.set(columns[1])
                    self.z_var.set(columns[2])
                
                messagebox.showinfo(
                    "Success", 
                    f"Loaded {len(self.data_loader.get_data())} rows\n"
                    f"Format: {format_type}\n"
                    f"Columns: {len(columns)}"
                )
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
    
    def create_plot(self):
        """Create heatmap plot"""
        if self.data_loader.get_data() is None:
            messagebox.showwarning("Warning", "Please load a CSV file first")
            return
        
        x_col = self.x_var.get()
        y_col = self.y_var.get()
        z_col = self.z_var.get()
        
        if not all([x_col, y_col, z_col]):
            messagebox.showwarning("Warning", "Please select X, Y, and Color columns")
            return
        
        try:
            # Clear previous plot
            self.figure.clear()
            
            # Create new plot using plotter
            self.plotter.clear()
            plot_fig = self.plotter.create_2d_heatmap(
                self.data_loader.get_data(),
                x_col, y_col, z_col,
                self.colormap_var.get()
            )
            
            # Copy plot to GUI figure
            ax = self.figure.add_subplot(111)
            
            # Get the plot data from plotter
            data = self.data_loader.get_data()
            pivot_data = data.pivot_table(
                index=y_col, 
                columns=x_col, 
                values=z_col, 
                fill_value=None
            )
            
            im = ax.imshow(
                pivot_data.values,
                aspect='auto',
                origin='lower',
                extent=[
                    pivot_data.columns.min(), pivot_data.columns.max(),
                    pivot_data.index.min(), pivot_data.index.max()
                ],
                cmap=self.colormap_var.get()
            )
            
            # Add colorbar
            cbar = self.figure.colorbar(im, ax=ax)
            cbar.set_label(z_col)
            
            # Set labels and title
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f'2D Heatmap: {z_col}')
            ax.grid(True, alpha=0.3)
            
            # Refresh canvas
            self.canvas.draw()
            
            # Store current axes for coordinate tracking
            self.current_axes = ax
            
            # Connect mouse motion event for coordinate display
            self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create plot:\n{str(e)}")
    
    def on_mouse_move(self, event):
        """Handle mouse movement for coordinate display"""
        if event.inaxes == self.current_axes and event.xdata is not None and event.ydata is not None:
            # Get current column names for proper labeling
            x_col = self.x_var.get()
            y_col = self.y_var.get()
            z_col = self.z_var.get()
            
            # Format coordinates
            coord_text = f"{x_col}={event.xdata:.3f}, {y_col}={event.ydata:.3f}"
            
            # Try to get the interpolated value at the cursor position
            try:
                data = self.data_loader.get_data()
                if data is not None:
                    # Find nearest data point for value display
                    x_data = data[x_col].values
                    y_data = data[y_col].values
                    z_data = data[z_col].values
                    
                    # Find closest point
                    distances = ((x_data - event.xdata)**2 + (y_data - event.ydata)**2)
                    closest_idx = distances.argmin()
                    closest_z = z_data[closest_idx]
                    
                    coord_text += f", {z_col}≈{closest_z:.3e}"
            except:
                pass  # If value lookup fails, just show coordinates
            
            self.coord_var.set(coord_text)
        else:
            # Mouse is outside the plot area
            self.coord_var.set("Ready")


def run_gui():
    """Run the GUI application"""
    root = tk.Tk()
    app = ColorMapApp(root)
    root.mainloop()