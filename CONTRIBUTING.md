# Contributing to Soko-Mushi

Thank you for your interest in contributing to Soko-Mushi! This document provides guidelines for contributing to the project.

## Support the Project

If you find Soko-Mushi useful and want to support its development, consider buying me a coffee! Your support helps keep the project active and enables new features.

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support%20development-yellow.svg?style=flat-square&logo=buy-me-a-coffee)](https://coff.ee/seijaku)

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/soko-mushi.git
   cd soko-mushi
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .[dev]
   ```

## Code Standards

### Python Style
- Follow PEP 8 conventions
- Use type hints for all function parameters and return values
- Document all public methods and classes with docstrings
- Use descriptive variable and function names

### Code Formatting
Before submitting a PR, run:
```bash
# Format code
python -m black src/

# Type checking
python -m mypy src/

# Run tests
python -m pytest tests/
```

### Git Workflow
1. Create a feature branch from `main`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Project Structure

```
soko-mushi/
├── src/soko_mushi/          # Main application code
│   ├── core/                # Core analysis logic
│   └── gui/                 # GUI components
├── tests/                   # Unit tests
├── build.py                 # Build script for executables
├── requirements.txt         # Python dependencies
└── README.md               # Project documentation
```

## Architecture Guidelines

### Core Module (`src/soko_mushi/core/`)
- **analyzer.py** - Main disk scanning logic
- **exporter.py** - Report export functionality
- Keep platform-specific code isolated
- Use threading for long-running operations
- Handle file system errors gracefully

### GUI Module (`src/soko_mushi/gui/`)
- **main_window.py** - Main application window
- **tree_view.py** - File hierarchy display
- **stats_panel.py** - Statistics and charts
- **toolbar.py** - Application toolbar
- Use CustomTkinter for modern UI components
- Keep GUI components modular and reusable
- Follow MVC pattern (Model=core, View=gui, Controller=main_window)

## Adding New Features

### Before Starting
1. Check existing issues and PRs
2. Create an issue to discuss the feature
3. Get feedback from maintainers

### Implementation Guidelines
1. **Start with tests** - Write tests for new functionality first
2. **Keep it simple** - Follow the KISS principle
3. **Cross-platform** - Ensure code works on Windows, macOS, and Linux
4. **Performance** - Consider impact on large directory scans
5. **User experience** - Provide progress feedback for long operations

### Common Feature Types

#### New Export Formats
1. Add export method to `ReportExporter` class
2. Update export dialog in `main_window.py`
3. Add tests for the new format
4. Update documentation

#### GUI Enhancements
1. Create new component in `gui/` directory
2. Import and use in `main_window.py`
3. Follow existing patterns for themes and styling
4. Test with different themes (Light/Dark/System)

#### Core Analysis Features
1. Add functionality to `DiskAnalyzer` class
2. Update `FileInfo` if needed for new data
3. Add corresponding GUI display
4. Ensure thread safety for background operations

## Testing

### Unit Tests
- Write tests for all new functionality
- Use pytest framework
- Mock file system operations when appropriate
- Test error conditions and edge cases

### Manual Testing
- Test on different operating systems
- Test with various folder structures
- Test with large directories (performance)
- Test all export formats
- Test theme switching

## Pull Request Process

1. **Update documentation** - Update README.md if needed
2. **Add tests** - Ensure adequate test coverage
3. **Check code quality** - Run black, mypy, and tests
4. **Small PRs** - Keep pull requests focused and small
5. **Clear description** - Explain what and why

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] Cross-platform testing done

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests pass
- [ ] Documentation updated
```

## Reporting Issues

### Bug Reports
Include:
- Operating system and version
- Python version
- Steps to reproduce
- Expected vs actual behavior
- Error messages (if any)
- Screenshots (if relevant)

### Feature Requests
Include:
- Clear description of the feature
- Use case or problem it solves
- Proposed implementation (if you have ideas)
- Willingness to contribute the implementation

## Questions?

- Open an issue for questions about contributing
- Check existing documentation first
- Be respectful and constructive in all interactions

## Support the Project ☕

Your contributions make Soko-Mushi better! If you'd like to support the project financially, you can:

[![Buy Me A Coffee](https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png)](https://coff.ee/seijaku)

Every coffee helps fuel development and keeps the project growing. Thank you for your support!

---

Thank you for contributing to Soko-Mushi! 🐛📊
