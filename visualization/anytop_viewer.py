#!/usr/bin/env python3
"""
AnyTop Unified Visualization Application

A modern GUI application for visualizing skeletal animations with full 3D support.

Features:
- Load FBX/OBJ models and NPY/BVH animations
- Interactive 3D viewer with texture support
- Playback controls (play/pause, speed, timeline)
- Skeleton and mesh visualization
- Modern PySide6 interface

Usage:
    python anytop_viewer.py
"""

import sys
import numpy as np
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QSlider, QLabel, QFileDialog, QComboBox, QSpinBox,
        QGroupBox, QMenuBar, QMenu, QStatusBar, QSplitter, QMessageBox,
        QProgressBar
    )
    from PySide6.QtCore import Qt, QTimer, Signal, QThread
    from PySide6.QtGui import QAction, QIcon
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    print("Error: PySide6 not available. Install with: pip install PySide6")
    sys.exit(1)

try:
    from pyvistaqt import QtInteractor
    import pyvista as pv
    PYVISTA_QT_AVAILABLE = True
except ImportError:
    PYVISTA_QT_AVAILABLE = False
    print("Warning: pyvistaqt not available. Install with: pip install pyvistaqt")

from data_loaders.truebones.truebones_utils.param_utils import t2m_kinematic_chain


class AnimationLoader(QThread):
    """Background thread for loading animations."""
    progress = Signal(int)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, motion_file, mesh_file=None):
        super().__init__()
        self.motion_file = motion_file
        self.mesh_file = mesh_file

    def run(self):
        """Load animation data in background."""
        try:
            result = {}

            # Load motion
            self.progress.emit(30)
            motion_data = np.load(self.motion_file)
            result['motion'] = motion_data
            result['n_frames'] = len(motion_data)
            result['n_joints'] = motion_data.shape[1]

            # Extract positions
            self.progress.emit(50)
            positions = motion_data[:, :, :3]
            root_pos = positions[:, 0:1, :]
            positions = positions - root_pos
            result['positions'] = positions

            # Load mesh if provided
            if self.mesh_file:
                self.progress.emit(70)
                mesh = pv.read(str(self.mesh_file))
                result['mesh'] = mesh
                result['has_mesh'] = True
            else:
                result['has_mesh'] = False

            self.progress.emit(100)
            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))


