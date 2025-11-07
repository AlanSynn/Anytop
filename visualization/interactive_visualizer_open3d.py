#!/usr/bin/env python3
"""
Interactive Skeleton Animation Visualizer using Open3D
Visualizes skeletal animations from .npy motion files with Open3D backend.

Features:
- High-performance 3D visualization
- Interactive camera controls
- Animation playback with controls
- Bone and joint rendering with custom colors
"""

import numpy as np
import argparse
from pathlib import Path
import sys
import time

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from data_loaders.truebones.truebones_utils.param_utils import t2m_kinematic_chain

try:
    import open3d as o3d
    OPEN3D_AVAILABLE = True
except ImportError:
    OPEN3D_AVAILABLE = False
    print("Warning: Open3D not available. Install with: pip install open3d")


class SkeletonVisualizerOpen3D:
    """Interactive skeleton visualizer using Open3D library."""

    def __init__(self, motion_data, skeleton_type='Horse', fps=30):
        """
        Initialize visualizer.

        Args:
            motion_data: numpy array of shape (frames, joints, 13)
            skeleton_type: type of skeleton (e.g., 'Horse', 'Ostrich')
            fps: frames per second for playback
        """
        self.motion_data = motion_data
        self.skeleton_type = skeleton_type
        self.fps = fps
        self.frame_delay = 1.0 / fps

        self.n_frames, self.n_joints, self.n_features = motion_data.shape
        self.current_frame = 0
        self.is_playing = False
        self.play_speed = 1.0
        self.last_update_time = time.time()

        # Get kinematic chain for skeleton type
        self.kinematic_chain = self._get_kinematic_chain()

        # Extract joint positions from motion data
        self.joint_positions = self._extract_positions()

        # Colors
        self.bone_color = [0.2, 0.6, 0.9]  # Light blue
        self.joint_color = [0.9, 0.2, 0.2]  # Red

        # Geometry containers
        self.geometries = []

    def _get_kinematic_chain(self):
        """Get kinematic chain for skeleton type."""
        try:
            return t2m_kinematic_chain[self.skeleton_type]
        except KeyError:
            print(f"Warning: Unknown skeleton type '{self.skeleton_type}'")
            print(f"Available types: {list(t2m_kinematic_chain.keys())}")
            # Return a simple chain as fallback
            return [[i, i+1] for i in range(self.n_joints-1)]

    def _extract_positions(self):
        """Extract 3D joint positions from motion features."""
        # Motion features: [0:3] RIC position
        positions = self.motion_data[:, :, :3]

        # Center the skeleton
        root_positions = positions[:, 0:1, :]
        positions = positions - root_positions

        return positions

    def _create_sphere(self, center, radius=0.05, color=None):
        """Create a sphere mesh for a joint."""
        if color is None:
            color = self.joint_color

        mesh = o3d.geometry.TriangleMesh.create_sphere(radius=radius)
        mesh.translate(center)
        mesh.paint_uniform_color(color)
        mesh.compute_vertex_normals()
        return mesh

    def _create_cylinder(self, start_pos, end_pos, radius=0.02, color=None):
        """Create a cylinder mesh for a bone."""
        if color is None:
            color = self.bone_color

        # Calculate cylinder parameters
        direction = end_pos - start_pos
        length = np.linalg.norm(direction)

        if length < 1e-6:
            return None

        # Create cylinder along Z-axis
        cylinder = o3d.geometry.TriangleMesh.create_cylinder(
            radius=radius, height=length)

        # Compute rotation to align cylinder with bone direction
        z_axis = np.array([0, 0, 1])
        direction_normalized = direction / length

        # Rotation axis (cross product)
        rotation_axis = np.cross(z_axis, direction_normalized)
        rotation_axis_norm = np.linalg.norm(rotation_axis)

        if rotation_axis_norm > 1e-6:
            rotation_axis = rotation_axis / rotation_axis_norm
            # Rotation angle
            angle = np.arccos(np.clip(np.dot(z_axis, direction_normalized), -1.0, 1.0))
            # Create rotation matrix
            rotation_matrix = o3d.geometry.get_rotation_matrix_from_axis_angle(
                rotation_axis * angle)
        else:
            # Cylinder already aligned or opposite
            if np.dot(z_axis, direction_normalized) < 0:
                rotation_matrix = o3d.geometry.get_rotation_matrix_from_axis_angle(
                    np.array([1, 0, 0]) * np.pi)
            else:
                rotation_matrix = np.eye(3)

        # Apply rotation and translation
        cylinder.rotate(rotation_matrix, center=[0, 0, 0])
        cylinder.translate(start_pos + direction / 2)

        cylinder.paint_uniform_color(color)
        cylinder.compute_vertex_normals()
        return cylinder

    def _create_frame_geometries(self, frame_idx):
        """Create all geometries for a specific frame."""
        geometries = []
        positions = self.joint_positions[frame_idx]

        # Create bones
        for chain in self.kinematic_chain:
            if len(chain) < 2:
                continue
            for i in range(len(chain) - 1):
                j1, j2 = chain[i], chain[i + 1]
                if j1 < self.n_joints and j2 < self.n_joints:
                    cylinder = self._create_cylinder(positions[j1], positions[j2])
                    if cylinder is not None:
                        geometries.append(cylinder)

        # Create joints
        for pos in positions:
            sphere = self._create_sphere(pos)
            geometries.append(sphere)

        # Create ground plane for reference
        ground = o3d.geometry.TriangleMesh.create_box(
            width=10, height=0.01, depth=10)
        ground.translate([-5, -0.5, -5])
        ground.paint_uniform_color([0.5, 0.5, 0.5])
        ground.compute_vertex_normals()
        geometries.append(ground)

        return geometries

    def _update_visualization(self, vis):
        """Update callback for animation."""
        current_time = time.time()
        elapsed = current_time - self.last_update_time

        if self.is_playing and elapsed >= (self.frame_delay / self.play_speed):
            # Advance frame
            self.current_frame = (self.current_frame + 1) % self.n_frames
            self.last_update_time = current_time

            # Clear previous geometries
            vis.clear_geometries()

            # Create new geometries for current frame
            self.geometries = self._create_frame_geometries(self.current_frame)

            # Add to visualizer
            for geom in self.geometries:
                vis.add_geometry(geom, reset_bounding_box=False)

        return False

    def show(self):
        """Display the interactive visualization."""
        if not OPEN3D_AVAILABLE:
            print("Error: Open3D library not available. Install with: pip install open3d")
            return

        # Create visualizer
        vis = o3d.visualization.VisualizerWithKeyCallback()
        vis.create_window(window_name=f"{self.skeleton_type} Animation Viewer",
                          width=1280, height=720)

        # Add initial geometries
        self.geometries = self._create_frame_geometries(0)
        for geom in self.geometries:
            vis.add_geometry(geom)

        # Configure rendering options
        opt = vis.get_render_option()
        opt.background_color = np.asarray([0.1, 0.1, 0.1])
        opt.light_on = True
        opt.mesh_show_back_face = True

        # Key callbacks
        def toggle_play(vis):
            self.is_playing = not self.is_playing
            print(f"{'Playing' if self.is_playing else 'Paused'}")
            return False

        def next_frame(vis):
            self.current_frame = (self.current_frame + 1) % self.n_frames
            print(f"Frame: {self.current_frame}/{self.n_frames-1}")
            vis.clear_geometries()
            self.geometries = self._create_frame_geometries(self.current_frame)
            for geom in self.geometries:
                vis.add_geometry(geom, reset_bounding_box=False)
            return False

        def prev_frame(vis):
            self.current_frame = (self.current_frame - 1) % self.n_frames
            print(f"Frame: {self.current_frame}/{self.n_frames-1}")
            vis.clear_geometries()
            self.geometries = self._create_frame_geometries(self.current_frame)
            for geom in self.geometries:
                vis.add_geometry(geom, reset_bounding_box=False)
            return False

        def increase_speed(vis):
            self.play_speed = min(self.play_speed * 1.5, 10.0)
            print(f"Speed: {self.play_speed:.2f}x")
            return False

        def decrease_speed(vis):
            self.play_speed = max(self.play_speed / 1.5, 0.1)
            print(f"Speed: {self.play_speed:.2f}x")
            return False

        def reset_frame(vis):
            self.current_frame = 0
            print(f"Reset to frame 0")
            vis.clear_geometries()
            self.geometries = self._create_frame_geometries(0)
            for geom in self.geometries:
                vis.add_geometry(geom, reset_bounding_box=False)
            return False

        # Register key callbacks
        vis.register_key_callback(32, toggle_play)  # Space
        vis.register_key_callback(262, next_frame)  # Right arrow
        vis.register_key_callback(263, prev_frame)  # Left arrow
        vis.register_key_callback(61, increase_speed)  # + or =
        vis.register_key_callback(45, decrease_speed)  # -
        vis.register_key_callback(82, reset_frame)  # R

        print("\n=== Controls ===")
        print("SPACE: Play/Pause")
        print("→/←: Next/Previous frame")
        print("+/-: Increase/Decrease speed")
        print("R: Reset to first frame")
        print("Mouse: Rotate/Pan/Zoom camera")
        print("===============\n")

        # Register animation callback
        vis.register_animation_callback(self._update_visualization)

        # Run visualizer
        vis.run()
        vis.destroy_window()


