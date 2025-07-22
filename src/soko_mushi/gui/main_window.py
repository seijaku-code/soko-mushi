"""
Main window for Soko-Mushi application using PyQt6.
"""

import sys
import shutil
from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QProgressBar, QFileDialog, QMessageBox,
    QDialog, QDialogButtonBox, QRadioButton, QVBoxLayout as QVBox,
    QLabel, QButtonGroup
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QIcon

from ..core import DiskAnalyzer, FileInfo, ReportExporter
from .tree_view import TreeViewWidget
from .stats_panel import StatsWidget
from .toolbar import ToolbarWidget


class ScanThread(QThread):
    """Thread for disk scanning operations."""
    
    progress_updated = pyqtSignal(int, str)
    scan_completed = pyqtSignal(object)  # FileInfo object
    scan_error = pyqtSignal(str)
    
    def __init__(self, root_path: str):
        super().__init__()
        self.root_path = root_path
        self.analyzer = DiskAnalyzer()
        
    def run(self):
        """Run the disk scan in background thread."""
        try:
            self.analyzer.start_scan(
                self.root_path,
                progress_callback=self.progress_updated.emit,
                completion_callback=self.scan_completed.emit,
                error_callback=self.scan_error.emit
            )
        except Exception as e:
            self.scan_error.emit(str(e))
            
    def stop_scan(self):
        """Stop the current scan."""
        self.analyzer.stop_scan()


