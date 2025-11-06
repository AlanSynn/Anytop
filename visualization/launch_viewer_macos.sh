#!/bin/bash
# AnyTop Viewer Launcher for macOS
# Automatically sets up environment and launches best available viewer

# macOS-specific environment variables for better compatibility
export QT_AUTO_SCREEN_SCALE_FACTOR=1
export QT_ENABLE_HIGHDPI_SCALING=1
export VTK_USE_COCOA=1

echo "========================================"
echo "AnyTop Viewer - macOS Launcher"
echo "========================================"
echo ""

# Detect Python
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found"
    echo ""
    echo "Install Python with:"
    echo "  brew install python@3.10"
    exit 1
fi

echo "Using: $PYTHON_CMD $($PYTHON_CMD --version 2>&1)"
echo ""

# Check dependencies
echo "Checking dependencies..."
HAS_PYSIDE6=false
HAS_PYVISTA=false
HAS_MATPLOTLIB=false

$PYTHON_CMD -c "import PySide6" 2>/dev/null && HAS_PYSIDE6=true
$PYTHON_CMD -c "import pyvistaqt" 2>/dev/null && HAS_PYVISTA=true
$PYTHON_CMD -c "import matplotlib" 2>/dev/null && HAS_MATPLOTLIB=true

if [ "$HAS_PYSIDE6" = false ]; then
    echo "❌ PySide6 not found"
    echo ""
    echo "Install with:"
    echo "  pip3 install PySide6"
    echo ""
    echo "Or run: ./install_macos.sh"
    exit 1
fi

echo "✓ PySide6 found"

# Determine which viewer to launch
VIEWER=""

if [ "$HAS_PYVISTA" = true ]; then
    echo "✓ PyVistaQt found"
    echo ""
    echo "Launching full AnyTop Viewer..."
    echo "(macOS optimized version with 3D mesh support)"
    echo ""
    VIEWER="anytop_viewer.py"
elif [ "$HAS_MATPLOTLIB" = true ]; then
    echo "⚠ PyVistaQt not found, using Matplotlib"
    echo "✓ Matplotlib found"
    echo ""
    echo "Launching macOS Optimized Viewer..."
    echo "(skeleton-only, better performance on Intel Mac)"
    echo ""
    VIEWER="anytop_viewer_macos.py"
else
    echo "❌ Neither PyVistaQt nor Matplotlib found"
    echo ""
    echo "Install at least Matplotlib:"
    echo "  pip3 install matplotlib"
    echo ""
    echo "Or run: ./install_macos.sh"
    exit 1
fi

# Launch viewer with macOS optimizations
exec $PYTHON_CMD "$VIEWER" "$@"
