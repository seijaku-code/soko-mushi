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
        '--standalone',
        '--onefile',
        '--enable-plugin=pyside6',
        '--windows-console-mode=disable' if platform == 'windows' else '--enable-console',
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
            '--windows-icon-from-ico=assets/icon.ico' if Path('assets/icon.ico').exists() else ''
        ])
    
        # Add Mac-specific options
    if platform == 'macos':
        cmd.extend([
            '--static-libpython=no',
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
        exe_path = Path('dist') / f"soko-mushi{exe_extension}"
        if exe_path.exists():
            print(f"📦 Executable created: {exe_path.absolute()}")
            print(f"📏 File size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
        else:
            print("❌ Executable not found in expected location")
            
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
