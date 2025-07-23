#!/usr/bin/env python3
"""
Build script for compiling Soko-Mushi with Nuitka.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def build_executable():
    """Build the executable using Nuitka."""
    
    # Determine the platform
    if sys.platform.startswith('win'):
        platform = 'windows'
        exe_extension = '.exe'
    elif sys.platform.startswith('darwin'):
        platform = 'macos'
        exe_extension = ''
    else:
        platform = 'linux'
        exe_extension = ''
    
    # Build command
    cmd = [
        sys.executable, '-m', 'nuitka',
        '--mode=app',
        '--enable-plugin=pyside6',
        '--output-filename=soko-mushi' + exe_extension,
        '--output-dir=dist',
#        '--include-data-dir=src/soko_mushi=soko_mushi',
        '--product-name=Soko-Mushi',
        '--product-version=1.0.0',
        '--file-description=Local Disk Analysis Tool',
        '--copyright=Seijaku',
        'soko_mushi/main.py'
    ]
    
    # Add Windows-specific options
    if platform == 'windows':
        cmd.extend([
            '--windows-console-mode=disable',
            '--windows-icon-from-ico=../assets/icon.ico' if Path('../assets/icon.ico').exists() else ''
        ])
    
        # Add Mac-specific options
    if platform == 'macos':
        cmd.extend([
            '--static-libpython=no',
            '--mode=app',
            '--macos-app-icon=../assets/icon.icns' if Path('../assets/icon.icns').exists() else ''
        ])

    # Remove empty arguments
    cmd = [arg for arg in cmd if arg]
    
    print("Building Soko-Mushi executable...")
    print(f"Platform: {platform}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    # Clean previous build
    if Path('dist').exists():
        print("Cleaning previous build...")
        shutil.rmtree('dist')
    
    # Run Nuitka
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ Build completed successfully!")
        
        # Show output location
        if platform == 'macos':
            # Nuitka --mode=app creates a .app bundle
            app_bundle = Path('dist') / 'main.app'
            target_bundle = Path('dist') / 'soko-mushi.app'
            icon_src = Path('../assets/icon.icns')
            if app_bundle.exists():
                if target_bundle.exists():
                    shutil.rmtree(target_bundle)
                app_bundle.rename(target_bundle)
                print(f"Renamed app bundle to: {target_bundle.absolute()}")

                # Ensure icon.icns is in Resources
                resources_dir = target_bundle / 'Contents' / 'Resources'
                if icon_src.exists():
                    resources_dir.mkdir(parents=True, exist_ok=True)
                    icon_dst = resources_dir / 'icon.icns'
                    shutil.copy(icon_src, icon_dst)
                    print(f"Copied icon.icns to: {icon_dst}")

                # Update Info.plist to reference icon.icns
                plist_path = target_bundle / 'Contents' / 'Info.plist'
                if plist_path.exists():
                    with open(plist_path, 'r', encoding='utf-8') as f:
                        plist_data = f.read()
                    import re
                    # Replace or add CFBundleIconFile
                    if '<key>CFBundleIconFile</key>' in plist_data:
                        plist_data = re.sub(r'<key>CFBundleIconFile</key>\s*<string>.*?</string>', '<key>CFBundleIconFile</key>\n    <string>icon.icns</string>', plist_data)
                    else:
                        # Insert before </dict>
                        plist_data = plist_data.replace('</dict>', '    <key>CFBundleIconFile</key>\n    <string>icon.icns</string>\n</dict>')
                    with open(plist_path, 'w', encoding='utf-8') as f:
                        f.write(plist_data)
                    print(f"Updated Info.plist to reference icon.icns")
                else:
                    print("Info.plist not found in app bundle!")
            else:
                print("\u274C .app bundle or executable not found in expected location")
        else:
            exe_path = Path('dist') / f"soko-mushi{exe_extension}"
            if exe_path.exists():
                print(f"\U0001F4E6 Executable created: {exe_path.absolute()}")
                print(f"\U0001F4CF File size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
            else:
                print("\u274C Executable not found in expected location")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with exit code {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Nuitka not found. Please install it with: pip install nuitka")
        sys.exit(1)


def build_installer():
    """Create an installer package (platform-specific)."""
    platform = sys.platform
    
    if platform.startswith('win'):
        print("To create a Windows installer, you can use:")
        print("1. Inno Setup (https://jrsoftware.org/isinfo.php)")
        print("2. NSIS (https://nsis.sourceforge.io/)")
        print("3. WiX Toolset (https://wixtoolset.org/)")
    elif platform.startswith('darwin'):
        print("To create a macOS installer, you can use:")
        print("1. create-dmg (https://github.com/sindresorhus/create-dmg)")
        print("2. pkgbuild and productbuild (built into macOS)")
    else:
        print("To create a Linux package, you can use:")
        print("1. fpm (https://fpm.readthedocs.io/)")
        print("2. Native package managers (dpkg, rpm, etc.)")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build Soko-Mushi executable")
    parser.add_argument("--installer", action="store_true", help="Show installer creation info")
    
    args = parser.parse_args()
    
    if args.installer:
        build_installer()
    else:
        build_executable()
