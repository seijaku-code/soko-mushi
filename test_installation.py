#!/usr/bin/env python3
"""
Test script to verify Soko-Mushi installation and basic functionality.
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        print("✅ PyQt6 imported successfully")
    except ImportError as e:
        print(f"❌ PyQt6 import failed: {e}")
        return False
    
    try:
        import psutil
        print("✅ psutil imported successfully")
    except ImportError as e:
        print(f"❌ psutil import failed: {e}")
        return False
    
    try:
        from soko_mushi.core import DiskAnalyzer, FileInfo
        print("✅ Core modules imported successfully")
    except ImportError as e:
        print(f"❌ Core modules import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic disk analysis functionality."""
    print("\nTesting basic functionality...")
    
    try:
        from soko_mushi.core import DiskAnalyzer
        
        analyzer = DiskAnalyzer()
        drives = analyzer.get_available_drives()
        print(f"✅ Available drives detected: {drives}")
        
        # Test format_size function
        size_tests = [0, 1024, 1024*1024, 1024*1024*1024]
        for size in size_tests:
            formatted = analyzer.format_size(size)
            print(f"✅ Size formatting: {size} bytes = {formatted}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_gui_components():
    """Test GUI components without actually showing windows."""
    print("\nTesting GUI components...")
    
    try:
        from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton
        from PyQt6.QtCore import Qt
        import sys
        
        # Create application instance
        app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        
        # Test basic widgets
        widget = QWidget()
        label = QLabel("Test")
        button = QPushButton("Test")
        
        print("✅ GUI components created successfully")
        
        # Don't call app.exec() - just test creation
        return True
        
    except Exception as e:
        print(f"❌ GUI components test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Soko-Mushi Installation Test")
    print("=" * 40)
    
    all_passed = True
    
    # Test imports
    all_passed &= test_imports()
    
    # Test basic functionality
    all_passed &= test_basic_functionality()
    
    # Test GUI components
    all_passed &= test_gui_components()
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✅ All tests passed! Soko-Mushi is ready to run.")
        print("\nTo start the application:")
        print("python src/soko_mushi/main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
