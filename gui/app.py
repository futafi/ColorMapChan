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
        
        # Cross-section variables
        self.cross_section_mode = tk.BooleanVar(value=False)
        self.cross_section_x = None
        self.cross_section_y = None
        self.cross_section_window = None
        
        # Scale variables
        self.x_scale_var = tk.StringVar(value='linear')
        self.y_scale_var = tk.StringVar(value='linear')
        self.z_scale_var = tk.StringVar(value='linear')
        self.scientific_notation_var = tk.BooleanVar(value=False)
        
        # Range setting variables
        self.x_min_var = tk.StringVar()
        self.x_max_var = tk.StringVar()
        self.y_min_var = tk.StringVar()
        self.y_max_var = tk.StringVar()
        self.z_min_var = tk.StringVar()
        self.z_max_var = tk.StringVar()
        self.auto_range_var = tk.BooleanVar(value=True)
        
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
        
        # Cross-section mode toggle
        cross_section_check = ttk.Checkbutton(
            axis_frame,
            text="Cross-section Mode",
            variable=self.cross_section_mode
        )
        cross_section_check.grid(row=0, column=9, padx=(10, 0))
        
        # Scale options frame
        scale_frame = ttk.Frame(control_frame)
        scale_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Scale selection
        ttk.Label(scale_frame, text="X Scale:").grid(row=0, column=0, padx=(0, 5))
        x_scale_combo = ttk.Combobox(
            scale_frame, 
            textvariable=self.x_scale_var,
            values=['linear', 'log'],
            width=8,
            state="readonly"
        )
        x_scale_combo.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(scale_frame, text="Y Scale:").grid(row=0, column=2, padx=(0, 5))
        y_scale_combo = ttk.Combobox(
            scale_frame, 
            textvariable=self.y_scale_var,
            values=['linear', 'log'],
            width=8,
            state="readonly"
        )
        y_scale_combo.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(scale_frame, text="Color Scale:").grid(row=0, column=4, padx=(0, 5))
        z_scale_combo = ttk.Combobox(
            scale_frame, 
            textvariable=self.z_scale_var,
            values=['linear', 'log'],
            width=8,
            state="readonly"
        )
        z_scale_combo.grid(row=0, column=5, padx=(0, 10))
        
        # Scientific notation toggle
        sci_notation_check = ttk.Checkbutton(
            scale_frame,
            text="Scientific Notation",
            variable=self.scientific_notation_var
        )
        sci_notation_check.grid(row=0, column=6, padx=(10, 0))
        
        # Apply scale button
        ttk.Button(
            scale_frame,
            text="Apply Scale",
            command=self.apply_scale_settings
        ).grid(row=0, column=7, padx=(10, 0))
        
        # Range setting controls
        range_frame = ttk.LabelFrame(control_frame, text="Range Settings", padding=10)
        range_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Auto range checkbox
        auto_check = ttk.Checkbutton(
            range_frame,
            text="Auto Range",
            variable=self.auto_range_var,
            command=self.on_auto_range_toggle
        )
        auto_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=(0, 20))
        
        # X Range
        ttk.Label(range_frame, text="X Range:").grid(row=0, column=2, padx=(0, 5))
        ttk.Label(range_frame, text="Min:").grid(row=0, column=3, padx=(5, 2))
        x_min_entry = ttk.Entry(range_frame, textvariable=self.x_min_var, width=8)
        x_min_entry.grid(row=0, column=4, padx=(0, 5))
        ttk.Label(range_frame, text="Max:").grid(row=0, column=5, padx=(5, 2))
        x_max_entry = ttk.Entry(range_frame, textvariable=self.x_max_var, width=8)
        x_max_entry.grid(row=0, column=6, padx=(0, 15))
        
        # Y Range
        ttk.Label(range_frame, text="Y Range:").grid(row=0, column=7, padx=(0, 5))
        ttk.Label(range_frame, text="Min:").grid(row=0, column=8, padx=(5, 2))
        y_min_entry = ttk.Entry(range_frame, textvariable=self.y_min_var, width=8)
        y_min_entry.grid(row=0, column=9, padx=(0, 5))
        ttk.Label(range_frame, text="Max:").grid(row=0, column=10, padx=(5, 2))
        y_max_entry = ttk.Entry(range_frame, textvariable=self.y_max_var, width=8)
        y_max_entry.grid(row=0, column=11, padx=(0, 15))
        
        # Color Range
        ttk.Label(range_frame, text="Color Range:").grid(row=1, column=2, padx=(0, 5), pady=(5, 0))
        ttk.Label(range_frame, text="Min:").grid(row=1, column=3, padx=(5, 2), pady=(5, 0))
        z_min_entry = ttk.Entry(range_frame, textvariable=self.z_min_var, width=8)
        z_min_entry.grid(row=1, column=4, padx=(0, 5), pady=(5, 0))
        ttk.Label(range_frame, text="Max:").grid(row=1, column=5, padx=(5, 2), pady=(5, 0))
        z_max_entry = ttk.Entry(range_frame, textvariable=self.z_max_var, width=8)
        z_max_entry.grid(row=1, column=6, padx=(0, 15), pady=(5, 0))
        
        # Apply Range button
        ttk.Button(
            range_frame,
            text="Apply Range",
            command=self.apply_manual_range
        ).grid(row=1, column=7, columnspan=2, padx=(10, 0), pady=(5, 0))
        
        # Store entry widgets for enabling/disabling
        self.range_entries = [x_min_entry, x_max_entry, y_min_entry, y_max_entry, z_min_entry, z_max_entry]
        
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
        
        # Initialize range entries state (disabled by default since auto range is on)
        self.on_auto_range_toggle()
        
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
                    
                    # Set initial range values based on data
                    self.update_range_suggestions()
                
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
            self.plotter.create_2d_heatmap(
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
            # Store colorbar reference for scale formatting
            self.figure._colorbar = cbar
            
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
            
            # Connect mouse click event for cross-section mode
            self.canvas.mpl_connect('button_press_event', self.on_mouse_click)
            
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
            except Exception:
                pass  # If value lookup fails, just show coordinates
            
            self.coord_var.set(coord_text)
        else:
            # Mouse is outside the plot area
            self.coord_var.set("Ready")
    
    def on_mouse_click(self, event):
        """Handle mouse click for cross-section mode"""
        if not self.cross_section_mode.get():
            return
        
        if event.inaxes == self.current_axes and event.xdata is not None and event.ydata is not None:
            # Store click position
            self.cross_section_x = event.xdata
            self.cross_section_y = event.ydata
            
            # Update coordinate display
            x_col = self.x_var.get()
            y_col = self.y_var.get()
            coord_text = f"Cross-section at {x_col}={event.xdata:.3f}, {y_col}={event.ydata:.3f}"
            self.coord_var.set(coord_text)
            
            # Show cross-section plots
            self.show_cross_sections()
    
    def show_cross_sections(self):
        """Display cross-section plots in a separate window"""
        if self.cross_section_x is None or self.cross_section_y is None:
            return
        
        # Close existing cross-section window if open
        if self.cross_section_window is not None:
            try:
                self.cross_section_window.destroy()
            except:
                pass
        
        # Create new window for cross-sections
        self.cross_section_window = tk.Toplevel(self.root)
        self.cross_section_window.title("Cross-Section Plots")
        self.cross_section_window.geometry("800x600")
        
        # Create matplotlib figure for cross-sections
        from matplotlib.figure import Figure
        cs_figure = Figure(figsize=(10, 8))
        cs_canvas = FigureCanvasTkAgg(cs_figure, self.cross_section_window)
        cs_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add navigation toolbar
        cs_toolbar = NavigationToolbar2Tk(cs_canvas, self.cross_section_window)
        cs_toolbar.update()
        
        try:
            # Get data and column names
            data = self.data_loader.get_data()
            x_col = self.x_var.get()
            y_col = self.y_var.get()
            z_col = self.z_var.get()
            
            # Create pivot table for easier slicing
            pivot_data = data.pivot_table(
                index=y_col, 
                columns=x_col, 
                values=z_col, 
                fill_value=None
            )
            
            # Create two subplots (X and Y cross-sections)
            ax1 = cs_figure.add_subplot(2, 1, 1)
            ax2 = cs_figure.add_subplot(2, 1, 2)
            
            # X cross-section (constant Y, varying X)
            y_closest_idx = (pivot_data.index - self.cross_section_y).abs().idxmin()
            x_cross_data = pivot_data.loc[y_closest_idx].dropna()
            
            ax1.plot(x_cross_data.index, x_cross_data.values, 'b-', linewidth=2, marker='o', markersize=4)
            ax1.axvline(x=self.cross_section_x, color='red', linestyle='--', alpha=0.7, label=f'{x_col}={self.cross_section_x:.3f}')
            ax1.set_xlabel(x_col)
            ax1.set_ylabel(z_col)
            ax1.set_title(f'X Cross-section at {y_col}={y_closest_idx:.3f}')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Y cross-section (constant X, varying Y)
            x_closest_idx = (pivot_data.columns - self.cross_section_x).abs().idxmin()
            y_cross_data = pivot_data[x_closest_idx].dropna()
            
            ax2.plot(y_cross_data.index, y_cross_data.values, 'g-', linewidth=2, marker='s', markersize=4)
            ax2.axvline(x=self.cross_section_y, color='red', linestyle='--', alpha=0.7, label=f'{y_col}={self.cross_section_y:.3f}')
            ax2.set_xlabel(y_col)
            ax2.set_ylabel(z_col)
            ax2.set_title(f'Y Cross-section at {x_col}={x_closest_idx:.3f}')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
            
            # Adjust layout
            cs_figure.tight_layout()
            cs_canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create cross-sections:\n{str(e)}")
            if self.cross_section_window:
                self.cross_section_window.destroy()
                self.cross_section_window = None
    
    def apply_scale_settings(self):
        """Apply scale settings to the current plot"""
        if self.current_axes is None:
            messagebox.showwarning("Warning", "Please create a plot first")
            return
        
        try:
            # Apply X scale
            if self.x_scale_var.get() == 'log':
                self.current_axes.set_xscale('log')
            else:
                self.current_axes.set_xscale('linear')
            
            # Apply Y scale
            if self.y_scale_var.get() == 'log':
                self.current_axes.set_yscale('log')
            else:
                self.current_axes.set_yscale('linear')
            
            # Apply color scale (for colorbar)
            images = self.current_axes.get_images()
            if images and self.z_scale_var.get() == 'log':
                # For log color scale, we need to handle data transformation
                data = self.data_loader.get_data()
                z_col = self.z_var.get()
                
                if data is not None and z_col:
                    z_data = data[z_col].values
                    # Check if data is suitable for log scale (positive values)
                    if np.all(z_data > 0):
                        images[0].set_norm(plt.colors.LogNorm())
                    else:
                        messagebox.showwarning(
                            "Warning",
                            f"Cannot apply log scale to {z_col}: "
                            f"contains non-positive values"
                        )
            elif images:
                images[0].set_norm(plt.colors.Normalize())
            
            # Apply scientific notation formatting
            if self.scientific_notation_var.get():
                from matplotlib.ticker import ScalarFormatter
                
                # X axis
                x_formatter = ScalarFormatter(useMathText=True)
                x_formatter.set_scientific(True)
                x_formatter.set_powerlimits((-2, 2))
                self.current_axes.xaxis.set_major_formatter(x_formatter)
                
                # Y axis
                y_formatter = ScalarFormatter(useMathText=True)
                y_formatter.set_scientific(True)
                y_formatter.set_powerlimits((-2, 2))
                self.current_axes.yaxis.set_major_formatter(y_formatter)
                
                # Colorbar
                if hasattr(self.figure, '_colorbar') and self.figure._colorbar:
                    cbar_formatter = ScalarFormatter(useMathText=True)
                    cbar_formatter.set_scientific(True)
                    cbar_formatter.set_powerlimits((-2, 2))
                    self.figure._colorbar.ax.yaxis.set_major_formatter(cbar_formatter)
            else:
                # Reset to default formatting
                self.current_axes.xaxis.set_major_formatter(plt.ScalarFormatter())
                self.current_axes.yaxis.set_major_formatter(plt.ScalarFormatter())
                
                if hasattr(self.figure, '_colorbar') and self.figure._colorbar:
                    self.figure._colorbar.ax.yaxis.set_major_formatter(plt.ScalarFormatter())
            
            # Refresh the plot
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to apply scale settings:\n{str(e)}"
            )
    
    def on_auto_range_toggle(self):
        """Handle auto range checkbox toggle"""
        is_auto = self.auto_range_var.get()
        
        # Enable/disable range entry widgets
        state = 'disabled' if is_auto else 'normal'
        for entry in self.range_entries:
            entry.config(state=state)
        
        # If switching to auto, clear manual values and replot
        if is_auto:
            self.x_min_var.set("")
            self.x_max_var.set("")
            self.y_min_var.set("")
            self.y_max_var.set("")
            self.z_min_var.set("")
            self.z_max_var.set("")
            
            # Replot with auto range if plot exists
            if self.current_axes is not None:
                self.create_plot()
    
    def apply_manual_range(self):
        """Apply manual range settings to the current plot"""
        if self.current_axes is None:
            messagebox.showwarning("Warning", "Please create a plot first")
            return
        
        if self.auto_range_var.get():
            messagebox.showinfo("Info", "Auto Range is enabled. Disable it to set manual ranges.")
            return
        
        try:
            # Get current axis limits as defaults
            current_xlim = self.current_axes.get_xlim()
            current_ylim = self.current_axes.get_ylim()
            
            # Parse range values, use current limits as fallback
            x_min = float(self.x_min_var.get()) if self.x_min_var.get() else current_xlim[0]
            x_max = float(self.x_max_var.get()) if self.x_max_var.get() else current_xlim[1]
            y_min = float(self.y_min_var.get()) if self.y_min_var.get() else current_ylim[0]
            y_max = float(self.y_max_var.get()) if self.y_max_var.get() else current_ylim[1]
            
            # Validate ranges
            if x_min >= x_max:
                messagebox.showerror("Error", "X minimum must be less than X maximum")
                return
            if y_min >= y_max:
                messagebox.showerror("Error", "Y minimum must be less than Y maximum")
                return
            
            # Apply X and Y ranges
            self.current_axes.set_xlim(x_min, x_max)
            self.current_axes.set_ylim(y_min, y_max)
            
            # Handle color range if specified
            z_min_str = self.z_min_var.get()
            z_max_str = self.z_max_var.get()
            
            if z_min_str or z_max_str:
                # Get current colorbar limits
                images = self.current_axes.get_images()
                if images:
                    current_clim = images[0].get_clim()
                    z_min = float(z_min_str) if z_min_str else current_clim[0]
                    z_max = float(z_max_str) if z_max_str else current_clim[1]
                    
                    if z_min >= z_max:
                        messagebox.showerror("Error", "Color minimum must be less than Color maximum")
                        return
                    
                    images[0].set_clim(z_min, z_max)
            
            # Refresh the plot
            self.canvas.draw()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid range values. Please enter numeric values.\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply range settings:\n{str(e)}")
    
    def update_range_suggestions(self):
        """Update range entry placeholders with data-based suggestions"""
        if self.data_loader.get_data() is None:
            return
        
        try:
            data = self.data_loader.get_data()
            x_col = self.x_var.get()
            y_col = self.y_var.get()
            z_col = self.z_var.get()
            
            if all([x_col, y_col, z_col]) and all(col in data.columns for col in [x_col, y_col, z_col]):
                # Calculate data ranges
                x_min, x_max = data[x_col].min(), data[x_col].max()
                y_min, y_max = data[y_col].min(), data[y_col].max()
                z_min, z_max = data[z_col].min(), data[z_col].max()
                
                # Set placeholder values (not actual values, just for reference)
                # Only update if auto range is enabled and fields are empty
                if self.auto_range_var.get():
                    self.x_min_var.set(f"{x_min:.3g}")
                    self.x_max_var.set(f"{x_max:.3g}")
                    self.y_min_var.set(f"{y_min:.3g}")
                    self.y_max_var.set(f"{y_max:.3g}")
                    self.z_min_var.set(f"{z_min:.3g}")
                    self.z_max_var.set(f"{z_max:.3g}")
        except Exception:
            pass  # Silently fail if range calculation fails


def run_gui():
    """Run the GUI application"""
    root = tk.Tk()
    ColorMapApp(root)
    root.mainloop()