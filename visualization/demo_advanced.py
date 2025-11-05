#!/usr/bin/env python3
"""
Demo script for advanced visualizers.

This demonstrates the advanced visualizers even without TrueBones models
by creating simple procedural meshes.

Usage:
    python demo_advanced.py --motion path/to/animation.npy
"""

import numpy as np
import argparse
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

try:
    import pyvista as pv
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False
    print("PyVista not available. Install with: pip install pyvista")


def create_procedural_animal_mesh(skeleton_type='Horse'):
    """
    Create a simple procedural mesh for demonstration.

    This creates a basic shape that can be animated with skeleton motion.
    In practice, you'd use actual 3D models from TrueBones.
    """
    if not PYVISTA_AVAILABLE:
        return None

    print(f"Creating procedural mesh for {skeleton_type}...")

    if skeleton_type in ['Horse', 'Bear', 'Lion', 'Tiger', 'Dog', 'Cat']:
        # Quadruped body
        # Main body (elongated box)
        body = pv.Cube(center=(0, 0.5, 0), x_length=2.0, y_length=0.8, z_length=0.6)

        # Neck
        neck = pv.Cylinder(center=(0.8, 0.7, 0), direction=(0.5, 0.3, 0),
                          radius=0.2, height=0.6)

        # Head
        head = pv.Sphere(center=(1.3, 1.0, 0), radius=0.3)

        # Legs (4 cylinders)
        leg_fl = pv.Cylinder(center=(0.6, 0.25, 0.3), direction=(0, -1, 0),
                            radius=0.1, height=0.5)
        leg_fr = pv.Cylinder(center=(0.6, 0.25, -0.3), direction=(0, -1, 0),
                            radius=0.1, height=0.5)
        leg_bl = pv.Cylinder(center=(-0.6, 0.25, 0.3), direction=(0, -1, 0),
                            radius=0.1, height=0.5)
        leg_br = pv.Cylinder(center=(-0.6, 0.25, -0.3), direction=(0, -1, 0),
                            radius=0.1, height=0.5)

        # Combine all parts
        mesh = body + neck + head + leg_fl + leg_fr + leg_bl + leg_br

    elif skeleton_type in ['Ostrich', 'Flamingo', 'Chicken']:
        # Biped bird body
        # Body
        body = pv.Sphere(center=(0, 0.8, 0), radius=0.4)

        # Neck
        neck = pv.Cylinder(center=(0, 1.3, 0), direction=(0, 1, 0),
                          radius=0.1, height=0.6)

        # Head
        head = pv.Sphere(center=(0, 1.8, 0), radius=0.15)

        # Legs
        leg_l = pv.Cylinder(center=(0.15, 0.4, 0), direction=(0, -1, 0),
                           radius=0.08, height=0.8)
        leg_r = pv.Cylinder(center=(-0.15, 0.4, 0), direction=(0, -1, 0),
                           radius=0.08, height=0.8)

        mesh = body + neck + head + leg_l + leg_r

    elif skeleton_type in ['Spider', 'Scorpion', 'Crab']:
        # Multi-legged creature
        # Body
        body = pv.Sphere(center=(0, 0.2, 0), radius=0.3)

        # Legs (8 for spider/scorpion, 6 for others)
        mesh = body
        n_legs = 8 if skeleton_type in ['Spider', 'Scorpion'] else 6

        angle_step = 2 * np.pi / n_legs
        for i in range(n_legs):
            angle = i * angle_step
            x = 0.3 * np.cos(angle)
            z = 0.3 * np.sin(angle)
            leg = pv.Cylinder(center=(x, 0.1, z),
                            direction=(np.cos(angle), -0.5, np.sin(angle)),
                            radius=0.05, height=0.4)
            mesh = mesh + leg

    else:
        # Default: simple sphere
        mesh = pv.Sphere(radius=0.5)

    # Apply smooth shading
    mesh = mesh.clean()
    mesh.compute_normals(inplace=True)

    print(f"Created mesh with {mesh.n_points} vertices, {mesh.n_cells} cells")

    return mesh


def create_simple_texture(size=(512, 512), color='tan'):
    """Create a simple colored texture."""
    from PIL import Image

    # Color map
    colors = {
        'tan': (210, 180, 140),
        'brown': (139, 90, 43),
        'grey': (128, 128, 128),
        'white': (240, 240, 240),
    }

    rgb = colors.get(color, (210, 180, 140))

    # Create colored image with some variation
    img = np.random.randint(rgb[0]-20, rgb[0]+20, (*size, 3), dtype=np.uint8)
    img[:, :, 0] = np.clip(img[:, :, 0], 0, 255)

    return Image.fromarray(img)


def demo_visualization(motion_file, skeleton_type='Horse'):
    """Run demo visualization with procedural mesh."""
    if not PYVISTA_AVAILABLE:
        print("Error: PyVista required for demo")
        return

    # Import the visualizer
    from pyvista_visualizer import PyVistaVisualizer

    # Create visualizer
    viz = PyVistaVisualizer(skeleton_type=skeleton_type, fps=30)

    # Create procedural mesh
    mesh = create_procedural_animal_mesh(skeleton_type)
    if mesh:
        viz.meshes.append(mesh)
        viz.rest_vertices.append(mesh.points.copy())
        viz.bone_weights.append(None)
        viz.bone_indices.append(None)

        # Create and apply simple texture
        try:
            from PIL import Image
            texture = create_simple_texture(color='tan')
            # Save temporarily and load with PyVista
            texture.save('/tmp/demo_texture.png')
            pv_texture = pv.read_texture('/tmp/demo_texture.png')
            viz.textures.append(pv_texture)
            mesh.texture_map_to_plane(inplace=True)
        except:
            viz.textures.append(None)

    # Load motion
    viz.load_motion_npy(motion_file)

    # Display info
    print("\n" + "="*50)
    print("DEMO: Advanced Visualizer with Procedural Mesh")
    print("="*50)
    print(f"Skeleton Type: {skeleton_type}")
    print(f"Mesh Vertices: {len(mesh.points) if mesh else 0}")
    print(f"Animation Frames: {viz.n_frames}")
    print(f"FPS: {viz.fps}")
    print()
    print("NOTE: This is a DEMO with a simple procedural mesh.")
    print("For real 3D models, use TrueBones FBX Zoo:")
    print("  https://truebones.gumroad.com/l/skZMC")
    print()
    print("With TrueBones, you'll get:")
    print("  - Professional 3D animal models")
    print("  - High-quality textures")
    print("  - Proper skeletal rigging")
    print("  - 75+ animals to choose from")
    print("="*50)
    print()

    # Run visualizer
    viz.run()


def main():
    parser = argparse.ArgumentParser(
        description='Demo of advanced visualizer with procedural mesh')
    parser.add_argument('--motion', '--npy', type=str, required=True,
                       help='Path to NPY motion file')
    parser.add_argument('--skeleton', type=str, default='Horse',
                       help='Skeleton type (default: Horse)')

    args = parser.parse_args()

    # Check if motion file exists
    motion_path = Path(args.motion)
    if not motion_path.exists():
        print(f"Error: Motion file not found: {args.motion}")
        print("\nAvailable sample files:")
        sample_dir = Path(__file__).parent.parent / 'assets'
        if sample_dir.exists():
            for npy_file in sample_dir.glob('*.npy'):
                print(f"  {npy_file}")
        return

    # Run demo
    demo_visualization(args.motion, args.skeleton)


if __name__ == '__main__':
    main()
