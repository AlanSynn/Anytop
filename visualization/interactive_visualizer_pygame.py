#!/usr/bin/env python3
"""
Interactive Skeleton Animation Visualizer using PyGame + ModernGL
Low-level OpenGL visualization with full control over rendering.

Features:
- Direct OpenGL rendering for maximum performance
- Custom shaders for bone and joint rendering
- Full camera control
- Animation playback system
"""

import numpy as np
import argparse
from pathlib import Path
import sys
import time
import math

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from data_loaders.truebones.truebones_utils.param_utils import t2m_kinematic_chain

try:
    import pygame
    from pygame.locals import *
    import moderngl
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: PyGame/ModernGL not available. Install with: pip install pygame moderngl")


# Vertex shader
VERTEX_SHADER = """
#version 330

uniform mat4 mvp;

in vec3 in_position;
in vec3 in_color;

out vec3 v_color;

void main() {
    gl_Position = mvp * vec4(in_position, 1.0);
    v_color = in_color;
}
"""

# Fragment shader
FRAGMENT_SHADER = """
#version 330

in vec3 v_color;
out vec4 fragColor;

void main() {
    fragColor = vec4(v_color, 1.0);
}
"""


class Camera:
    """Simple orbital camera for 3D visualization."""

    def __init__(self):
        self.distance = 5.0
        self.azimuth = 45.0  # degrees
        self.elevation = 30.0  # degrees
        self.target = np.array([0.0, 0.0, 0.0])
        self.fov = 60.0
        self.near = 0.1
        self.far = 100.0

    def get_view_matrix(self):
        """Calculate view matrix."""
        # Convert angles to radians
        azimuth_rad = math.radians(self.azimuth)
        elevation_rad = math.radians(self.elevation)

        # Calculate camera position
        x = self.distance * math.cos(elevation_rad) * math.cos(azimuth_rad)
        y = self.distance * math.sin(elevation_rad)
        z = self.distance * math.cos(elevation_rad) * math.sin(azimuth_rad)

        eye = self.target + np.array([x, y, z])
        up = np.array([0.0, 1.0, 0.0])

        return look_at(eye, self.target, up)

    def get_projection_matrix(self, aspect_ratio):
        """Calculate projection matrix."""
        return perspective(self.fov, aspect_ratio, self.near, self.far)


def look_at(eye, target, up):
    """Create a look-at view matrix."""
    f = target - eye
    f = f / np.linalg.norm(f)

    s = np.cross(f, up)
    s = s / np.linalg.norm(s)

    u = np.cross(s, f)

    result = np.identity(4, dtype=np.float32)
    result[0, 0:3] = s
    result[1, 0:3] = u
    result[2, 0:3] = -f
    result[3, 0:3] = [-np.dot(s, eye), -np.dot(u, eye), np.dot(f, eye)]

    return result.T


def perspective(fov, aspect, near, far):
    """Create a perspective projection matrix."""
    f = 1.0 / math.tan(math.radians(fov) / 2.0)
    result = np.zeros((4, 4), dtype=np.float32)

    result[0, 0] = f / aspect
    result[1, 1] = f
    result[2, 2] = (far + near) / (near - far)
    result[2, 3] = (2.0 * far * near) / (near - far)
    result[3, 2] = -1.0

    return result


