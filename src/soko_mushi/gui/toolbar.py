"""
Toolbar component for Soko-Mushi application using PyQt6.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox, QFrame
from PyQt6.QtCore import pyqtSignal, Qt


class ToolbarWidget(QWidget):
    """Toolbar with scan and export buttons."""
    
    scan_requested = pyqtSignal()
    export_requested = pyqtSignal()
    theme_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = "System"
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup toolbar UI."""
        # Set fixed height for toolbar
        self.setFixedHeight(45)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)
        
        # Scan button
        self.scan_button = QPushButton("Scan Folder")
        self.scan_button.setMinimumWidth(100)
        self.scan_button.setMinimumHeight(32)
        self.scan_button.clicked.connect(self.scan_requested.emit)
        layout.addWidget(self.scan_button)
        
        # Export button
        self.export_button = QPushButton("Export Report")
        self.export_button.setMinimumWidth(100)
        self.export_button.setMinimumHeight(32)
        self.export_button.clicked.connect(self.export_requested.emit)
        layout.addWidget(self.export_button)
        
        # Separator
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.VLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.separator.setMaximumHeight(30)
        layout.addWidget(self.separator)
        
        # Theme selector
        self.theme_label = QLabel("Theme:")
        layout.addWidget(self.theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        self.theme_combo.setMinimumWidth(80)
        self.theme_combo.setMinimumHeight(30)
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        layout.addWidget(self.theme_combo)
        
        # Stretch to push info label to right
        layout.addStretch()
        
        # Info label
        self.info_label = QLabel("Soko-Mushi Free Edition")
        layout.addWidget(self.info_label)
        
        # Apply initial theme
        self._apply_theme("System")
        
    def _on_theme_changed(self, theme: str):
        """Handle theme combo change."""
        self.current_theme = theme
        self._apply_theme(theme)
        self.theme_changed.emit(theme)
        
    def _apply_theme(self, theme: str):
        """Apply theme styling to toolbar."""
        if theme == "Light":
            self._apply_light_theme()
        elif theme == "Dark":
            self._apply_dark_theme()
        else:  # System
            self._apply_system_theme()
            
    def _apply_light_theme(self):
        """Apply light theme styling."""
        self.setStyleSheet("QWidget { background-color: #f0f0f0; }")
        
        button_style = """
            QPushButton { 
                padding: 4px 10px; 
                font-size: 12px; 
                color: black;
                background-color: #e1e1e1;
                border: 1px solid #adadad;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #d4d4d4;
                border-color: #999999;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
                border-color: #888888;
            }
        """
        
        self.scan_button.setStyleSheet(button_style)
        self.export_button.setStyleSheet(button_style)
        
        self.separator.setStyleSheet("QFrame { margin: 0px 8px; color: #adadad; }")
        self.theme_label.setStyleSheet("QLabel { margin-right: 4px; font-size: 12px; color: black; }")
        self.info_label.setStyleSheet("QLabel { font-weight: bold; font-size: 12px; color: black; }")
        
        combo_style = """
            QComboBox { 
                padding: 3px 8px; 
                font-size: 12px; 
                color: black;
                background-color: white;
                border: 1px solid #adadad;
                border-radius: 3px;
            }
            QComboBox:hover {
                background-color: #f5f5f5;
                border-color: #999999;
            }
            QComboBox::drop-down {
                border: none;
                background-color: white;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid black;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                border: 1px solid #adadad;
                selection-background-color: #e0e0e0;
            }
        """
        self.theme_combo.setStyleSheet(combo_style)
        
    def _apply_dark_theme(self):
        """Apply dark theme styling."""
        self.setStyleSheet("QWidget { background-color: #2b2b2b; }")
        
        button_style = """
            QPushButton { 
                padding: 4px 10px; 
                font-size: 12px; 
                color: white;
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #707070;
            }
            QPushButton:pressed {
                background-color: #353535;
                border-color: #555555;
            }
        """
        
        self.scan_button.setStyleSheet(button_style)
        self.export_button.setStyleSheet(button_style)
        
        self.separator.setStyleSheet("QFrame { margin: 0px 8px; color: #606060; }")
        self.theme_label.setStyleSheet("QLabel { margin-right: 4px; font-size: 12px; color: white; }")
        self.info_label.setStyleSheet("QLabel { font-weight: bold; font-size: 12px; color: white; }")
        
        combo_style = """
            QComboBox { 
                padding: 3px 8px; 
                font-size: 12px; 
                color: white;
                background-color: #404040;
                border: 1px solid #606060;
                border-radius: 3px;
            }
            QComboBox:hover {
                background-color: #4a4a4a;
                border-color: #707070;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #404040;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid white;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #404040;
                color: white;
                border: 1px solid #606060;
                selection-background-color: #505050;
            }
        """
        self.theme_combo.setStyleSheet(combo_style)
        
    def _apply_system_theme(self):
        """Apply system theme styling."""
        # Use dark theme as default for now, could detect system theme
        self._apply_dark_theme()
        
    def set_scan_button_text(self, text: str):
        """Update scan button text."""
        self.scan_button.setText(text)
