#!/usr/bin/env python3
"""
Main entry point for Soko-Mushi disk analysis tool.
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Add src to path for development
src_path = Path(__file__).parent.parent.parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

from soko_mushi.gui.main_window import run_app


def main() -> None:
    """Main entry point for the application."""
    try:
        exit_code = run_app()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting Soko-Mushi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
