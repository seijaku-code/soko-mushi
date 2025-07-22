<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Soko-Mushi Project Instructions

This is a Python-based disk analysis tool called Soko-Mushi (Free Edition) that provides TreeSize-style functionality for local disk analysis.

## Project Structure
- `src/soko_mushi/` - Main application code
- `src/soko_mushi/core/` - Core analysis functionality
- `src/soko_mushi/gui/` - GUI components using CustomTkinter
- `build.py` - Nuitka compilation script

## Key Technologies
- **Python 3.8+** - Main programming language
- **PyQt6** - Modern GUI framework
- **psutil** - System information and disk access
- **pandas** - Data processing for exports
- **Nuitka** - Python-to-executable compilation

## Architecture Guidelines
- Use type hints throughout the codebase
- Follow the MVC pattern (Model=core, View=gui, Controller=main_window)
- Keep GUI components modular and reusable
- Handle errors gracefully, especially file system operations
- Use threading for long-running operations (disk scanning)

## Code Style
- Follow PEP 8 conventions
- Use Black for code formatting
- Use MyPy for type checking
- Document all public methods and classes
- Use descriptive variable and function names

## Features to Maintain
- Cross-platform compatibility (Windows, macOS, Linux)
- Modern GUI with dark/light theme support
- Efficient disk scanning with progress updates
- Multiple export formats (JSON, CSV)
- Tree view with hierarchical folder display
- Statistics panel with file type breakdown

## Performance Considerations
- Use threading for disk I/O operations
- Implement scan cancellation functionality
- Optimize memory usage for large directory trees
- Provide progress feedback for long operations

## Build & Distribution
- Use Nuitka for creating standalone executables
- Support one-file distribution for easy deployment
- Include proper metadata (version, description, etc.)
- Handle platform-specific requirements

When implementing new features or fixing bugs, prioritize:
1. User experience and responsiveness
2. Cross-platform compatibility
3. Error handling and edge cases
4. Performance optimization
5. Code maintainability
