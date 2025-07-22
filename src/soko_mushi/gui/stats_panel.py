"""
Statistics panel component for displaying file and folder statistics using PyQt6.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QScrollArea, QFrame, QHBoxLayout
)
from PyQt6.QtCore import Qt

from ..core import FileInfo, DiskAnalyzer


class NumericTreeWidgetItem(QTreeWidgetItem):
    """QTreeWidgetItem with proper numeric sorting support."""
    
    def __lt__(self, other):
        """Custom comparison for sorting."""
        column = self.treeWidget().sortColumn()
        
        # Use numeric sorting for columns that have numeric UserRole data
        try:
            self_data = self.data(column, Qt.ItemDataRole.UserRole)
            other_data = other.data(column, Qt.ItemDataRole.UserRole)
            
            if self_data is not None and other_data is not None:
                return self_data < other_data
        except (TypeError, AttributeError):
            pass
        
        # Fall back to text comparison
        return super().__lt__(other)


class StatsWidget(QWidget):
    """Panel showing statistics about the current scan or selection."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup statistics UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Title
        title_label = QLabel("Statistics")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Tab widget for different stats
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_overview_tab()
        self._create_types_tab()
        self._create_largest_tab()
        
    def _create_overview_tab(self):
        """Create overview statistics tab."""
        # Scrollable widget for overview
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        overview_widget = QWidget()
        overview_layout = QVBoxLayout(overview_widget)
        overview_layout.setContentsMargins(15, 15, 15, 15)
        overview_layout.setSpacing(8)
        
        # Stats labels
        self.stats_labels = {}
        
        stats_info = [
            ("Total Size", "total_size"),
            ("Total Files", "total_files"),
            ("Total Folders", "total_folders"),
            ("Average File Size", "avg_file_size"),
            ("Largest File", "largest_file"),
            ("Largest Folder", "largest_folder"),
            ("Deepest Path", "deepest_path"),
            ("", "separator1"),  # Separator
            ("Drive Total", "drive_total"),
            ("Drive Used", "drive_used"),
            ("Drive Free", "drive_free"),
        ]
        
        for label_text, key in stats_info:
            # Handle separator
            if key.startswith("separator"):
                separator = QFrame()
                separator.setFrameStyle(QFrame.Shape.HLine | QFrame.Shadow.Sunken)
                separator.setStyleSheet("margin: 10px 0px; color: #888;")
                overview_layout.addWidget(separator)
                continue
                
            # Create frame for each stat
            stat_frame = QFrame()
            stat_frame.setFrameStyle(QFrame.Shape.StyledPanel)
            stat_layout = QHBoxLayout(stat_frame)
            stat_layout.setContentsMargins(10, 8, 10, 8)
            stat_layout.setSpacing(15)
            
            # Label name
            name_label = QLabel(f"{label_text}:")
            name_label.setMinimumWidth(120)
            name_label.setStyleSheet("font-weight: bold;")
            stat_layout.addWidget(name_label)
            
            # Value label
            value_label = QLabel("")
            value_label.setWordWrap(True)
            stat_layout.addWidget(value_label, 1)
            
            overview_layout.addWidget(stat_frame)
            self.stats_labels[key] = value_label
            
        overview_layout.addStretch()
        scroll_area.setWidget(overview_widget)
        self.tab_widget.addTab(scroll_area, "Overview")
        
    def _create_types_tab(self):
        """Create file types statistics tab."""
        self.types_tree = QTreeWidget()
        self.types_tree.setHeaderLabels(["File Type", "Count", "Size", "Percentage"])
        self.types_tree.setAlternatingRowColors(True)
        self.types_tree.setSortingEnabled(True)
        
        # Configure column widths
        header = self.types_tree.header()
        header.resizeSection(0, 120)  # File Type
        header.resizeSection(1, 80)   # Count
        header.resizeSection(2, 100)  # Size
        header.resizeSection(3, 100)  # Percentage
        
        self.tab_widget.addTab(self.types_tree, "File Types")
        
    def _create_largest_tab(self):
        """Create largest items tab."""
        self.largest_tree = QTreeWidget()
        self.largest_tree.setHeaderLabels(["Name", "Size", "Type"])
        self.largest_tree.setAlternatingRowColors(True)
        self.largest_tree.setSortingEnabled(True)
        
        # Configure column widths
        header = self.largest_tree.header()
        header.resizeSection(0, 200)  # Name
        header.resizeSection(1, 100)  # Size
        header.resizeSection(2, 80)   # Type
        
        self.tab_widget.addTab(self.largest_tree, "Largest Items")
        
    def update_stats(self, scan_data: FileInfo):
        """Update statistics with new scan data."""
        self._update_overview_stats(scan_data)
        self._update_file_types_stats(scan_data)
        self._update_largest_items_stats(scan_data)
        
    def _update_overview_stats(self, scan_data: FileInfo):
        """Update overview statistics."""
        # Calculate statistics
        total_files = 0
        total_folders = 0
        file_sizes = []
        largest_file = None
        largest_folder = None
        max_depth = 0
        deepest_path = ""
        
        def collect_stats(info: FileInfo, depth: int = 0):
            nonlocal total_files, total_folders, largest_file, largest_folder, max_depth, deepest_path
            
            if info.is_directory:
                total_folders += 1
                if largest_folder is None or info.size > largest_folder.size:
                    largest_folder = info
            else:
                total_files += 1
                file_sizes.append(info.size)
                if largest_file is None or info.size > largest_file.size:
                    largest_file = info
                    
            if depth > max_depth:
                max_depth = depth
                deepest_path = str(info.path)
                
            for child in info.children:
                collect_stats(child, depth + 1)
                
        collect_stats(scan_data)
        
        # Update labels
        self.stats_labels["total_size"].setText(DiskAnalyzer.format_size(scan_data.size))
        self.stats_labels["total_files"].setText(f"{total_files:,}")
        self.stats_labels["total_folders"].setText(f"{total_folders:,}")
        
        avg_size = sum(file_sizes) / len(file_sizes) if file_sizes else 0
        self.stats_labels["avg_file_size"].setText(DiskAnalyzer.format_size(int(avg_size)))
        
        if largest_file:
            self.stats_labels["largest_file"].setText(
                f"{largest_file.name} ({DiskAnalyzer.format_size(largest_file.size)})"
            )
        else:
            self.stats_labels["largest_file"].setText("N/A")
            
        if largest_folder:
            self.stats_labels["largest_folder"].setText(
                f"{largest_folder.name} ({DiskAnalyzer.format_size(largest_folder.size)})"
            )
        else:
            self.stats_labels["largest_folder"].setText("N/A")
            
        # Truncate deepest path if too long
        if len(deepest_path) > 50:
            deepest_path = "..." + deepest_path[-47:]
        self.stats_labels["deepest_path"].setText(deepest_path)
        
    def _update_file_types_stats(self, scan_data: FileInfo):
        """Update file types statistics."""
        # Clear existing items
        self.types_tree.clear()
        
        # Get file type statistics
        type_stats = DiskAnalyzer.get_file_type_stats(scan_data)
        total_size = scan_data.size
        
        # Insert items
        for ext, data in type_stats.items():
            percentage = (data["size"] / total_size * 100) if total_size > 0 else 0
            item = NumericTreeWidgetItem([
                ext,
                f"{data['count']:,}",
                DiskAnalyzer.format_size(data["size"]),
                f"{percentage:.1f}%"
            ])
            # Set sorting data for proper numeric sorting
            item.setData(1, Qt.ItemDataRole.UserRole, data['count'])  # Count column
            item.setData(2, Qt.ItemDataRole.UserRole, data["size"])   # Size column
            item.setData(3, Qt.ItemDataRole.UserRole, percentage)     # Percentage column
            self.types_tree.addTopLevelItem(item)
            
    def _update_largest_items_stats(self, scan_data: FileInfo):
        """Update largest items statistics."""
        # Clear existing items
        self.largest_tree.clear()
        
        # Get largest items
        largest_items = DiskAnalyzer.get_largest_items(scan_data, 50)
        
        # Insert items
        for item_info in largest_items:
            item_type = "Folder" if item_info.is_directory else "File"
            item = NumericTreeWidgetItem([
                item_info.name,
                DiskAnalyzer.format_size(item_info.size),
                item_type
            ])
            # Set sorting data for proper numeric sorting
            item.setData(1, Qt.ItemDataRole.UserRole, item_info.size)  # Size column
            self.largest_tree.addTopLevelItem(item)
            
    def update_selection_stats(self, file_info: FileInfo):
        """Update statistics for a selected item."""
        # For now, just update the overview with selection info
        # Could be enhanced to show selection-specific stats
        pass
        
    def update_drive_stats(self, total: str, used: str, free: str):
        """Update drive statistics in the overview panel."""
        if "drive_total" in self.stats_labels:
            self.stats_labels["drive_total"].setText(total)
        if "drive_used" in self.stats_labels:
            self.stats_labels["drive_used"].setText(used)
        if "drive_free" in self.stats_labels:
            self.stats_labels["drive_free"].setText(free)
        
    def clear(self):
        """Clear all statistics."""
        # Clear overview
        for label in self.stats_labels.values():
            label.setText("")
            
        # Clear trees
        self.types_tree.clear()
        self.largest_tree.clear()