class SkeletonVisualizerPyGame:
    """Interactive skeleton visualizer using PyGame + ModernGL."""

    def __init__(self, motion_data, skeleton_type='Horse', fps=30):
        """Initialize visualizer."""
        self.motion_data = motion_data
        self.skeleton_type = skeleton_type
        self.fps = fps
        self.frame_delay = 1.0 / fps

        self.n_frames, self.n_joints, self.n_features = motion_data.shape
        self.current_frame = 0
        self.is_playing = False
        self.play_speed = 1.0
        self.last_update_time = time.time()

        # Get kinematic chain
        self.kinematic_chain = self._get_kinematic_chain()

        # Extract positions
        self.joint_positions = self._extract_positions()

        # Initialize PyGame and OpenGL
        self.width = 1280
        self.height = 720
        self.camera = Camera()

        # Mouse state
        self.mouse_down = False
        self.last_mouse_pos = None

    def _get_kinematic_chain(self):
        """Get kinematic chain for skeleton type."""
        try:
            return t2m_kinematic_chain[self.skeleton_type]
        except KeyError:
            print(f"Warning: Unknown skeleton type '{self.skeleton_type}'")
            return [[i, i+1] for i in range(self.n_joints-1)]

    def _extract_positions(self):
        """Extract 3D joint positions."""
        positions = self.motion_data[:, :, :3]
        root_positions = positions[:, 0:1, :]
        positions = positions - root_positions
        return positions

    def _create_sphere_vertices(self, center, radius=0.05, segments=16):
        """Create vertices for a sphere."""
        vertices = []
        color = [0.9, 0.2, 0.2]  # Red

        for i in range(segments):
            lat0 = np.pi * (-0.5 + float(i) / segments)
            lat1 = np.pi * (-0.5 + float(i + 1) / segments)

            for j in range(segments):
                lng0 = 2 * np.pi * float(j) / segments
                lng1 = 2 * np.pi * float(j + 1) / segments

                # Four corners of the quad
                x0 = radius * np.cos(lat0) * np.cos(lng0)
                y0 = radius * np.sin(lat0)
                z0 = radius * np.cos(lat0) * np.sin(lng0)

                x1 = radius * np.cos(lat1) * np.cos(lng0)
                y1 = radius * np.sin(lat1)
                z1 = radius * np.cos(lat1) * np.sin(lng0)

                x2 = radius * np.cos(lat1) * np.cos(lng1)
                y2 = radius * np.sin(lat1)
                z2 = radius * np.cos(lat1) * np.sin(lng1)

                x3 = radius * np.cos(lat0) * np.cos(lng1)
                y3 = radius * np.sin(lat0)
                z3 = radius * np.cos(lat0) * np.sin(lng1)

                # Two triangles per quad
                vertices.extend([
                    center[0] + x0, center[1] + y0, center[2] + z0, *color,
                    center[0] + x1, center[1] + y1, center[2] + z1, *color,
                    center[0] + x2, center[1] + y2, center[2] + z2, *color,

                    center[0] + x0, center[1] + y0, center[2] + z0, *color,
                    center[0] + x2, center[1] + y2, center[2] + z2, *color,
                    center[0] + x3, center[1] + y3, center[2] + z3, *color,
                ])

        return np.array(vertices, dtype=np.float32)

    def _create_cylinder_vertices(self, start, end, radius=0.02, segments=16):
        """Create vertices for a cylinder."""
        vertices = []
        color = [0.2, 0.6, 0.9]  # Blue

        direction = end - start
        length = np.linalg.norm(direction)

        if length < 1e-6:
            return np.array([], dtype=np.float32)

        direction = direction / length

        # Create perpendicular vectors
        if abs(direction[1]) < 0.9:
            perp1 = np.cross(direction, [0, 1, 0])
        else:
            perp1 = np.cross(direction, [1, 0, 0])
        perp1 = perp1 / np.linalg.norm(perp1)
        perp2 = np.cross(direction, perp1)

        # Create cylinder
        for i in range(segments):
            angle0 = 2 * np.pi * i / segments
            angle1 = 2 * np.pi * (i + 1) / segments

            # Points on start circle
            p0_start = start + radius * (np.cos(angle0) * perp1 + np.sin(angle0) * perp2)
            p1_start = start + radius * (np.cos(angle1) * perp1 + np.sin(angle1) * perp2)

            # Points on end circle
            p0_end = end + radius * (np.cos(angle0) * perp1 + np.sin(angle0) * perp2)
            p1_end = end + radius * (np.cos(angle1) * perp1 + np.sin(angle1) * perp2)

            # Two triangles per segment
            vertices.extend([
                *p0_start, *color,
                *p0_end, *color,
                *p1_end, *color,

                *p0_start, *color,
                *p1_end, *color,
                *p1_start, *color,
            ])

        return np.array(vertices, dtype=np.float32)

    def _create_frame_geometry(self, frame_idx):
        """Create geometry for a specific frame."""
        positions = self.joint_positions[frame_idx]
        all_vertices = []

        # Create bones
        for chain in self.kinematic_chain:
            if len(chain) < 2:
                continue
            for i in range(len(chain) - 1):
                j1, j2 = chain[i], chain[i + 1]
                if j1 < self.n_joints and j2 < self.n_joints:
                    vertices = self._create_cylinder_vertices(
                        positions[j1], positions[j2])
                    if len(vertices) > 0:
                        all_vertices.append(vertices)

        # Create joints
        for pos in positions:
            vertices = self._create_sphere_vertices(pos)
            all_vertices.append(vertices)

        if len(all_vertices) == 0:
            return np.array([], dtype=np.float32)

        return np.concatenate(all_vertices)

    def run(self):
        """Run the interactive visualization."""
        if not PYGAME_AVAILABLE:
            print("Error: PyGame/ModernGL not available.")
            return

        # Initialize PyGame
        pygame.init()
        pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption(f"{self.skeleton_type} Animation Viewer")

        # Initialize ModernGL
        ctx = moderngl.create_context()
        ctx.enable(moderngl.DEPTH_TEST)

        # Create shader program
        prog = ctx.program(vertex_shader=VERTEX_SHADER,
                          fragment_shader=FRAGMENT_SHADER)

        # Create initial geometry
        vertices = self._create_frame_geometry(0)
        vbo = ctx.buffer(vertices.tobytes())
        vao = ctx.simple_vertex_array(prog, vbo, 'in_position', 'in_color')

        clock = pygame.time.Clock()
        running = True

        print("\n=== Controls ===")
        print("SPACE: Play/Pause")
        print("→/←: Next/Previous frame")
        print("+/-: Increase/Decrease speed")
        print("R: Reset to first frame")
        print("Mouse Drag: Rotate camera")
        print("ESC: Quit")
        print("===============\n")

        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    elif event.key == K_SPACE:
                        self.is_playing = not self.is_playing
                        print(f"{'Playing' if self.is_playing else 'Paused'}")
                    elif event.key == K_RIGHT:
                        self.current_frame = (self.current_frame + 1) % self.n_frames
                        print(f"Frame: {self.current_frame}/{self.n_frames-1}")
                        vertices = self._create_frame_geometry(self.current_frame)
                        vbo.write(vertices.tobytes())
                    elif event.key == K_LEFT:
                        self.current_frame = (self.current_frame - 1) % self.n_frames
                        print(f"Frame: {self.current_frame}/{self.n_frames-1}")
                        vertices = self._create_frame_geometry(self.current_frame)
                        vbo.write(vertices.tobytes())
                    elif event.key == K_EQUALS or event.key == K_PLUS:
                        self.play_speed = min(self.play_speed * 1.5, 10.0)
                        print(f"Speed: {self.play_speed:.2f}x")
                    elif event.key == K_MINUS:
                        self.play_speed = max(self.play_speed / 1.5, 0.1)
                        print(f"Speed: {self.play_speed:.2f}x")
                    elif event.key == K_r:
                        self.current_frame = 0
                        print("Reset to frame 0")
                        vertices = self._create_frame_geometry(0)
                        vbo.write(vertices.tobytes())
                elif event.type == MOUSEBUTTONDOWN:
                    self.mouse_down = True
                    self.last_mouse_pos = pygame.mouse.get_pos()
                elif event.type == MOUSEBUTTONUP:
                    self.mouse_down = False
                elif event.type == MOUSEMOTION and self.mouse_down:
                    pos = pygame.mouse.get_pos()
                    if self.last_mouse_pos:
                        dx = pos[0] - self.last_mouse_pos[0]
                        dy = pos[1] - self.last_mouse_pos[1]
                        self.camera.azimuth += dx * 0.5
                        self.camera.elevation = np.clip(
                            self.camera.elevation - dy * 0.5, -89, 89)
                    self.last_mouse_pos = pos

            # Update animation
            if self.is_playing:
                current_time = time.time()
                if current_time - self.last_update_time >= (self.frame_delay / self.play_speed):
                    self.current_frame = (self.current_frame + 1) % self.n_frames
                    self.last_update_time = current_time

                    vertices = self._create_frame_geometry(self.current_frame)
                    vbo.write(vertices.tobytes())

            # Render
            ctx.clear(0.1, 0.1, 0.1)

            # Update matrices
            view = self.camera.get_view_matrix()
            projection = self.camera.get_projection_matrix(self.width / self.height)
            mvp = projection @ view

            prog['mvp'].write(mvp.T.astype('f4').tobytes())

            # Draw
            vao.render(moderngl.TRIANGLES)

            pygame.display.flip()
            clock.tick(60)  # 60 FPS display

        pygame.quit()


