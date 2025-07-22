"""
Tree view component for displaying file hierarchy using PyQt6.
"""

import subprocess
import os
import shutil
from typing import Optional, Dict
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

# Import for cross-platform recycle bin functionality
try:
    from send2trash import send2trash
    HAS_SEND2TRASH = True
except ImportError:
    HAS_SEND2TRASH = False

from ..core import FileInfo, DiskAnalyzer


class NumericTreeWidgetItem(QTreeWidgetItem):
    """QTreeWidgetItem with proper numeric sorting support."""
    
    def __lt__(self, other):
        """Custom comparison for sorting."""
        column = self.treeWidget().sortColumn()
        
        # For Size column (1) and Items column (2), use numeric sorting
        if column in [1, 2]:
            try:
                self_data = self.data(column, Qt.ItemDataRole.UserRole)
                other_data = other.data(column, Qt.ItemDataRole.UserRole)
                
                if self_data is not None and other_data is not None:
                    return self_data < other_data
            except (TypeError, AttributeError):
                pass
        
        # Fall back to text comparison for other columns
        return super().__lt__(other)


class TreeViewWidget(QWidget):
    """Widget containing the hierarchical tree view of files and folders."""
    
    item_selected = pyqtSignal(object)  # FileInfo object
    selection_cleared = pyqtSignal()    # Emitted when no items are selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_info_map: Dict[int, FileInfo] = {}  # Use item ID as key
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup tree view UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Title
        title_label = QLabel("Folder Structure")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Tree widget
        self.tree = QTreeWidget()
        layout.addWidget(self.tree)
        
        # Configure tree
        self.tree.setHeaderLabels(["Name", "Size", "Items", "Type", "Path"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(True)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)  # Enable multiselect
        
        # Configure column widths
        header = self.tree.header()
        header.resizeSection(0, 300)  # Name
        header.resizeSection(1, 100)  # Size
        header.resizeSection(2, 80)   # Items
        header.resizeSection(3, 100)  # Type
        header.resizeSection(4, 400)  # Path
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        
        # Connect signals
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        
    def _is_file_locked(self, file_path: Path) -> bool:
        """Check if a file is locked by another process."""
        if not file_path.exists():
            return False
            
        if file_path.is_dir():
            # For directories, try to create and remove a temporary file inside
            try:
                temp_file = file_path / '.temp_lock_check'
                temp_file.touch()
                temp_file.unlink()
                return False
            except (OSError, PermissionError):
                return True
        else:
            # For files, try to open in exclusive mode
            try:
                with open(file_path, 'r+b') as f:
                    pass
                return False
            except (OSError, PermissionError):
                return True
        
    def _on_selection_changed(self):
        """Handle tree item selection."""
        current_item = self.tree.currentItem()
        if current_item:
            item_id = id(current_item)
            if item_id in self.file_info_map:
                file_info = self.file_info_map[item_id]
                self.item_selected.emit(file_info)
        else:
            # No item selected - emit clear signal
            self.selection_cleared.emit()
            
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double-click to expand/collapse."""
        item.setExpanded(not item.isExpanded())
        
    def _show_context_menu(self, position):
        """Show context menu."""
        item = self.tree.itemAt(position)
        if not item:
            return
            
        menu = QMenu(self)
        selected_items = self.tree.selectedItems()
        
        # Expand/Collapse actions
        expand_all_action = QAction("Expand All", self)
        expand_all_action.setStatusTip("")  # Clear status tip to prevent clearing status bar
        expand_all_action.triggered.connect(self._expand_all)
        menu.addAction(expand_all_action)
        
        collapse_all_action = QAction("Collapse All", self)
        collapse_all_action.setStatusTip("")  # Clear status tip to prevent clearing status bar
        collapse_all_action.triggered.connect(self._collapse_all)
        menu.addAction(collapse_all_action)
        
        menu.addSeparator()
        
        # Show in explorer action (only for single selection)
        if len(selected_items) == 1:
            item_id = id(selected_items[0])
            if item_id in self.file_info_map:
                show_explorer_action = QAction("Show in Explorer", self)
                show_explorer_action.setStatusTip("")  # Clear status tip to prevent clearing status bar
                show_explorer_action.triggered.connect(lambda: self._show_in_explorer(selected_items[0]))
                menu.addAction(show_explorer_action)
                
                menu.addSeparator()
        
        # Delete/Recycle actions (for single or multiple selection)
        if selected_items:
            if len(selected_items) == 1:
                # Single item
                if HAS_SEND2TRASH:
                    recycle_action = QAction("Send to Recycle Bin", self)
                    recycle_action.setStatusTip("")  # Clear status tip to prevent clearing status bar
                    recycle_action.triggered.connect(lambda: self._delete_items(selected_items, use_recycle_bin=True))
                    menu.addAction(recycle_action)
                
                delete_action = QAction("Delete Permanently", self)
                delete_action.setStatusTip("")  # Clear status tip to prevent clearing status bar
                delete_action.triggered.connect(lambda: self._delete_items(selected_items, use_recycle_bin=False))
                menu.addAction(delete_action)
            else:
                # Multiple items
                if HAS_SEND2TRASH:
                    recycle_action = QAction(f"Send {len(selected_items)} Items to Recycle Bin", self)
                    recycle_action.setStatusTip("")  # Clear status tip to prevent clearing status bar
                    recycle_action.triggered.connect(lambda: self._delete_items(selected_items, use_recycle_bin=True))
                    menu.addAction(recycle_action)
                
                delete_action = QAction(f"Delete {len(selected_items)} Items Permanently", self)
                delete_action.setStatusTip("")  # Clear status tip to prevent clearing status bar
                delete_action.triggered.connect(lambda: self._delete_items(selected_items, use_recycle_bin=False))
                menu.addAction(delete_action)
        
        menu.exec(self.tree.mapToGlobal(position))
        
    def _expand_all(self):
        """Expand all tree items."""
        self.tree.expandAll()
        
    def _collapse_all(self):
        """Collapse all tree items."""
        self.tree.collapseAll()
        
    def _show_in_explorer(self, item: QTreeWidgetItem):
        """Show selected item in file explorer."""
        item_id = id(item)
        if item_id not in self.file_info_map:
            return
            
        file_info = self.file_info_map[item_id]
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(['explorer', '/select,', str(file_info.path)], check=False)
            elif os.name == 'posix':  # macOS and Linux
                if os.uname().sysname == 'Darwin':  # macOS
                    subprocess.run(['open', '-R', str(file_info.path)], check=False)
                else:  # Linux
                    subprocess.run(['xdg-open', str(file_info.path.parent)], check=False)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open file explorer: {str(e)}")
            
    def _delete_item(self, item: QTreeWidgetItem, use_recycle_bin: bool = True):
        """Delete or recycle the selected item."""
        item_id = id(item)
        if item_id not in self.file_info_map:
            return
            
        file_info = self.file_info_map[item_id]
        file_path = Path(file_info.path)
        
        # Check if file is locked
        is_locked = self._is_file_locked(file_path)
        
        # Confirm deletion
        if file_info.is_directory:
            msg = f"Are you sure you want to delete the folder '{file_info.name}' and all its contents?"
        else:
            msg = f"Are you sure you want to delete the file '{file_info.name}'?"
            
        if use_recycle_bin and HAS_SEND2TRASH:
            msg += "\n\nThis will send the item to the Recycle Bin."
        else:
            msg += "\n\nThis action cannot be undone - the item will be permanently deleted."
            
        if is_locked:
            msg += "\n\nWarning: This file appears to be locked or in use by another application. Deletion will likely fail."
            
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
            
        try:
            if use_recycle_bin and HAS_SEND2TRASH:
                # Use send2trash library for cross-platform recycle bin support
                send2trash(str(file_path))
                action_msg = "sent to Recycle Bin"
            else:
                # Permanent deletion
                if file_path.is_dir():
                    shutil.rmtree(file_path)
                else:
                    file_path.unlink()
                action_msg = "permanently deleted"
                
            # Remove item from tree
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                # Root level item
                index = self.tree.indexOfTopLevelItem(item)
                if index >= 0:
                    self.tree.takeTopLevelItem(index)
                    
            # Remove from file info map
            del self.file_info_map[item_id]
            
            QMessageBox.information(
                self, 
                "Success", 
                f"'{file_info.name}' has been {action_msg} successfully."
            )
            
        except PermissionError:
            QMessageBox.warning(
                self, 
                "Permission Denied", 
                f"Cannot delete '{file_info.name}': File is in use by another application or you don't have permission to delete it."
            )
        except OSError as e:
            if "being used by another process" in str(e).lower() or "access is denied" in str(e).lower():
                QMessageBox.warning(
                    self, 
                    "File In Use", 
                    f"Cannot delete '{file_info.name}': The file is currently being used by another application."
                )
            else:
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"Could not delete '{file_info.name}':\n{str(e)}"
                )
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Could not delete '{file_info.name}':\n{str(e)}"
            )
            
    def _delete_items(self, items: list[QTreeWidgetItem], use_recycle_bin: bool = True):
        """Delete or recycle multiple selected items."""
        if not items:
            return
            
        # Get file info for all items
        items_to_delete = []
        for item in items:
            item_id = id(item)
            if item_id in self.file_info_map:
                file_info = self.file_info_map[item_id]
                items_to_delete.append((item, file_info))
        
        if not items_to_delete:
            return
        
        # Check for locked files
        locked_files = []
        for item, file_info in items_to_delete:
            if self._is_file_locked(Path(file_info.path)):
                locked_files.append(file_info.name)
        
        # Confirm deletion
        if len(items_to_delete) == 1:
            item, file_info = items_to_delete[0]
            if file_info.is_directory:
                msg = f"Are you sure you want to delete the folder '{file_info.name}' and all its contents?"
            else:
                msg = f"Are you sure you want to delete the file '{file_info.name}'?"
        else:
            folders = sum(1 for _, fi in items_to_delete if fi.is_directory)
            files = len(items_to_delete) - folders
            
            if folders > 0 and files > 0:
                msg = f"Are you sure you want to delete {folders} folder(s) and {files} file(s)?"
            elif folders > 0:
                msg = f"Are you sure you want to delete {folders} folder(s) and all their contents?"
            else:
                msg = f"Are you sure you want to delete {files} file(s)?"
            
        if use_recycle_bin and HAS_SEND2TRASH:
            msg += "\n\nThese items will be sent to the Recycle Bin."
        else:
            msg += "\n\nThis action cannot be undone - the items will be permanently deleted."
            
        if locked_files:
            if len(locked_files) == 1:
                msg += f"\n\nWarning: '{locked_files[0]}' appears to be locked or in use. Deletion may fail."
            else:
                msg += f"\n\nWarning: {len(locked_files)} files appear to be locked or in use. Some deletions may fail."
            
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Delete items
        successful_deletions = []
        failed_deletions = []
        
        for item, file_info in items_to_delete:
            try:
                file_path = Path(file_info.path)
                
                if use_recycle_bin and HAS_SEND2TRASH:
                    send2trash(str(file_path))
                else:
                    if file_path.is_dir():
                        shutil.rmtree(file_path)
                    else:
                        file_path.unlink()
                
                # Remove from tree and file info map
                parent = item.parent()
                if parent:
                    parent.removeChild(item)
                else:
                    index = self.tree.indexOfTopLevelItem(item)
                    if index >= 0:
                        self.tree.takeTopLevelItem(index)
                
                del self.file_info_map[id(item)]
                successful_deletions.append(file_info.name)
                
            except Exception as e:
                failed_deletions.append((file_info.name, str(e)))
        
        # Show results
        if successful_deletions and not failed_deletions:
            action_msg = "sent to Recycle Bin" if (use_recycle_bin and HAS_SEND2TRASH) else "permanently deleted"
            if len(successful_deletions) == 1:
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"'{successful_deletions[0]}' has been {action_msg} successfully."
                )
            else:
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"{len(successful_deletions)} items have been {action_msg} successfully."
                )
        elif successful_deletions and failed_deletions:
            action_msg = "sent to Recycle Bin" if (use_recycle_bin and HAS_SEND2TRASH) else "permanently deleted"
            msg = f"{len(successful_deletions)} items were {action_msg} successfully.\n\n"
            msg += f"Failed to delete {len(failed_deletions)} items:\n"
            for name, error in failed_deletions[:5]:  # Show first 5 errors
                msg += f"• {name}: {error[:50]}...\n"
            if len(failed_deletions) > 5:
                msg += f"... and {len(failed_deletions) - 5} more"
            
            QMessageBox.warning(self, "Partial Success", msg)
        else:
            # All deletions failed
            if len(failed_deletions) == 1:
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"Could not delete '{failed_deletions[0][0]}':\n{failed_deletions[0][1]}"
                )
            else:
                msg = f"Failed to delete all {len(failed_deletions)} items.\n\nFirst few errors:\n"
                for name, error in failed_deletions[:3]:
                    msg += f"• {name}: {error[:50]}...\n"
                QMessageBox.critical(self, "Error", msg)
            
    def populate_tree(self, root_info: FileInfo):
        """Populate tree with file information."""
        self.clear()
        
        # Create root item
        root_item = self._create_tree_item(None, root_info)
        self.tree.addTopLevelItem(root_item)
        
        # Expand root by default
        root_item.setExpanded(True)
        
        # Auto-expand first level if not too many items
        if len(root_info.children) <= 20:
            for i in range(root_item.childCount()):
                child = root_item.child(i)
                child.setExpanded(True)
                
    def _create_tree_item(self, parent_item: Optional[QTreeWidgetItem], file_info: FileInfo) -> QTreeWidgetItem:
        """Create a tree item for the given file info."""
        # Determine display values
        name = file_info.name
        size_str = DiskAnalyzer.format_size(file_info.size)
        
        if file_info.is_directory:
            items_count = len(file_info.children)
            items_str = f"{items_count} items"
            type_str = "Folder"
            icon = "📁"
        else:
            items_str = ""
            if file_info.extension:
                type_str = f"{file_info.extension.upper()} File"
            else:
                type_str = "File"
            icon = "📄"
        
        # Create item
        display_name = f"{icon} {name}"
        path_str = str(file_info.path)
        item = NumericTreeWidgetItem([display_name, size_str, items_str, type_str, path_str])
        
        # Set sorting data for proper numeric sorting
        item.setData(1, Qt.ItemDataRole.UserRole, file_info.size)  # Size column - use raw bytes for sorting
        if file_info.is_directory:
            item.setData(2, Qt.ItemDataRole.UserRole, len(file_info.children))  # Items column - use count for sorting
        else:
            item.setData(2, Qt.ItemDataRole.UserRole, 0)  # Files have 0 items
        
        # Store file info mapping using item's memory id
        self.file_info_map[id(item)] = file_info
        
        # Add children (sorted by size, largest first)
        sorted_children = sorted(
            file_info.children,
            key=lambda x: x.size,
            reverse=True
        )
        
        for child in sorted_children:
            child_item = self._create_tree_item(item, child)
            item.addChild(child_item)
            
        return item
        
    def clear(self):
        """Clear the tree view."""
        self.tree.clear()
        self.file_info_map.clear()