def load_motion_from_npy(npy_path):
    """Load motion data from .npy file."""
    data = np.load(npy_path)
    print(f"Loaded motion data: {data.shape}")
    return data


def infer_skeleton_type_from_path(npy_path):
    """Try to infer skeleton type from file path."""
    path = Path(npy_path)
    filename = path.stem

    # Common skeleton types in the dataset
    skeleton_types = list(t2m_kinematic_chain.keys())

    # Try to match filename to skeleton type
    for skel_type in skeleton_types:
        if skel_type.lower() in filename.lower():
            return skel_type

    # Default to Horse if not found
    return 'Horse'


def main():
    parser = argparse.ArgumentParser(
        description='Interactive skeleton animation visualizer (Open3D)')
    parser.add_argument('motion_file', type=str,
                        help='Path to .npy motion file')
    parser.add_argument('--skeleton', type=str, default=None,
                        help='Skeleton type (e.g., Horse, Ostrich). Auto-detected if not provided.')
    parser.add_argument('--fps', type=int, default=30,
                        help='Frames per second for playback (default: 30)')

    args = parser.parse_args()

    # Load motion data
    motion_data = load_motion_from_npy(args.motion_file)

    # Infer or use provided skeleton type
    skeleton_type = args.skeleton
    if skeleton_type is None:
        skeleton_type = infer_skeleton_type_from_path(args.motion_file)
        print(f"Auto-detected skeleton type: {skeleton_type}")

    # Create and show visualizer
    visualizer = SkeletonVisualizerOpen3D(motion_data, skeleton_type, args.fps)
    visualizer.show()


if __name__ == '__main__':
    main()
