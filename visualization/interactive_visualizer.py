#!/usr/bin/env python3
"""
Interactive Skeleton Animation Visualizer
Visualizes skeletal animations from .npy motion files without Blender.

Features:
- Interactive 3D visualization with mouse controls
- Playback controls (play/pause, speed adjustment)
- Frame-by-frame navigation
- Bone and joint rendering
- Support for all skeleton types in the dataset
"""

import numpy as np
import argparse
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from data_loaders.truebones.truebones_utils.param_utils import t2m_kinematic_chain
from utils.rotation_conversions import rotation_6d_to_matrix_np

try:
    from vedo import Plotter, Sphere, Cylinder, Text2D, show
    VEDO_AVAILABLE = True
except ImportError:
    VEDO_AVAILABLE = False
    print("Warning: Vedo not available. Install with: pip install vedo")


class SkeletonVisualizer:
    """Interactive skeleton visualizer using Vedo library."""

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
        self.frame_delay = 1000 / fps  # milliseconds

        self.n_frames, self.n_joints, self.n_features = motion_data.shape
        self.current_frame = 0
        self.is_playing = False
        self.play_speed = 1.0

        # Get kinematic chain for skeleton type
        self.kinematic_chain = self._get_kinematic_chain()

        # Extract joint positions from motion data
        self.joint_positions = self._extract_positions()

        # Initialize Vedo plotter
        if VEDO_AVAILABLE:
            self.plotter = Plotter(title=f"{skeleton_type} Animation Viewer",
                                   axes=1, interactive=True)
            self.actors = {'joints': [], 'bones': [], 'text': None}

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
        # Motion features: [0:3] RIC position, [3:9] 6D rotation, [9:12] velocity, [12] contact
        positions = self.motion_data[:, :, :3]  # Extract RIC positions

        # Center the skeleton for better visualization
        # Find root joint (typically joint 0)
        root_positions = positions[:, 0:1, :]
        positions = positions - root_positions  # Make root relative

        return positions

    def _create_joint(self, position, radius=0.05):
        """Create a sphere for a joint."""
        return Sphere(position, r=radius, c='red')

    def _create_bone(self, start_pos, end_pos, radius=0.02):
        """Create a cylinder for a bone."""
        return Cylinder(start_pos, end_pos, r=radius, c='lightblue')

    def _update_frame(self, frame_idx):
        """Update visualization to show a specific frame."""
        self.current_frame = frame_idx % self.n_frames

        # Remove old actors
        if self.actors['joints']:
            self.plotter.remove(self.actors['joints'])
            self.actors['joints'] = []
        if self.actors['bones']:
            self.plotter.remove(self.actors['bones'])
            self.actors['bones'] = []
        if self.actors['text']:
            self.plotter.remove(self.actors['text'])

        # Get positions for current frame
        positions = self.joint_positions[self.current_frame]

        # Create bones (connections between joints)
        for chain in self.kinematic_chain:
            if len(chain) < 2:
                continue
            for i in range(len(chain) - 1):
                j1, j2 = chain[i], chain[i+1]
                if j1 < self.n_joints and j2 < self.n_joints:
                    bone = self._create_bone(positions[j1], positions[j2])
                    self.actors['bones'].append(bone)
                    self.plotter.add(bone)

        # Create joints (spheres at each joint location)
        for i, pos in enumerate(positions):
            joint = self._create_joint(pos)
            self.actors['joints'].append(joint)
            self.plotter.add(joint)

        # Add frame counter
        text = Text2D(f"Frame: {self.current_frame}/{self.n_frames-1} | "
                      f"Speed: {self.play_speed}x | "
                      f"{'Playing' if self.is_playing else 'Paused'}\n"
                      f"Controls: SPACE=play/pause, ←/→=prev/next frame, +/-=speed",
                      pos='bottom-left', c='white', s=0.8)
        self.actors['text'] = text
        self.plotter.add(text)

    def _on_key_press(self, evt):
        """Handle keyboard events."""
        key = evt.keypress

        if key == 'space' or key == ' ':
            # Toggle play/pause
            self.is_playing = not self.is_playing
        elif key == 'Right':
            # Next frame
            self.current_frame = (self.current_frame + 1) % self.n_frames
            self._update_frame(self.current_frame)
        elif key == 'Left':
            # Previous frame
            self.current_frame = (self.current_frame - 1) % self.n_frames
            self._update_frame(self.current_frame)
        elif key == 'plus' or key == '+' or key == '=':
            # Increase speed
            self.play_speed = min(self.play_speed * 1.5, 10.0)
            self._update_frame(self.current_frame)
        elif key == 'minus' or key == '-':
            # Decrease speed
            self.play_speed = max(self.play_speed / 1.5, 0.1)
            self._update_frame(self.current_frame)
        elif key == 'r':
            # Reset to first frame
            self.current_frame = 0
            self._update_frame(self.current_frame)
        elif key == 'q' or key == 'Escape':
            # Quit
            self.plotter.close()

    def _on_timer(self, evt):
        """Handle timer events for animation playback."""
        if self.is_playing:
            frames_to_advance = max(1, int(self.play_speed))
            self.current_frame = (self.current_frame + frames_to_advance) % self.n_frames
            self._update_frame(self.current_frame)

    def show(self):
        """Display the interactive visualization."""
        if not VEDO_AVAILABLE:
            print("Error: Vedo library not available. Install with: pip install vedo")
            return

        # Set up initial frame
        self._update_frame(0)

        # Add event handlers
        self.plotter.add_callback('KeyPress', self._on_key_press)
        self.plotter.add_callback('timer', self._on_timer)

        # Start timer for animation
        self.plotter.timer_callback('create', dt=int(self.frame_delay))

        # Set camera position
        self.plotter.show(viewup='y')


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
        description='Interactive skeleton animation visualizer')
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
    visualizer = SkeletonVisualizer(motion_data, skeleton_type, args.fps)
    visualizer.show()


if __name__ == '__main__':
    main()
