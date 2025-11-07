#!/bin/bash
# Quick start script for interactive visualizers

echo "=================================="
echo "Interactive Visualizer Quick Start"
echo "=================================="
echo ""

# Check if a file was provided
if [ $# -eq 0 ]; then
    echo "Usage: ./quickstart.sh <path_to_npy_file> [visualizer_type]"
    echo ""
    echo "Visualizer types:"
    echo "  1 or vedo     - Vedo visualizer (default, easiest)"
    echo "  2 or open3d   - Open3D visualizer (high performance)"
    echo "  3 or pygame   - PyGame+ModernGL visualizer (custom shaders)"
    echo ""
    echo "Example:"
    echo "  ./quickstart.sh ../assets/Hound___Attack_470.npy"
    echo "  ./quickstart.sh ../assets/Horse___Walk_123.npy open3d"
    echo ""

    # Show available sample files
    echo "Available sample files in assets/:"
    ls -1 ../assets/*.npy 2>/dev/null | head -5 || echo "  (no .npy files found)"
    echo ""
    exit 1
fi

NPY_FILE="$1"
VIZ_TYPE="${2:-vedo}"

# Check if file exists
if [ ! -f "$NPY_FILE" ]; then
    echo "Error: File not found: $NPY_FILE"
    exit 1
fi

# Determine which visualizer to use
case "$VIZ_TYPE" in
    1|vedo)
        echo "Starting Vedo visualizer..."
        python interactive_visualizer.py "$NPY_FILE"
        ;;
    2|open3d)
        echo "Starting Open3D visualizer..."
        python interactive_visualizer_open3d.py "$NPY_FILE"
        ;;
    3|pygame)
        echo "Starting PyGame+ModernGL visualizer..."
        python interactive_visualizer_pygame.py "$NPY_FILE"
        ;;
    *)
        echo "Error: Unknown visualizer type: $VIZ_TYPE"
        echo "Use: vedo, open3d, or pygame"
        exit 1
        ;;
esac