def load_motion_from_npy(npy_path):
    """Load motion data from .npy file."""
    data = np.load(npy_path)
    print(f"Loaded motion data: {data.shape}")
    return data


def infer_skeleton_type_from_path(npy_path):
    """Try to infer skeleton type from file path."""
    path = Path(npy_path)
    filename = path.stem

    skeleton_types = list(t2m_kinematic_chain.keys())

    for skel_type in skeleton_types:
        if skel_type.lower() in filename.lower():
            return skel_type

    return 'Horse'


def main():
    parser = argparse.ArgumentParser(
        description='Interactive skeleton animation visualizer (PyGame+ModernGL)')
    parser.add_argument('motion_file', type=str,
                        help='Path to .npy motion file')
    parser.add_argument('--skeleton', type=str, default=None,
                        help='Skeleton type (e.g., Horse, Ostrich)')
    parser.add_argument('--fps', type=int, default=30,
                        help='Frames per second for playback (default: 30)')

    args = parser.parse_args()

    motion_data = load_motion_from_npy(args.motion_file)

    skeleton_type = args.skeleton
    if skeleton_type is None:
        skeleton_type = infer_skeleton_type_from_path(args.motion_file)
        print(f"Auto-detected skeleton type: {skeleton_type}")

    visualizer = SkeletonVisualizerPyGame(motion_data, skeleton_type, args.fps)
    visualizer.run()


if __name__ == '__main__':
    main()
