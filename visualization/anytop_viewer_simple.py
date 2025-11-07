#!/usr/bin/env python3
"""
AnyTop Simple Viewer - Alternative GUI using Matplotlib

A simpler GUI application using matplotlib for 3D visualization.
This is a fallback option if PyVistaQt is not available.

Features:
- Load NPY motion files
- 3D matplotlib visualization
- Playback controls
- PySide6 interface

Usage:
    python anytop_viewer_simple.py
"""

import sys
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Qt5Agg')

sys.path.append(str(Path(__file__).parent.parent))

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QSlider, QLabel, QFileDialog, QComboBox, QSpinBox,
        QGroupBox, QMenuBar, QStatusBar, QMessageBox
    )
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QAction
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    print("Error: PySide6 not available. Install with: pip install PySide6")
    sys.exit(1)

try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Error: Matplotlib not available. Install with: pip install matplotlib")
    sys.exit(1)

from data_loaders.truebones.truebones_utils.param_utils import t2m_kinematic_chain


class MatplotlibCanvas(FigureCanvas):
    """Matplotlib canvas for embedding in Qt."""

    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 6), facecolor='#2b2b2b')
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('#1e1e1e')
        self.ax.grid(True, alpha=0.3)

        super().__init__(self.fig)
        self.setParent(parent)

    def clear_plot(self):
        """Clear the plot."""
        self.ax.cla()
        self.ax.set_facecolor('#1e1e1e')
        self.ax.grid(True, alpha=0.3)


