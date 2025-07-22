"""
Export functionality for Soko-Mushi reports.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from .analyzer import FileInfo, DiskAnalyzer


class ReportExporter:
    """Handle exporting scan results to various formats."""
    
    @staticmethod
    def export_to_json(root_info: FileInfo, output_path: str) -> None:
        """Export scan results to JSON format."""
        def file_info_to_dict(info: FileInfo) -> Dict[str, Any]:
            return {
                "path": str(info.path),
                "name": info.name,
                "size": info.size,
                "size_formatted": DiskAnalyzer.format_size(info.size),
                "is_directory": info.is_directory,
                "extension": info.extension,
                "modified_time": info.modified_time,
                "modified_time_formatted": datetime.fromtimestamp(info.modified_time).isoformat() if info.modified_time > 0 else "",
                "children": [file_info_to_dict(child) for child in info.children]
            }
        
        report_data = {
            "scan_timestamp": datetime.now().isoformat(),
            "root_path": str(root_info.path),
            "total_size": root_info.size,
            "total_size_formatted": DiskAnalyzer.format_size(root_info.size),
            "file_tree": file_info_to_dict(root_info),
            "file_type_stats": DiskAnalyzer.get_file_type_stats(root_info),
            "largest_items": [
                {
                    "path": str(item.path),
                    "name": item.name,
                    "size": item.size,
                    "size_formatted": DiskAnalyzer.format_size(item.size),
                    "is_directory": item.is_directory
                }
                for item in DiskAnalyzer.get_largest_items(root_info, 50)
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def export_to_csv(root_info: FileInfo, output_path: str) -> None:
        """Export scan results to CSV format."""
        all_items = []
        
        def collect_items(info: FileInfo, depth: int = 0) -> None:
            all_items.append({
                "path": str(info.path),
                "name": info.name,
                "size": info.size,
                "size_formatted": DiskAnalyzer.format_size(info.size),
                "is_directory": "Yes" if info.is_directory else "No",
                "extension": info.extension,
                "depth": depth,
                "modified_time": datetime.fromtimestamp(info.modified_time).isoformat() if info.modified_time > 0 else ""
            })
            
            for child in info.children:
                collect_items(child, depth + 1)
        
        collect_items(root_info)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if all_items:
                writer = csv.DictWriter(f, fieldnames=all_items[0].keys())
                writer.writeheader()
                writer.writerows(all_items)
    
    @staticmethod
    def export_file_types_csv(root_info: FileInfo, output_path: str) -> None:
        """Export file type statistics to CSV format."""
        stats = DiskAnalyzer.get_file_type_stats(root_info)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["File Extension", "File Count", "Total Size (Bytes)", "Total Size (Formatted)", "Percentage of Total"])
            
            total_size = root_info.size
            for ext, data in stats.items():
                percentage = (data["size"] / total_size * 100) if total_size > 0 else 0
                writer.writerow([
                    ext,
                    data["count"],
                    data["size"],
                    DiskAnalyzer.format_size(data["size"]),
                    f"{percentage:.2f}%"
                ])
    
    @staticmethod
    def export_largest_items_csv(root_info: FileInfo, output_path: str, count: int = 100) -> None:
        """Export largest items to CSV format."""
        largest_items = DiskAnalyzer.get_largest_items(root_info, count)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Rank", "Path", "Name", "Size (Bytes)", "Size (Formatted)", "Type"])
            
            for i, item in enumerate(largest_items, 1):
                writer.writerow([
                    i,
                    str(item.path),
                    item.name,
                    item.size,
                    DiskAnalyzer.format_size(item.size),
                    "Directory" if item.is_directory else "File"
                ])
