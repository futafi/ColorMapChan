# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

カラープロットちゃん is a 2D/3D heatmap visualization application for scientific measurement data. It's a personal, non-public project prioritizing simplicity and functionality over complex architecture.

## Development Commands

### Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
# GUI mode (production)
python main.py

# CLI mode (for testing)
python main.py --cli --file test_data/test_plain_csv.csv
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_data_loader.py

# Run with coverage
pytest --cov=core
```

### Code Quality
```bash
# Linting
flake8 .
pylint core/ gui/ cli/

# Format check
black --check .
```

### Building
```bash
# Build executable with PyInstaller
pyinstaller --onefile --windowed --icon=icon.ico main.py
```

## Architecture

### Core Design Philosophy
- **Simplicity over complexity**: Personal project prioritizing working code over perfect architecture
- **Testability**: Core logic separated from GUI to enable pytest testing
- **GUI/CLI separation**: Same core logic used by both tkinter GUI and CLI interface

### Module Structure
```
core/           # Data processing logic (testable)
├── data_loader.py    # CSV file reading (3 formats)
├── data_processor.py # Filtering, transformations
└── plotter.py        # matplotlib graph generation

gui/            # tkinter GUI (Windows exe target)
└── app.py      # Main GUI application

cli/            # CLI interface (testing only)
└── interface.py # Command-line interface

tests/          # pytest test suite
└── test_*.py   # Test files for core modules
```

### Data Format Support
The application supports 3 CSV formats from B1500A semiconductor parameter analyzer:
1. **PlainCSV**: Standard CSV with header row
2. **ParameterCSV**: B1500A text2csv format with metadata
3. **AnalysisCSV**: B1500A single file CSV with AutoAnalysis

Auto-detection tries formats in order: ParameterCSV → AnalysisCSV → PlainCSV

### Key Features to Implement
- 2D/3D heatmap visualization with matplotlib
- Interactive operations (zoom, pan, cross-section plots)
- Advanced filtering (value filters, range filters)
- Multiple colormap support (plasma, viridis, jet, hot, cool, gray)
- Data export (PNG images, filtered CSV)
- Simple data transformations (abs, diff_n)

### Testing Strategy
- Core modules (data_loader, data_processor, plotter) are fully testable
- GUI components are not tested (tkinter complexity not worth it for personal project)
- Use test_data/ directory with 3 sample files for each format
- CLI interface enables non-GUI testing of full workflows

### Deployment
- Target: Windows executable via PyInstaller
- GitHub Actions automates testing and building
- Single-file executable for easy distribution
- Users only interact with GUI (exe double-click)

## Project Documentation

### Important Reference Files
These files in the `notes/` directory contain critical project information:

- **`notes/SPEC.md`**: Complete feature specification and requirements
  - 2D/3D heatmap visualization requirements
  - Interactive operations (zoom, pan, cross-section plots)
  - Filtering capabilities and display options
  - Export functionality specifications
  
- **`notes/FILEFORMAT.md`**: Data format specifications
  - PlainCSV, ParameterCSV, AnalysisCSV format details
  - B1500A semiconductor analyzer data formats
  - Auto-detection algorithms and parsing requirements
  
- **`notes/IMPLEMENTATION_PHASES.md`**: Detailed development roadmap
  - 7-phase implementation plan with specific tasks
  - Phase 1 focuses on minimal working version + CI/CD
  - Each phase has clear deliverables and success criteria
  
- **`notes/DEVELOPMENT_RULES.md`**: Development guidelines and git workflow
  - Semantic versioning and commit message format
  - v2 branch strategy for rebuild project
  - Quality requirements and CI/CD rules

**IMPORTANT**: Always refer to these files when:
- Implementing new features (check SPEC.md)
- Working with data formats (check FILEFORMAT.md)
- Planning next steps (check IMPLEMENTATION_PHASES.md)
- Making commits or releases (check DEVELOPMENT_RULES.md)

## Implementation Notes

### Keep It Simple
- Use tkinter's native appearance (no custom styling)
- Minimal dependencies (numpy, pandas, matplotlib, pytest)
- Avoid over-engineering for this personal project
- Focus on working functionality over perfect code

### Test Data
Located in test_data/ directory:
- test_plain_csv.csv: Standard CSV format
- test_parameter_csv.csv: B1500A text2csv format  
- test_analysis_csv.csv: B1500A single file format

All contain MOSFET characteristics data with VG1, VG2 voltage sweeps and current measurements.

## Project Management
- プロジェクトはgitで管理されている．
- バージョンはSemantic versionで管理する．
- 細かい単位でのコミットを行なう様に．