#!/usr/bin/env python3
"""
AnyTop Viewer Launcher

Automatically detects available dependencies and launches the best viewer.
"""

import sys
import subprocess
from pathlib import Path


def check_module(module_name):
    """Check if a Python module is available."""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def main():
    print("=" * 50)
    print("AnyTop Unified Viewer Launcher")
    print("=" * 50)
    print()

    # Check basic requirements
    print("Checking dependencies...")

    if not check_module('PySide6'):
        print("❌ PySide6 not found")
        print()
        print("Install with:")
        print("  pip install PySide6")
        print()
        return 1

    print("✓ PySide6 found")

    # Determine which viewer to use
    if check_module('pyvistaqt'):
        print("✓ PyVistaQt found")
        print()
        print("Launching full AnyTop Viewer with 3D mesh support...")
        print()

        viewer_script = Path(__file__).parent / 'anytop_viewer.py'
        subprocess.run([sys.executable, str(viewer_script)] + sys.argv[1:])

    elif check_module('matplotlib'):
        print("⚠ PyVistaQt not found, using Matplotlib fallback")
        print()
        print("For full features including mesh support, install:")
        print("  pip install pyvistaqt")
        print()
        print("Launching Simple Viewer (skeleton-only)...")
        print()

        viewer_script = Path(__file__).parent / 'anytop_viewer_simple.py'
        subprocess.run([sys.executable, str(viewer_script)] + sys.argv[1:])

    else:
        print("❌ Neither PyVistaQt nor Matplotlib found")
        print()
        print("Install one of:")
        print("  pip install pyvistaqt          # For full features")
        print("  pip install matplotlib         # For simple viewer")
        print()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
