#!/bin/bash
# AnyTop Viewer Launcher
# Automatically launches the best available viewer

echo "========================================"
echo "AnyTop Unified Viewer Launcher"
echo "========================================"
echo ""

# Check Python version
PYTHON_CMD="python3"
if ! command -v $PYTHON_CMD &> /dev/null; then
    PYTHON_CMD="python"
fi

if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "Error: Python not found"
    exit 1
fi

# Check PySide6
echo "Checking dependencies..."
$PYTHON_CMD -c "import PySide6" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: PySide6 not installed"
    echo ""
    echo "Install with:"
    echo "  pip install PySide6"
    echo ""
    exit 1
fi

# Check PyVistaQt for full viewer
$PYTHON_CMD -c "import pyvistaqt" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ PyVistaQt found - launching full AnyTop Viewer"
    echo ""
    exec $PYTHON_CMD anytop_viewer.py "$@"
else
    echo "⚠ PyVistaQt not found - launching Simple Viewer"
    echo ""
    echo "For full features, install:"
    echo "  pip install pyvistaqt"
    echo ""
    exec $PYTHON_CMD anytop_viewer_simple.py "$@"
fi