class SimpleAnyTopViewer(QMainWindow):
    """Simplified AnyTop Viewer with Matplotlib."""

    def __init__(self):
        super().__init__()

        # Data
        self.motion_data = None
        self.joint_positions = None
        self.n_frames = 0
        self.n_joints = 0
        self.current_frame = 0
        self.skeleton_type = 'Horse'

        # Playback
        self.is_playing = False
        self.fps = 30
        self.play_speed = 1.0

        # Setup UI
        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle('AnyTop Simple Viewer')
        self.setGeometry(100, 100, 1200, 700)

        # Create menu bar
        self.create_menu_bar()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status('Ready. Load a motion file to begin.')

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Left: Matplotlib canvas
        self.canvas = MatplotlibCanvas(self)
        main_layout.addWidget(self.canvas, stretch=3)

        # Right: Control panel
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, stretch=1)

    def create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('&File')

        open_action = QAction('&Open Motion...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.load_motion_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu('&Help')

        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_control_panel(self):
        """Create control panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # File section
        file_group = QGroupBox('File')
        file_layout = QVBoxLayout()

        load_btn = QPushButton('Load Motion (.npy)')
        load_btn.clicked.connect(self.load_motion_file)
        file_layout.addWidget(load_btn)

        self.file_label = QLabel('No file loaded')
        self.file_label.setWordWrap(True)
        file_layout.addWidget(self.file_label)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Settings section
        settings_group = QGroupBox('Settings')
        settings_layout = QVBoxLayout()

        # Skeleton type
        skel_layout = QHBoxLayout()
        skel_layout.addWidget(QLabel('Skeleton:'))
        self.skeleton_combo = QComboBox()
        skeleton_types = sorted(list(t2m_kinematic_chain.keys()))
        self.skeleton_combo.addItems(skeleton_types)
        self.skeleton_combo.setCurrentText('Horse')
        self.skeleton_combo.currentTextChanged.connect(self.on_skeleton_changed)
        skel_layout.addWidget(self.skeleton_combo)
        settings_layout.addLayout(skel_layout)

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

        # Playback section
        playback_group = QGroupBox('Playback')
        playback_layout = QVBoxLayout()

        # Frame label
        self.frame_label = QLabel('Frame: 0 / 0')
        self.frame_label.setAlignment(Qt.AlignCenter)
        playback_layout.addWidget(self.frame_label)

        # Timeline
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setMinimum(0)
        self.timeline_slider.setMaximum(0)
        self.timeline_slider.valueChanged.connect(self.on_timeline_changed)
        playback_layout.addWidget(self.timeline_slider)

        # Buttons
        btn_layout = QHBoxLayout()

        self.play_btn = QPushButton('▶ Play')
        self.play_btn.clicked.connect(self.toggle_playback)
        self.play_btn.setEnabled(False)
        btn_layout.addWidget(self.play_btn)

        self.reset_btn = QPushButton('⏮')
        self.reset_btn.clicked.connect(self.reset_animation)
        self.reset_btn.setEnabled(False)
        btn_layout.addWidget(self.reset_btn)

        playback_layout.addLayout(btn_layout)

        # Speed
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

        # Info section
        info_group = QGroupBox('Info')
        info_layout = QVBoxLayout()

        self.info_label = QLabel('Load a motion file')
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

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

    def load_motion(self, file_path):
        """Load motion data."""
        try:
            self.update_status(f'Loading {Path(file_path).name}...')

            # Load data
            self.motion_data = np.load(file_path)
            self.n_frames, self.n_joints = self.motion_data.shape[:2]

            # Extract positions
            positions = self.motion_data[:, :, :3]
            root_pos = positions[:, 0:1, :]
            self.joint_positions = positions - root_pos

            # Update UI
            self.file_label.setText(f'{Path(file_path).name}')
            self.timeline_slider.setMaximum(self.n_frames - 1)
            self.play_btn.setEnabled(True)
            self.reset_btn.setEnabled(True)

            # Update info
            info_text = f'Frames: {self.n_frames}\nJoints: {self.n_joints}\nDuration: {self.n_frames/self.fps:.2f}s'
            self.info_label.setText(info_text)

            # Auto-detect skeleton
            filename = Path(file_path).stem
            for skel_type in t2m_kinematic_chain.keys():
                if skel_type.lower() in filename.lower():
                    self.skeleton_combo.setCurrentText(skel_type)
                    break

            # Render first frame
            self.render_frame(0)

            self.update_status('Motion loaded successfully')

        except Exception as e:
            self.update_status(f'Error: {e}')
            QMessageBox.critical(self, 'Error', f'Failed to load motion:\n{e}')

    def render_frame(self, frame_idx):
        """Render frame."""
        if self.joint_positions is None:
            return

        self.current_frame = frame_idx
        positions = self.joint_positions[frame_idx]

        # Clear canvas
        self.canvas.clear_plot()
        ax = self.canvas.ax

        # Get kinematic chain
        kinematic_chain = t2m_kinematic_chain.get(self.skeleton_type, [])

        # Draw bones
        for chain in kinematic_chain:
            if len(chain) < 2:
                continue
            for i in range(len(chain) - 1):
                j1, j2 = chain[i], chain[i + 1]
                if j1 < self.n_joints and j2 < self.n_joints:
                    x = [positions[j1, 0], positions[j2, 0]]
                    y = [positions[j1, 1], positions[j2, 1]]
                    z = [positions[j1, 2], positions[j2, 2]]
                    ax.plot(x, y, z, 'b-', linewidth=2, alpha=0.7)

        # Draw joints
        ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2],
                  c='red', s=50, alpha=0.8)

        # Set equal aspect ratio
        max_range = np.array([
            positions[:, 0].max() - positions[:, 0].min(),
            positions[:, 1].max() - positions[:, 1].min(),
            positions[:, 2].max() - positions[:, 2].min()
        ]).max() / 2.0

        mid_x = (positions[:, 0].max() + positions[:, 0].min()) * 0.5
        mid_y = (positions[:, 1].max() + positions[:, 1].min()) * 0.5
        mid_z = (positions[:, 2].max() + positions[:, 2].min()) * 0.5

        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)

        ax.set_xlabel('X', color='white')
        ax.set_ylabel('Y', color='white')
        ax.set_zlabel('Z', color='white')

        # Update frame label
        self.frame_label.setText(f'Frame: {frame_idx} / {self.n_frames - 1}')

        # Refresh canvas
        self.canvas.draw()

    def toggle_playback(self):
        """Toggle play/pause."""
        self.is_playing = not self.is_playing

        if self.is_playing:
            self.play_btn.setText('⏸ Pause')
            interval = int(1000 / (self.fps * self.play_speed))
            self.timer.start(interval)
        else:
            self.play_btn.setText('▶ Play')
            self.timer.stop()

    def update_animation(self):
        """Update animation."""
        if self.is_playing:
            self.current_frame = (self.current_frame + 1) % self.n_frames
            self.timeline_slider.setValue(self.current_frame)
            self.render_frame(self.current_frame)

    def reset_animation(self):
        """Reset to first frame."""
        self.current_frame = 0
        self.timeline_slider.setValue(0)
        self.render_frame(0)

    def on_timeline_changed(self, value):
        """Handle timeline change."""
        if not self.is_playing:
            self.render_frame(value)

    def on_speed_changed(self, value):
        """Handle speed change."""
        self.play_speed = value / 100.0
        self.speed_label.setText(f'{self.play_speed:.1f}x')

        if self.is_playing:
            interval = int(1000 / (self.fps * self.play_speed))
            self.timer.setInterval(interval)

    def on_fps_changed(self, value):
        """Handle FPS change."""
        self.fps = value

        if self.is_playing:
            interval = int(1000 / (self.fps * self.play_speed))
            self.timer.setInterval(interval)

    def on_skeleton_changed(self, skeleton_type):
        """Handle skeleton change."""
        self.skeleton_type = skeleton_type
        if self.joint_positions is not None:
            self.render_frame(self.current_frame)

    def update_status(self, message):
        """Update status bar."""
        self.status_bar.showMessage(message)

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            'About AnyTop Simple Viewer',
            '<h2>AnyTop Simple Viewer</h2>'
            '<p>A simple GUI for visualizing skeletal animations using Matplotlib.</p>'
            '<p><b>Version:</b> 1.0.0</p>'
            '<p><b>Powered by:</b> PySide6, Matplotlib, NumPy</p>'
        )


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName('AnyTop Simple Viewer')
    app.setStyle('Fusion')

    window = SimpleAnyTopViewer()
    window.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
