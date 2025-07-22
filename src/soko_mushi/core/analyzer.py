"""
Core disk analysis functionality for Soko-Mushi.
"""

import os
import threading
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Any
import time
import psutil


@dataclass
class FileInfo:
    """Information about a file or directory."""
    path: Path
    name: str
    size: int
    is_directory: bool
    extension: str
    modified_time: float
    children: Optional[List['FileInfo']] = None
    
    def __post_init__(self) -> None:
        if self.children is None:
            self.children = []


class DiskAnalyzer:
    """Main disk analysis engine."""
    
    def __init__(self) -> None:
        self.is_scanning = False
        self.scan_thread: Optional[threading.Thread] = None
        self.progress_callback: Optional[Callable[[int, str], None]] = None
        self.completion_callback: Optional[Callable[[FileInfo], None]] = None
        self.error_callback: Optional[Callable[[str], None]] = None
        
    def start_scan(
        self, 
        root_path: str, 
        progress_callback: Optional[Callable[[int, str], None]] = None,
        completion_callback: Optional[Callable[[FileInfo], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None
    ) -> None:
        """Start scanning a directory in a separate thread."""
        if self.is_scanning:
            return
            
        self.progress_callback = progress_callback
        self.completion_callback = completion_callback
        self.error_callback = error_callback
        
        self.scan_thread = threading.Thread(
            target=self._scan_directory_threaded,
            args=(root_path,),
            daemon=True
        )
        self.is_scanning = True
        self.scan_thread.start()
        
    def stop_scan(self) -> None:
        """Stop the current scan."""
        self.is_scanning = False
        if self.scan_thread:
            self.scan_thread.join(timeout=1.0)
            
    def _scan_directory_threaded(self, root_path: str) -> None:
        """Thread worker for directory scanning."""
        try:
            root_info = self._scan_directory(Path(root_path))
            if self.completion_callback and self.is_scanning:
                self.completion_callback(root_info)
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"Scan error: {str(e)}")
        finally:
            self.is_scanning = False
            
    def _scan_directory(self, path: Path, depth: int = 0) -> FileInfo:
        """Recursively scan a directory and return file information."""
        if not self.is_scanning:
            raise InterruptedError("Scan was stopped")
            
        try:
            stat_info = path.stat()
            name = path.name if path.name else str(path)
            
            if self.progress_callback:
                self.progress_callback(depth, str(path))
            
            file_info = FileInfo(
                path=path,
                name=name,
                size=0,
                is_directory=path.is_dir(),
                extension=path.suffix.lower() if path.suffix else "",
                modified_time=stat_info.st_mtime
            )
            
            if path.is_dir():
                total_size = 0
                try:
                    for child_path in path.iterdir():
                        if not self.is_scanning:
                            break
                            
                        try:
                            child_info = self._scan_directory(child_path, depth + 1)
                            file_info.children.append(child_info)
                            total_size += child_info.size
                        except (PermissionError, FileNotFoundError, OSError):
                            # Skip inaccessible files/directories
                            continue
                            
                    file_info.size = total_size
                    
                except (PermissionError, OSError):
                    # If we can't read the directory, treat it as a file
                    file_info.size = stat_info.st_size
                    
            else:
                file_info.size = stat_info.st_size
                
            return file_info
            
        except Exception as e:
            # Return a minimal file info for failed entries
            return FileInfo(
                path=path,
                name=path.name or str(path),
                size=0,
                is_directory=False,
                extension="",
                modified_time=0
            )
            
    @staticmethod
    def get_available_drives() -> List[str]:
        """Get list of available disk drives."""
        drives = []
        if os.name == 'nt':  # Windows
            for partition in psutil.disk_partitions():
                if 'cdrom' not in partition.opts:
                    drives.append(partition.mountpoint)
        else:  # Unix-like systems
            drives = ['/']
            # Add common mount points
            for mount_point in ['/home', '/mnt', '/media']:
                if os.path.exists(mount_point):
                    drives.append(mount_point)
                    
        return drives
        
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
            
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
            
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.1f} {units[unit_index]}"
            
    @staticmethod
    def get_file_type_stats(root_info: FileInfo) -> Dict[str, Dict[str, Any]]:
        """Get statistics about file types."""
        stats = {}
        
        def collect_stats(info: FileInfo) -> None:
            if not info.is_directory:
                ext = info.extension or "No extension"
                if ext not in stats:
                    stats[ext] = {"count": 0, "size": 0}
                stats[ext]["count"] += 1
                stats[ext]["size"] += info.size
            
            for child in info.children:
                collect_stats(child)
                
        collect_stats(root_info)
        
        # Sort by total size
        sorted_stats = dict(
            sorted(stats.items(), key=lambda x: x[1]["size"], reverse=True)
        )
        
        return sorted_stats
        
    @staticmethod
    def get_largest_items(root_info: FileInfo, count: int = 10) -> List[FileInfo]:
        """Get the largest files and directories."""
        all_items = []
        
        def collect_items(info: FileInfo) -> None:
            all_items.append(info)
            for child in info.children:
                collect_items(child)
                
        collect_items(root_info)
        
        # Sort by size and return top items
        return sorted(all_items, key=lambda x: x.size, reverse=True)[:count]