class SokoMushiApp(QMainWindow):
    """Main application window for Soko-Mushi."""
    
    def __init__(self):
        super().__init__()
        self.current_scan_data: Optional[FileInfo] = None
        self.scan_thread: Optional[ScanThread] = None
        self.is_scanning = False
        
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Soko-Mushi - Disk Analysis Tool (Free Edition)")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(2)
        
        # Toolbar
        self.toolbar_widget = ToolbarWidget()
        main_layout.addWidget(self.toolbar_widget)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Tree view (left panel)
        self.tree_view = TreeViewWidget()
        splitter.addWidget(self.tree_view)
        
        # Stats panel (right panel)
        self.stats_panel = StatsWidget()
        splitter.addWidget(self.stats_panel)
        
        # Set splitter proportions (2:1 ratio)
        splitter.setSizes([800, 400])
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Progress bar in status bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        self.status_bar.showMessage("Ready - Select a folder to scan")
        
        # Apply initial theme
        self._apply_application_theme("System")
        
    def _connect_signals(self):
        """Connect widget signals to slots."""
        self.toolbar_widget.scan_requested.connect(self._on_scan_click)
        self.toolbar_widget.export_requested.connect(self._on_export_click)
        self.toolbar_widget.theme_changed.connect(self._on_theme_change)
        self.tree_view.item_selected.connect(self._on_tree_item_select)
        self.tree_view.selection_cleared.connect(self._on_tree_selection_cleared)
        
    def _on_scan_click(self):
        """Handle scan button click."""
        if self.is_scanning:
            self._stop_scan()
        else:
            self._start_scan()
            
    def _start_scan(self):
        """Start a new disk scan."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select folder to analyze",
            str(Path.home())
        )
        
        if not folder_path:
            return
            
        self.is_scanning = True
        self.toolbar_widget.set_scan_button_text("Stop Scan")
        
        # Show simple scanning status
        self.status_bar.showMessage(f"Scanning: {folder_path}")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Clear previous data
        self.tree_view.clear()
        self.stats_panel.clear()
        
        # Start scan thread
        self.scan_thread = ScanThread(folder_path)
        self.scan_thread.progress_updated.connect(self._on_scan_progress)
        self.scan_thread.scan_completed.connect(self._on_scan_complete)
        self.scan_thread.scan_error.connect(self._on_scan_error)
        self.scan_thread.start()
        
    def _stop_scan(self):
        """Stop the current scan."""
        if self.scan_thread:
            self.scan_thread.stop_scan()
            self.scan_thread.wait()
            
        self._reset_scan_ui()
        
    def _reset_scan_ui(self):
        """Reset the scanning UI state."""
        self.is_scanning = False
        self.toolbar_widget.set_scan_button_text("Scan Folder")
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Scan stopped")
        
    def _on_scan_progress(self, depth: int, current_path: str):
        """Handle scan progress updates."""
        display_path = current_path
        if len(display_path) > 80:
            display_path = "..." + display_path[-77:]
            
        # Show simple progress status
        self.status_bar.showMessage(f"Scanning: {display_path}")
        
    def _get_drive_stats(self, path: str) -> tuple[str, str, str]:
        """Get drive statistics for the given path."""
        try:
            # Get disk usage statistics
            total, used, free = shutil.disk_usage(path)
            
            # Format sizes
            total_str = DiskAnalyzer.format_size(total)
            used_str = DiskAnalyzer.format_size(used)
            free_str = DiskAnalyzer.format_size(free)
            
            return total_str, used_str, free_str
        except Exception:
            return "Unknown", "Unknown", "Unknown"
        
    def _on_scan_complete(self, scan_data: FileInfo):
        """Handle scan completion."""
        self.current_scan_data = scan_data
        self._reset_scan_ui()
        
        # Populate UI components
        self.tree_view.populate_tree(scan_data)
        self.stats_panel.update_stats(scan_data)
        
        # Get drive statistics and update stats panel
        total_drive, used_drive, free_drive = self._get_drive_stats(str(scan_data.path))
        self.stats_panel.update_drive_stats(total_drive, used_drive, free_drive)
        
        # Update status with scan results only
        scanned_size = DiskAnalyzer.format_size(scan_data.size)
        status_message = f"Scan complete - Scanned: {scanned_size}"
        self.status_bar.showMessage(status_message)
        
    def _on_scan_error(self, error_message: str):
        """Handle scan errors."""
        self._reset_scan_ui()
        QMessageBox.critical(self, "Scan Error", error_message)
        
    def _on_tree_item_select(self, file_info: FileInfo):
        """Handle tree item selection."""
        self.stats_panel.update_selection_stats(file_info)
        
        # Update status bar with selection info
        selected_size = DiskAnalyzer.format_size(file_info.size)
        status_message = f"Selected: {file_info.name} ({selected_size})"
        self.status_bar.showMessage(status_message)
        
    def _on_tree_selection_cleared(self):
        """Handle when tree selection is cleared."""
        # Restore the scan complete status
        if self.current_scan_data:
            scanned_size = DiskAnalyzer.format_size(self.current_scan_data.size)
            status_message = f"Scan complete - Scanned: {scanned_size}"
            self.status_bar.showMessage(status_message)
        else:
            self.status_bar.showMessage("Ready - Select a folder to scan")
        
    def _on_export_click(self):
        """Handle export button click."""
        if not self.current_scan_data:
            QMessageBox.warning(self, "No Data", "Please scan a folder first")
            return
            
        dialog = ExportDialog(self, self.current_scan_data)
        dialog.exec()
        
    def _on_theme_change(self, theme: str):
        """Handle theme change."""
        self.status_bar.showMessage(f"Theme changed to: {theme}", 2000)
        self._apply_application_theme(theme)
        
    def _apply_application_theme(self, theme: str):
        """Apply theme to the entire application."""
        if theme == "Light":
            self._apply_light_theme()
        elif theme == "Dark":
            self._apply_dark_theme()
        else:  # System
            self._apply_dark_theme()  # Default to dark for now
            
    def _apply_light_theme(self):
        """Apply light theme to the application."""
        app_style = """
            QMainWindow {
                background-color: #f0f0f0;
                color: black;
            }
            QWidget {
                background-color: #f0f0f0;
                color: black;
            }
            QTreeWidget {
                background-color: white;
                alternate-background-color: #f8f8f8;
                color: black;
                border: 1px solid #d0d0d0;
            }
            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid #e0e0e0;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #e5f3ff;
            }
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e8e8e8;
                color: black;
                padding: 8px 16px;
                border: 1px solid #d0d0d0;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover {
                background-color: #f0f0f0;
            }
            QLabel {
                color: black;
            }
            QFrame {
                background-color: #f8f8f8;
                border: 1px solid #d0d0d0;
            }
            QScrollArea {
                background-color: white;
                border: 1px solid #d0d0d0;
            }
            QStatusBar {
                background-color: #e8e8e8;
                color: black;
                border-top: 1px solid #d0d0d0;
            }
        """
        self.setStyleSheet(app_style)
        
    def _apply_dark_theme(self):
        """Apply dark theme to the application."""
        app_style = """
            QMainWindow {
                background-color: #2b2b2b;
                color: white;
            }
            QWidget {
                background-color: #2b2b2b;
                color: white;
            }
            QTreeWidget {
                background-color: #383838;
                alternate-background-color: #404040;
                color: white;
                border: 1px solid #555555;
            }
            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid #555555;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #505050;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #383838;
            }
            QTabBar::tab {
                background-color: #404040;
                color: white;
                padding: 8px 16px;
                border: 1px solid #555555;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #383838;
                border-bottom: 1px solid #383838;
            }
            QTabBar::tab:hover {
                background-color: #4a4a4a;
            }
            QLabel {
                color: white;
            }
            QFrame {
                background-color: #404040;
                border: 1px solid #555555;
            }
            QScrollArea {
                background-color: #383838;
                border: 1px solid #555555;
            }
            QStatusBar {
                background-color: #404040;
                color: white;
                border-top: 1px solid #555555;
            }
        """
        self.setStyleSheet(app_style)
        
    def closeEvent(self, event):
        """Handle application closing."""
        if self.is_scanning and self.scan_thread:
            self.scan_thread.stop_scan()
            self.scan_thread.wait()
        event.accept()


class ExportDialog(QDialog):
    """Dialog for export options."""
    
    def __init__(self, parent: QMainWindow, scan_data: FileInfo):
        super().__init__(parent)
        self.scan_data = scan_data
        self.setWindowTitle("Export Report")
        self.setModal(True)
        self.resize(400, 300)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBox(self)
        
        # Title
        title_label = QLabel("Export Options")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # Radio buttons for export options
        self.button_group = QButtonGroup()
        
        self.json_radio = QRadioButton("Complete Report (JSON)")
        self.json_radio.setChecked(True)
        self.button_group.addButton(self.json_radio, 0)
        layout.addWidget(self.json_radio)
        
        self.csv_radio = QRadioButton("File List (CSV)")
        self.button_group.addButton(self.csv_radio, 1)
        layout.addWidget(self.csv_radio)
        
        self.types_radio = QRadioButton("File Types Statistics (CSV)")
        self.button_group.addButton(self.types_radio, 2)
        layout.addWidget(self.types_radio)
        
        self.largest_radio = QRadioButton("Largest Items (CSV)")
        self.button_group.addButton(self.largest_radio, 3)
        layout.addWidget(self.largest_radio)
        
        layout.addStretch()
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._export)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def _export(self):
        """Perform the export."""
        export_type = self.button_group.checkedId()
        
        # File filters and default names
        filters = {
            0: ("JSON files (*.json)", "soko_mushi_report.json", ".json"),
            1: ("CSV files (*.csv)", "soko_mushi_files.csv", ".csv"),
            2: ("CSV files (*.csv)", "soko_mushi_file_types.csv", ".csv"),
            3: ("CSV files (*.csv)", "soko_mushi_largest_items.csv", ".csv"),
        }
        
        file_filter, default_name, extension = filters[export_type]
        
        # Ask for save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Export As",
            default_name,
            file_filter
        )
        
        if not file_path:
            return
            
        try:
            # Perform export
            if export_type == 0:  # JSON
                ReportExporter.export_to_json(self.scan_data, file_path)
            elif export_type == 1:  # CSV
                ReportExporter.export_to_csv(self.scan_data, file_path)
            elif export_type == 2:  # Types CSV
                ReportExporter.export_file_types_csv(self.scan_data, file_path)
            elif export_type == 3:  # Largest CSV
                ReportExporter.export_largest_items_csv(self.scan_data, file_path)
                
            QMessageBox.information(self, "Export Complete", f"Report exported to:\n{file_path}")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export report:\n{str(e)}")


def run_app():
    """Run the Soko-Mushi application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Soko-Mushi")
    app.setApplicationVersion("1.0.0")
    
    window = SokoMushiApp()
    window.show()
    
    return app.exec()
