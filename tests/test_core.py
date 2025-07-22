"""
Unit tests for Soko-Mushi core functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path

from soko_mushi.core import DiskAnalyzer, FileInfo, ReportExporter


class TestDiskAnalyzer:
    """Test cases for DiskAnalyzer class."""
    
    def test_format_size(self):
        """Test file size formatting."""
        assert DiskAnalyzer.format_size(0) == "0 B"
        assert DiskAnalyzer.format_size(1024) == "1.0 KB"
        assert DiskAnalyzer.format_size(1024 * 1024) == "1.0 MB"
        assert DiskAnalyzer.format_size(1024 * 1024 * 1024) == "1.0 GB"
        assert DiskAnalyzer.format_size(512) == "512 B"
        
    def test_get_available_drives(self):
        """Test drive detection."""
        drives = DiskAnalyzer.get_available_drives()
        assert isinstance(drives, list)
        assert len(drives) > 0
        
    def test_file_info_creation(self):
        """Test FileInfo dataclass."""
        file_info = FileInfo(
            path=Path("/test/path"),
            name="test.txt",
            size=1024,
            is_directory=False,
            extension=".txt",
            modified_time=1234567890.0
        )
        
        assert file_info.name == "test.txt"
        assert file_info.size == 1024
        assert not file_info.is_directory
        assert file_info.extension == ".txt"
        assert len(file_info.children) == 0


class TestReportExporter:
    """Test cases for ReportExporter class."""
    
    def create_test_file_info(self):
        """Create test file info structure."""
        root = FileInfo(
            path=Path("/test"),
            name="test",
            size=2048,
            is_directory=True,
            extension="",
            modified_time=1234567890.0
        )
        
        file1 = FileInfo(
            path=Path("/test/file1.txt"),
            name="file1.txt",
            size=1024,
            is_directory=False,
            extension=".txt",
            modified_time=1234567890.0
        )
        
        file2 = FileInfo(
            path=Path("/test/file2.py"),
            name="file2.py",
            size=1024,
            is_directory=False,
            extension=".py",
            modified_time=1234567890.0
        )
        
        root.children = [file1, file2]
        return root
        
    def test_export_to_json(self):
        """Test JSON export functionality."""
        root_info = self.create_test_file_info()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
            
        try:
            ReportExporter.export_to_json(root_info, temp_path)
            assert os.path.exists(temp_path)
            
            # Verify file has content
            with open(temp_path, 'r') as f:
                content = f.read()
                assert len(content) > 0
                assert "scan_timestamp" in content
                assert "file_tree" in content
                
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    def test_export_to_csv(self):
        """Test CSV export functionality."""
        root_info = self.create_test_file_info()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
            
        try:
            ReportExporter.export_to_csv(root_info, temp_path)
            assert os.path.exists(temp_path)
            
            # Verify file has content
            with open(temp_path, 'r') as f:
                lines = f.readlines()
                assert len(lines) > 1  # Header + at least one data row
                assert "path" in lines[0]  # Header should contain 'path'
                
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
