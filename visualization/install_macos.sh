#!/bin/bash
# AnyTop Viewer - macOS Installation Script
# Optimized for Intel Mac compatibility

set -e  # Exit on error

echo "=========================================="
echo "AnyTop Viewer - macOS Installation"
echo "=========================================="
echo ""

# Detect system
MACOS_VERSION=$(sw_vers -productVersion)
ARCHITECTURE=$(uname -m)

echo "macOS Version: $MACOS_VERSION"
echo "Architecture: $ARCHITECTURE"
echo ""

# Check if on Intel Mac
if [ "$ARCHITECTURE" = "x86_64" ]; then
    echo "✓ Intel Mac detected"
    echo "  Using Intel-optimized installation"
elif [ "$ARCHITECTURE" = "arm64" ]; then
    echo "✓ Apple Silicon Mac detected"
    echo "  Installation will work but consider native ARM Python"
fi

echo ""

# Check Homebrew
if ! command -v brew &> /dev/null; then
    echo "⚠ Homebrew not found"
    echo ""
    echo "Install Homebrew first:"
    echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    echo ""
    read -p "Install Homebrew now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        echo "Please install Homebrew and try again"
        exit 1
    fi
fi

echo "✓ Homebrew found"
echo ""

# Check Python
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$($PYTHON_CMD --version | cut -d' ' -f2)
    echo "✓ Python found: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$($PYTHON_CMD --version | cut -d' ' -f2)
    echo "✓ Python found: $PYTHON_VERSION"
else
    echo "⚠ Python not found"
    echo ""
    echo "Installing Python via Homebrew..."
    brew install python@3.10
    PYTHON_CMD="python3"
fi

# Verify Python version
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "❌ Python 3.8+ required (found $PYTHON_MAJOR.$PYTHON_MINOR)"
    echo ""
    echo "Installing Python 3.10 via Homebrew..."
    brew install python@3.10
    PYTHON_CMD="/usr/local/bin/python3.10"
fi

echo ""
echo "Using Python: $PYTHON_CMD"
echo ""

# Choose installation method
echo "Choose installation method:"
echo "  1) Minimal (PySide6 + Matplotlib) - RECOMMENDED for Intel Mac"
echo "  2) Full (includes PyVista for 3D meshes)"
echo "  3) Use Conda (most reliable, requires Miniconda)"
echo ""

read -p "Select option (1/2/3): " -n 1 -r
echo ""
echo ""

case $REPLY in
    1)
        echo "Installing minimal dependencies..."
        echo ""
        $PYTHON_CMD -m pip install --user --upgrade pip
        $PYTHON_CMD -m pip install --user PySide6 numpy matplotlib
        echo ""
        echo "✓ Minimal installation complete"
        echo ""
        echo "Launch with:"
        echo "  $PYTHON_CMD anytop_viewer_macos.py"
        echo "  or"
        echo "  $PYTHON_CMD anytop_viewer_simple.py"
        ;;

    2)
        echo "Installing full dependencies..."
        echo ""
        $PYTHON_CMD -m pip install --user --upgrade pip

        # Install with specific versions known to work on macOS
        echo "Installing PySide6..."
        $PYTHON_CMD -m pip install --user PySide6>=6.5.0

        echo "Installing NumPy and Matplotlib..."
        $PYTHON_CMD -m pip install --user numpy matplotlib

        echo "Installing PyVista (this may take a while)..."
        # Use specific VTK version for Intel Mac compatibility
        $PYTHON_CMD -m pip install --user vtk==9.2.6
        $PYTHON_CMD -m pip install --user pyvista==0.42.0

        echo "Installing PyVistaQt..."
        $PYTHON_CMD -m pip install --user pyvistaqt==0.11.0

        echo ""
        echo "✓ Full installation complete"
        echo ""
        echo "Launch with:"
        echo "  $PYTHON_CMD anytop_viewer.py        # Full features"
        echo "  $PYTHON_CMD anytop_viewer_macos.py  # Optimized"
        ;;

    3)
        echo "Setting up Conda environment..."
        echo ""

        # Check if conda is installed
        if ! command -v conda &> /dev/null; then
            echo "⚠ Conda not found"
            echo ""
            echo "Install Miniconda first:"
            echo "  brew install --cask miniconda"
            echo ""
            echo "Then run this script again"
            exit 1
        fi

        # Create environment
        echo "Creating 'anytop' conda environment..."
        conda create -n anytop python=3.10 -y

        echo "Installing packages..."
        conda activate anytop
        conda install -c conda-forge pyside6 numpy matplotlib pyvista pyvistaqt -y

        echo ""
        echo "✓ Conda environment created"
        echo ""
        echo "Activate with:"
        echo "  conda activate anytop"
        echo ""
        echo "Then launch with:"
        echo "  python anytop_viewer.py"
        ;;

    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""

# Test installation
echo "Testing installation..."
echo ""

$PYTHON_CMD -c "from PySide6.QtWidgets import QApplication; print('✓ PySide6: OK')" 2>&1 || echo "❌ PySide6: Failed"
$PYTHON_CMD -c "import matplotlib; print('✓ Matplotlib: OK')" 2>&1 || echo "❌ Matplotlib: Failed"
$PYTHON_CMD -c "import numpy; print('✓ NumPy: OK')" 2>&1 || echo "❌ NumPy: Failed"

if [ "$REPLY" = "2" ]; then
    $PYTHON_CMD -c "import pyvista; print('✓ PyVista: OK')" 2>&1 || echo "⚠ PyVista: Failed (not critical)"
    $PYTHON_CMD -c "import pyvistaqt; print('✓ PyVistaQt: OK')" 2>&1 || echo "⚠ PyVistaQt: Failed (not critical)"
fi

echo ""
echo "Next steps:"
echo "  1. cd to visualization directory"
echo "  2. Run: $PYTHON_CMD anytop_viewer_macos.py"
echo "  3. Load a .npy motion file"
echo "  4. Enjoy!"
echo ""
echo "For troubleshooting, see MACOS_SETUP.md"
echo ""
