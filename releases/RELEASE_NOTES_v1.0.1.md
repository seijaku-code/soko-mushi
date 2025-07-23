# Soko-Mushi v1.0.1 Release Notes

## 🆕 Version 1.0.1 Update

This update brings improved cross-platform compatibility and a more robust build process for Soko-Mushi!

### ✨ What's New

- **PySide6 Migration**: The GUI framework has been migrated from PyQt6 to PySide6 for better compatibility, especially on macOS and Linux. This ensures smoother builds and a more consistent user experience across all platforms.
- **Revised Build Script**: The build process is now more reliable and automated:
  - The build script now handles platform-specific options for Windows, macOS, and Linux.
  - Improved macOS support: The script ensures the app bundle icon is set correctly and Info.plist is updated automatically.
  - Optional renaming of the .app bundle for macOS, with post-build icon and Info.plist fixes.
  - Cleaner output and error handling.
- **General Improvements**:
  - Minor bug fixes and code cleanup.
  - Updated documentation for building and packaging on all platforms.

### 📦 Downloads

- **Windows**: `soko-mushi-v1.0.1-windows-x64.exe` (Standalone executable, no installation required)
- **Linux**: `soko-mushi-v1.0.1-linux-x64` (Standalone executable, no installation required)
- **macOS**: `soko-mushi-v1.0.1-macOS.dmg` (App bundle in DMG format)
- **Source Code**: Available on GitHub for building on other platforms

### 🚀 Getting Started

1. Download the executable for your platform
2. Run the application (no installation required)
3. Select a folder to analyze
4. Explore your disk usage with the interactive tree view

### 🐛 Known Issues

- Large directories (>100K files) may take time to scan
- Some antivirus software may flag the executable (false positive)
- On macOS, unsigned builds require right-click > Open to bypass Gatekeeper

### ⚠️ macOS Gatekeeper Note

If you see a "damaged" or "corrupt" warning when opening the app on macOS, this is due to Apple's Gatekeeper quarantine for unsigned apps. To resolve:

1. Open Terminal.
2. Run the following command (replace the path if needed):
   ```sh
   xattr -dr com.apple.quarantine ~/Downloads/soko-mushi-v1.0.1-mac.dmg
   ```
3. You can now open the app normally.

Alternatively, right-click the app and choose "Open" to bypass the warning for unsigned apps.

### 🔗 Links

- **GitHub Repository**: https://github.com/seijaku-code/soko-mushi
- **Bug Reports**: https://github.com/seijaku-code/soko-mushi/issues
- **Support the Project**: https://buymeacoffee.com/seijaku

### 🙏 Acknowledgments

Special thanks to:
- PySide6 team for the excellent GUI framework
- Nuitka team for Python-to-executable compilation
- All beta testers and contributors

---

**File Information:**

- Version: 1.0.1
- Build Date: July 2025
- Platforms:
  - **Windows x64**: ~24MB, Windows 10/11 (no additional dependencies)
  - **Linux x64**: ~22MB, tested on Ubuntu 22.04+ and recent distributions (no additional dependencies)
  - **macOS**: Universal app bundle, tested on macOS 13+ (no additional dependencies)