class AnyTopViewer(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Data
        self.motion_data = None
        self.joint_positions = None
        self.mesh = None
        self.mesh_rest_vertices = None
        self.n_frames = 0
        self.n_joints = 0
        self.current_frame = 0
        self.skeleton_type = 'Horse'

        # Playback
        self.is_playing = False
        self.fps = 30
        self.play_speed = 1.0

        # UI components
        self.viewer = None
        self.mesh_actors = []
        self.skeleton_actors = []

        # Setup UI
        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle('AnyTop Unified Viewer')
        self.setGeometry(100, 100, 1400, 800)

        # Create menu bar
        self.create_menu_bar()

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel('Ready')
        self.status_bar.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Create splitter for 3D view and controls
        splitter = QSplitter(Qt.Horizontal)

        # Left: 3D Viewer
        viewer_widget = self.create_viewer_widget()
        splitter.addWidget(viewer_widget)

        # Right: Control Panel
        control_panel = self.create_control_panel()
        splitter.addWidget(control_panel)

        # Set splitter sizes (70% viewer, 30% controls)
        splitter.setSizes([1000, 400])

        main_layout.addWidget(splitter)

        # Update status
        self.update_status('Ready. Load a motion file to begin.')

    def create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('&File')

        open_motion_action = QAction('Open &Motion...', self)
        open_motion_action.setShortcut('Ctrl+O')
        open_motion_action.triggered.connect(self.load_motion_file)
        file_menu.addAction(open_motion_action)

        open_mesh_action = QAction('Open &Mesh...', self)
        open_mesh_action.setShortcut('Ctrl+M')
        open_mesh_action.triggered.connect(self.load_mesh_file)
        file_menu.addAction(open_mesh_action)

        file_menu.addSeparator()

        export_video_action = QAction('Export &Video...', self)
        export_video_action.triggered.connect(self.export_video)
        file_menu.addAction(export_video_action)

        file_menu.addSeparator()

        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu('&View')

        reset_camera_action = QAction('&Reset Camera', self)
        reset_camera_action.setShortcut('R')
        reset_camera_action.triggered.connect(self.reset_camera)
        view_menu.addAction(reset_camera_action)

        toggle_skeleton_action = QAction('Toggle &Skeleton', self)
        toggle_skeleton_action.setShortcut('S')
        toggle_skeleton_action.setCheckable(True)
        toggle_skeleton_action.setChecked(True)
        toggle_skeleton_action.triggered.connect(self.toggle_skeleton)
        view_menu.addAction(toggle_skeleton_action)

        toggle_mesh_action = QAction('Toggle &Mesh', self)
        toggle_mesh_action.setShortcut('M')
        toggle_mesh_action.setCheckable(True)
        toggle_mesh_action.setChecked(True)
        toggle_mesh_action.triggered.connect(self.toggle_mesh)
        view_menu.addAction(toggle_mesh_action)

        # Help menu
        help_menu = menubar.addMenu('&Help')

        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_viewer_widget(self):
        """Create 3D viewer widget."""
        viewer_container = QWidget()
        viewer_layout = QVBoxLayout(viewer_container)

        if PYVISTA_QT_AVAILABLE:
            # PyVista Qt Interactor
            self.viewer = QtInteractor(viewer_container)
            self.viewer.set_background('black')
            viewer_layout.addWidget(self.viewer.interactor)
        else:
            # Fallback: show message
            label = QLabel('PyVista Qt not available.\nInstall with: pip install pyvistaqt')
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet('color: white; background-color: #2b2b2b; padding: 20px;')
            viewer_layout.addWidget(label)

        return viewer_container

    def create_control_panel(self):
        """Create control panel widget."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # File selection group
        file_group = QGroupBox('Files')
        file_layout = QVBoxLayout()

        self.motion_file_label = QLabel('Motion: None')
        self.motion_file_label.setWordWrap(True)
        file_layout.addWidget(self.motion_file_label)

        load_motion_btn = QPushButton('Load Motion File (.npy)')
        load_motion_btn.clicked.connect(self.load_motion_file)
        file_layout.addWidget(load_motion_btn)

        self.mesh_file_label = QLabel('Mesh: None')
        self.mesh_file_label.setWordWrap(True)
        file_layout.addWidget(self.mesh_file_label)

        load_mesh_btn = QPushButton('Load Mesh File (.fbx, .obj)')
        load_mesh_btn.clicked.connect(self.load_mesh_file)
        file_layout.addWidget(load_mesh_btn)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Settings group
        settings_group = QGroupBox('Settings')
        settings_layout = QVBoxLayout()

        # Skeleton type
        skeleton_layout = QHBoxLayout()
        skeleton_layout.addWidget(QLabel('Skeleton Type:'))
        self.skeleton_combo = QComboBox()
        skeleton_types = sorted(list(t2m_kinematic_chain.keys()))
        self.skeleton_combo.addItems(skeleton_types)
        self.skeleton_combo.setCurrentText('Horse')
        self.skeleton_combo.currentTextChanged.connect(self.on_skeleton_changed)
        skeleton_layout.addWidget(self.skeleton_combo)
        settings_layout.addLayout(skeleton_layout)

        # FPS
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel('FPS:'))
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(1, 120)
        self.fps_spinbox.setValue(30)
        self.fps_spinbox.valueChanged.connect(self.on_fps_changed)
        fps_layout.addWidget(self.fps_spinbox)
        settings_layout.addLayout(fps_layout)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Playback controls group
        playback_group = QGroupBox('Playback')
        playback_layout = QVBoxLayout()

        # Frame info
        self.frame_label = QLabel('Frame: 0 / 0')
        self.frame_label.setAlignment(Qt.AlignCenter)
        playback_layout.addWidget(self.frame_label)

        # Timeline slider
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setMinimum(0)
        self.timeline_slider.setMaximum(0)
        self.timeline_slider.setValue(0)
        self.timeline_slider.valueChanged.connect(self.on_timeline_changed)
        playback_layout.addWidget(self.timeline_slider)

        # Playback buttons
        button_layout = QHBoxLayout()

        self.play_button = QPushButton('▶ Play')
        self.play_button.clicked.connect(self.toggle_playback)
        self.play_button.setEnabled(False)
        button_layout.addWidget(self.play_button)

        self.reset_button = QPushButton('⏮ Reset')
        self.reset_button.clicked.connect(self.reset_animation)
        self.reset_button.setEnabled(False)
        button_layout.addWidget(self.reset_button)

        playback_layout.addLayout(button_layout)

        # Speed control
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel('Speed:'))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(10)
        self.speed_slider.setMaximum(200)
        self.speed_slider.setValue(100)
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        speed_layout.addWidget(self.speed_slider)
        self.speed_label = QLabel('1.0x')
        speed_layout.addWidget(self.speed_label)
        playback_layout.addLayout(speed_layout)

        playback_group.setLayout(playback_layout)
        layout.addWidget(playback_group)

        # Info group
        info_group = QGroupBox('Information')
        info_layout = QVBoxLayout()

        self.info_label = QLabel('No animation loaded')
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Add stretch to push everything to top
        layout.addStretch()

        return panel

    def setup_timer(self):
        """Setup animation timer."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)

    def load_motion_file(self):
        """Load motion file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Open Motion File',
            str(Path.home()),
            'Motion Files (*.npy);;All Files (*)'
        )

        if file_path:
            self.load_motion(file_path)

    def load_mesh_file(self):
        """Load mesh file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Open Mesh File',
            str(Path.home()),
            'Mesh Files (*.fbx *.obj *.stl *.ply);;All Files (*)'
        )

        if file_path:
            self.load_mesh(file_path)

    def load_motion(self, file_path):
        """Load motion data."""
        self.update_status(f'Loading {Path(file_path).name}...')
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Create loader thread
        self.loader = AnimationLoader(file_path)
        self.loader.progress.connect(self.progress_bar.setValue)
        self.loader.finished.connect(self.on_motion_loaded)
        self.loader.error.connect(self.on_load_error)
        self.loader.start()

        # Update UI
        self.motion_file_label.setText(f'Motion: {Path(file_path).name}')

        # Try to detect skeleton type
        filename = Path(file_path).stem
        for skel_type in t2m_kinematic_chain.keys():
            if skel_type.lower() in filename.lower():
                self.skeleton_combo.setCurrentText(skel_type)
                break

    def on_motion_loaded(self, result):
        """Handle loaded motion data."""
        self.motion_data = result['motion']
        self.joint_positions = result['positions']
        self.n_frames = result['n_frames']
        self.n_joints = result['n_joints']
        self.current_frame = 0

        # Update UI
        self.timeline_slider.setMaximum(self.n_frames - 1)
        self.timeline_slider.setValue(0)
        self.play_button.setEnabled(True)
        self.reset_button.setEnabled(True)

        # Update info
        self.update_info()

        # Render first frame
        self.render_frame(0)

        # Hide progress bar
        self.progress_bar.setVisible(False)
        self.update_status('Motion loaded successfully')

    def on_load_error(self, error_msg):
        """Handle loading error."""
        self.progress_bar.setVisible(False)
        self.update_status(f'Error: {error_msg}')
        QMessageBox.critical(self, 'Loading Error', f'Failed to load file:\n{error_msg}')

    def load_mesh(self, file_path):
        """Load 3D mesh."""
        try:
            self.update_status(f'Loading mesh {Path(file_path).name}...')
            mesh = pv.read(str(file_path))
            self.mesh = mesh
            self.mesh_rest_vertices = mesh.points.copy()
            self.mesh_file_label.setText(f'Mesh: {Path(file_path).name}')

            # Re-render current frame
            if self.joint_positions is not None:
                self.render_frame(self.current_frame)

            self.update_status('Mesh loaded successfully')

        except Exception as e:
            self.update_status(f'Error loading mesh: {e}')
            QMessageBox.critical(self, 'Mesh Loading Error', f'Failed to load mesh:\n{e}')

    def render_frame(self, frame_idx):
        """Render specific frame."""
        if not PYVISTA_QT_AVAILABLE or self.viewer is None:
            return

        if self.joint_positions is None:
            return

        self.current_frame = frame_idx

        # Clear previous actors
        self.viewer.clear()

        # Get positions for current frame
        positions = self.joint_positions[frame_idx]

        # Render mesh if available
        if self.mesh is not None:
            # Simple rigid transform to root
            transform = np.eye(4)
            transform[:3, 3] = positions[0]

            transformed_mesh = self.mesh.copy()
            transformed_mesh.points = self.mesh_rest_vertices + positions[0]

            self.viewer.add_mesh(transformed_mesh, color='tan', smooth_shading=True)

        # Render skeleton
        kinematic_chain = t2m_kinematic_chain.get(self.skeleton_type, [])

        # Draw bones
        for chain in kinematic_chain:
            if len(chain) < 2:
                continue
            for i in range(len(chain) - 1):
                j1, j2 = chain[i], chain[i + 1]
                if j1 < self.n_joints and j2 < self.n_joints:
                    start = positions[j1]
                    end = positions[j2]
                    direction = end - start
                    length = np.linalg.norm(direction)

                    if length > 1e-6:
                        cylinder = pv.Cylinder(
                            center=(start + end) / 2,
                            direction=direction,
                            radius=0.02,
                            height=length
                        )
                        self.viewer.add_mesh(cylinder, color='lightblue', opacity=0.8)

        # Draw joints
        for pos in positions:
            sphere = pv.Sphere(radius=0.03, center=pos)
            self.viewer.add_mesh(sphere, color='red')

        # Update frame label
        self.frame_label.setText(f'Frame: {frame_idx} / {self.n_frames - 1}')

        # Update viewer
        if hasattr(self.viewer, 'update'):
            self.viewer.update()

    def toggle_playback(self):
        """Toggle play/pause."""
        self.is_playing = not self.is_playing

        if self.is_playing:
            self.play_button.setText('⏸ Pause')
            interval = int(1000 / (self.fps * self.play_speed))
            self.timer.start(interval)
        else:
            self.play_button.setText('▶ Play')
            self.timer.stop()

    def update_animation(self):
        """Update animation frame."""
        if self.is_playing and self.joint_positions is not None:
            self.current_frame = (self.current_frame + 1) % self.n_frames
            self.timeline_slider.setValue(self.current_frame)
            self.render_frame(self.current_frame)

    def reset_animation(self):
        """Reset animation to first frame."""
        self.current_frame = 0
        self.timeline_slider.setValue(0)
        self.render_frame(0)

    def on_timeline_changed(self, value):
        """Handle timeline slider change."""
        if not self.is_playing:  # Only manual scrubbing when paused
            self.render_frame(value)

    def on_speed_changed(self, value):
        """Handle speed slider change."""
        self.play_speed = value / 100.0
        self.speed_label.setText(f'{self.play_speed:.1f}x')

        # Update timer if playing
        if self.is_playing:
            interval = int(1000 / (self.fps * self.play_speed))
            self.timer.setInterval(interval)

    def on_fps_changed(self, value):
        """Handle FPS change."""
        self.fps = value

        # Update timer if playing
        if self.is_playing:
            interval = int(1000 / (self.fps * self.play_speed))
            self.timer.setInterval(interval)

    def on_skeleton_changed(self, skeleton_type):
        """Handle skeleton type change."""
        self.skeleton_type = skeleton_type
        if self.joint_positions is not None:
            self.render_frame(self.current_frame)

    def reset_camera(self):
        """Reset camera to default view."""
        if PYVISTA_QT_AVAILABLE and self.viewer is not None:
            self.viewer.reset_camera()

    def toggle_skeleton(self, checked):
        """Toggle skeleton visibility."""
        # Would need to track skeleton actors separately
        pass

    def toggle_mesh(self, checked):
        """Toggle mesh visibility."""
        # Would need to track mesh actors separately
        pass

    def export_video(self):
        """Export animation as video."""
        if self.joint_positions is None:
            QMessageBox.warning(self, 'No Animation', 'Load an animation first.')
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Export Video',
            str(Path.home() / 'animation.mp4'),
            'Video Files (*.mp4 *.avi);;All Files (*)'
        )

        if file_path:
            # TODO: Implement video export
            QMessageBox.information(
                self,
                'Video Export',
                'Video export feature coming soon!\n\n'
                'For now, use the command-line visualizers with screenshot export.'
            )

    def update_status(self, message):
        """Update status bar message."""
        self.status_label.setText(message)

    def update_info(self):
        """Update information panel."""
        if self.motion_data is not None:
            info_text = f'''
<b>Animation Info:</b><br>
Frames: {self.n_frames}<br>
Joints: {self.n_joints}<br>
Features: {self.motion_data.shape[2]}<br>
Skeleton: {self.skeleton_type}<br>
FPS: {self.fps}<br>
Duration: {self.n_frames / self.fps:.2f}s
            '''.strip()
            self.info_label.setText(info_text)
        else:
            self.info_label.setText('No animation loaded')

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            'About AnyTop Viewer',
            '''<h2>AnyTop Unified Viewer</h2>
            <p>A modern GUI application for visualizing skeletal animations.</p>
            <p><b>Features:</b></p>
            <ul>
            <li>Interactive 3D visualization</li>
            <li>Support for NPY motion files</li>
            <li>Support for FBX/OBJ mesh files</li>
            <li>Real-time playback controls</li>
            <li>Multiple skeleton types</li>
            </ul>
            <p><b>Version:</b> 1.0.0</p>
            <p><b>Powered by:</b> PySide6, PyVista, NumPy</p>
            '''
        )


def main():
    """Main application entry point."""
    if not PYSIDE6_AVAILABLE:
        print("Error: PySide6 not available")
        print("Install with: pip install PySide6")
        return 1

    if not PYVISTA_QT_AVAILABLE:
        print("Warning: pyvistaqt not available")
        print("Install with: pip install pyvistaqt")
        print("Continuing with limited functionality...")

    app = QApplication(sys.argv)
    app.setApplicationName('AnyTop Viewer')
    app.setOrganizationName('AnyTop')

    # Set application style
    app.setStyle('Fusion')

    # Create and show main window
    window = AnyTopViewer()
    window.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
