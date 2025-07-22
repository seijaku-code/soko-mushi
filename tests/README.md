# Test directory for Soko-Mushi

This directory contains unit tests for the Soko-Mushi application.

## Running Tests

To run all tests:
```bash
python -m pytest tests/ -v
```

To run specific test files:
```bash
python -m pytest tests/test_core.py -v
```

## Test Structure

- `test_core.py` - Tests for core disk analysis functionality
- Additional test files can be added as the project grows

## Test Coverage

The tests cover:
- File size formatting
- Drive detection
- FileInfo data structure
- Export functionality (JSON/CSV)
- Basic error handling

To run tests with coverage:
```bash
pip install pytest-cov
python -m pytest tests/ --cov=soko_mushi --cov-report=html
```
