#!/usr/bin/env python3
"""
Test script for interactive visualizers.
Validates that visualizers can load data and initialize correctly.
"""

import sys
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from data_loaders.truebones.truebones_utils.param_utils import t2m_kinematic_chain


def test_data_loading():
    """Test that we can load .npy files."""
    print("=" * 60)
    print("TEST 1: Data Loading")
    print("=" * 60)

    test_files = [
        'assets/Hound___Attack_470.npy',
        'assets/Ostrich___Attack_581.npy',
        'assets/Scorpion___SlowForward_837.npy',
        'assets/Monkey___B2Attack_574.npy'
    ]

    for test_file in test_files:
        file_path = Path(__file__).parent.parent / test_file
        if not file_path.exists():
            print(f"❌ File not found: {test_file}")
            continue

        try:
            data = np.load(file_path)
            print(f"✓ Loaded {test_file}")
            print(f"  Shape: {data.shape}")

            if len(data.shape) != 3:
                print(f"  ❌ Expected 3D array, got {len(data.shape)}D")
            elif data.shape[2] != 13:
                print(f"  ❌ Expected 13 features, got {data.shape[2]}")
            else:
                print(f"  ✓ Valid shape: ({data.shape[0]} frames, {data.shape[1]} joints, {data.shape[2]} features)")

        except Exception as e:
            print(f"❌ Error loading {test_file}: {e}")

    print()


def test_skeleton_types():
    """Test that skeleton types are available."""
    print("=" * 60)
    print("TEST 2: Skeleton Types")
    print("=" * 60)

    test_types = ['Horse', 'Hound', 'Ostrich', 'Scorpion', 'Monkey']

    for skel_type in test_types:
        if skel_type in t2m_kinematic_chain:
            chains = t2m_kinematic_chain[skel_type]
            print(f"✓ {skel_type}: {len(chains)} kinematic chains")
        else:
            print(f"❌ {skel_type}: Not found in kinematic chain dictionary")

    print(f"\nTotal available skeleton types: {len(t2m_kinematic_chain)}")
    print()


def test_visualizer_initialization():
    """Test that visualizers can be imported and initialized."""
    print("=" * 60)
    print("TEST 3: Visualizer Initialization")
    print("=" * 60)

    # Load sample data
    sample_file = Path(__file__).parent.parent / 'assets' / 'Hound___Attack_470.npy'
    if not sample_file.exists():
        print("❌ Sample file not found for testing")
        return

    motion_data = np.load(sample_file)
    print(f"Using test data: {motion_data.shape}")
    print()

    # Test Vedo visualizer
    try:
        from interactive_visualizer import SkeletonVisualizer
        viz = SkeletonVisualizer(motion_data, skeleton_type='Hound', fps=30)
        print("✓ Vedo visualizer initialized successfully")
        print(f"  - Frames: {viz.n_frames}")
        print(f"  - Joints: {viz.n_joints}")
        print(f"  - Features: {viz.n_features}")
        print(f"  - Kinematic chains: {len(viz.kinematic_chain)}")
    except ImportError as e:
        print(f"⚠ Vedo visualizer: Library not available ({e})")
    except Exception as e:
        print(f"❌ Vedo visualizer: Initialization error - {e}")

    print()

    # Test Open3D visualizer
    try:
        from interactive_visualizer_open3d import SkeletonVisualizerOpen3D
        viz = SkeletonVisualizerOpen3D(motion_data, skeleton_type='Hound', fps=30)
        print("✓ Open3D visualizer initialized successfully")
        print(f"  - Frames: {viz.n_frames}")
        print(f"  - Joints: {viz.n_joints}")
        print(f"  - Features: {viz.n_features}")
        print(f"  - Kinematic chains: {len(viz.kinematic_chain)}")
    except ImportError as e:
        print(f"⚠ Open3D visualizer: Library not available ({e})")
    except Exception as e:
        print(f"❌ Open3D visualizer: Initialization error - {e}")

    print()

    # Test PyGame visualizer
    try:
        from interactive_visualizer_pygame import SkeletonVisualizerPyGame
        viz = SkeletonVisualizerPyGame(motion_data, skeleton_type='Hound', fps=30)
        print("✓ PyGame visualizer initialized successfully")
        print(f"  - Frames: {viz.n_frames}")
        print(f"  - Joints: {viz.n_joints}")
        print(f"  - Features: {viz.n_features}")
        print(f"  - Kinematic chains: {len(viz.kinematic_chain)}")
    except ImportError as e:
        print(f"⚠ PyGame visualizer: Library not available ({e})")
    except Exception as e:
        print(f"❌ PyGame visualizer: Initialization error - {e}")

    print()


def test_position_extraction():
    """Test that position extraction works correctly."""
    print("=" * 60)
    print("TEST 4: Position Extraction")
    print("=" * 60)

    sample_file = Path(__file__).parent.parent / 'assets' / 'Hound___Attack_470.npy'
    if not sample_file.exists():
        print("❌ Sample file not found for testing")
        return

    motion_data = np.load(sample_file)

    # Extract positions (first 3 features)
    positions = motion_data[:, :, :3]
    print(f"✓ Extracted positions: {positions.shape}")

    # Check for NaN or Inf values
    if np.any(np.isnan(positions)):
        print("❌ Found NaN values in positions")
    else:
        print("✓ No NaN values in positions")

    if np.any(np.isinf(positions)):
        print("❌ Found Inf values in positions")
    else:
        print("✓ No Inf values in positions")

    # Check position ranges
    pos_min = np.min(positions, axis=(0, 1))
    pos_max = np.max(positions, axis=(0, 1))
    pos_mean = np.mean(positions, axis=(0, 1))

    print(f"Position ranges:")
    print(f"  X: [{pos_min[0]:.3f}, {pos_max[0]:.3f}] (mean: {pos_mean[0]:.3f})")
    print(f"  Y: [{pos_min[1]:.3f}, {pos_max[1]:.3f}] (mean: {pos_mean[1]:.3f})")
    print(f"  Z: [{pos_min[2]:.3f}, {pos_max[2]:.3f}] (mean: {pos_mean[2]:.3f})")

    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("INTERACTIVE VISUALIZER TEST SUITE")
    print("=" * 60)
    print()

    test_data_loading()
    test_skeleton_types()
    test_position_extraction()
    test_visualizer_initialization()

    print("=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)
    print("\nNote: Visualizers were initialized but not displayed.")
    print("To actually view animations, run the visualizer scripts directly:")
    print("  python interactive_visualizer.py assets/Hound___Attack_470.npy")
    print()


if __name__ == '__main__':
    main()
