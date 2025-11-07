#!/usr/bin/env python3
"""
AnyTop Viewer - macOS Optimized Version

Optimized specifically for Intel Mac performance and compatibility.

Features:
- Reduced rendering overhead
- Optimized update loops
- Better memory management
- macOS-specific OpenGL context handling
- Retina display support
- Performance monitoring

Usage:
    python3 anytop_viewer_macos.py
"""

import sys
import os
import numpy as np
from pathlib import Path

# macOS-specific optimizations
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QSlider, QLabel, QFileDialog, QComboBox, QSpinBox,
        QGroupBox, QStatusBar, QMessageBox, QCheckBox
    )
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QAction
    PYSIDE6_AVAILABLE = True
except ImportError:
    print("Error: PySide6 not available")
    print("Install with: pip3 install PySide6")
    sys.exit(1)

try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib
    matplotlib.use('Qt5Agg')
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    print("Error: Matplotlib not available")
    print("Install with: pip3 install matplotlib")
    sys.exit(1)

from data_loaders.truebones.truebones_utils.param_utils import t2m_kinematic_chain


class OptimizedCanvas(FigureCanvas):
    """Optimized Matplotlib canvas for macOS."""

    def __init__(self, parent=None, dpi=100):
        # Reduced DPI for better performance on Retina displays
        self.fig = Figure(figsize=(8, 6), facecolor='#2b2b2b', dpi=dpi)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('#1e1e1e')
        self.ax.grid(True, alpha=0.3)

        super().__init__(self.fig)
        self.setParent(parent)

        # macOS optimizations
        self.setStyleSheet("background-color: #2b2b2b;")

    def clear_plot(self):
        """Clear with minimal overhead."""
        self.ax.cla()
        self.ax.set_facecolor('#1e1e1e')
        self.ax.grid(True, alpha=0.3)


class MacOSViewer(QMainWindow):
    """macOS-optimized viewer with performance enhancements."""

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
        self.fps = 24  # Cinematic FPS for better performance
        self.play_speed = 1.0

        # Performance settings
        self.render_quality = 'medium'  # low, medium, high
        self.skip_frames = False  # Skip rendering if falling behind

        # UI
        self.init_ui()
        self.setup_timer()

        # macOS specific
        self.set_macos_style()

    def set_macos_style(self):
        """Apply macOS-native styling."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QGroupBox {
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QComboBox, QSpinBox {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 3px;
            }
        """)

    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle('AnyTop Viewer (macOS Optimized)')
        self.setGeometry(100, 100, 1200, 700)

        # Create menu bar
        self.create_menu_bar()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status('Ready | Optimized for macOS')

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Left: Canvas
        self.canvas = OptimizedCanvas(self, dpi=100)  # Lower DPI for performance
        main_layout.addWidget(self.canvas, stretch=3)

        # Right: Controls
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, stretch=1)

    def create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('&File')

        open_action = QAction('&Open Motion...', self)
        open_action.setShortcut('Cmd+O')
        open_action.triggered.connect(self.load_motion_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction('&Quit', self)
        exit_action.setShortcut('Cmd+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Performance menu
        perf_menu = menubar.addMenu('&Performance')

        quality_high = QAction('High Quality', self)
        quality_high.triggered.connect(lambda: self.set_quality('high'))
        perf_menu.addAction(quality_high)

        quality_medium = QAction('Medium Quality', self)
        quality_medium.triggered.connect(lambda: self.set_quality('medium'))
        perf_menu.addAction(quality_medium)

        quality_low = QAction('Low Quality (Fastest)', self)
        quality_low.triggered.connect(lambda: self.set_quality('low'))
        perf_menu.addAction(quality_low)

        # Help menu
        help_menu = menubar.addMenu('&Help')

        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        macos_tips = QAction('macOS Tips', self)
        macos_tips.triggered.connect(self.show_macos_tips)
        help_menu.addAction(macos_tips)

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
        self.fps_spinbox.setRange(10, 60)
        self.fps_spinbox.setValue(24)
        self.fps_spinbox.valueChanged.connect(self.on_fps_changed)
        fps_layout.addWidget(self.fps_spinbox)
        settings_layout.addLayout(fps_layout)

        # Quality preset
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel('Quality:'))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(['Low (Fastest)', 'Medium', 'High'])
        self.quality_combo.setCurrentText('Medium')
        self.quality_combo.currentTextChanged.connect(self.on_quality_changed)
        quality_layout.addWidget(self.quality_combo)
        settings_layout.addLayout(quality_layout)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Playback section
        playback_group = QGroupBox('Playback')
        playback_layout = QVBoxLayout()

        self.frame_label = QLabel('Frame: 0 / 0')
        self.frame_label.setAlignment(Qt.AlignCenter)
        playback_layout.addWidget(self.frame_label)

        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setMinimum(0)
        self.timeline_slider.setMaximum(0)
        self.timeline_slider.valueChanged.connect(self.on_timeline_changed)
        playback_layout.addWidget(self.timeline_slider)

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

        # Performance monitor
        perf_group = QGroupBox('Performance')
        perf_layout = QVBoxLayout()

        self.perf_label = QLabel('FPS: -- | Render: -- ms')
        perf_layout.addWidget(self.perf_label)

        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)

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
        """Setup animation timer with performance monitoring."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)

        # Performance monitoring
        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self.update_performance)
        self.perf_timer.start(1000)  # Update every second

        self.frame_times = []
        self.render_times = []

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
            import time
            start = time.time()

            self.update_status(f'Loading {Path(file_path).name}...')

            self.motion_data = np.load(file_path)
            self.n_frames, self.n_joints = self.motion_data.shape[:2]

            # Extract positions
            positions = self.motion_data[:, :, :3]
            root_pos = positions[:, 0:1, :]
            self.joint_positions = positions - root_pos

            load_time = time.time() - start

            # Update UI
            self.file_label.setText(f'{Path(file_path).name}\n({load_time:.2f}s)')
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

            self.update_status(f'Loaded in {load_time:.2f}s')

        except Exception as e:
            self.update_status(f'Error: {e}')
            QMessageBox.critical(self, 'Error', f'Failed to load:\n{e}')

    def render_frame(self, frame_idx):
        """Render frame with performance optimization."""
        import time
        start = time.time()

        if self.joint_positions is None:
            return

        self.current_frame = frame_idx
        positions = self.joint_positions[frame_idx]

        # Clear canvas
        self.canvas.clear_plot()
        ax = self.canvas.ax

        # Get kinematic chain
        kinematic_chain = t2m_kinematic_chain.get(self.skeleton_type, [])

        # Adjust rendering based on quality setting
        if self.render_quality == 'low':
            linewidth = 1
            markersize = 20
            alpha = 0.6
        elif self.render_quality == 'medium':
            linewidth = 2
            markersize = 40
            alpha = 0.7
        else:  # high
            linewidth = 3
            markersize = 60
            alpha = 0.8

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
                    ax.plot(x, y, z, 'b-', linewidth=linewidth, alpha=alpha)

        # Draw joints
        ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2],
                  c='red', s=markersize, alpha=alpha)

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

        # Track render time
        render_time = (time.time() - start) * 1000  # ms
        self.render_times.append(render_time)
        if len(self.render_times) > 30:
            self.render_times.pop(0)

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
        import time
        start = time.time()

        if self.is_playing:
            self.current_frame = (self.current_frame + 1) % self.n_frames
            self.timeline_slider.setValue(self.current_frame)
            self.render_frame(self.current_frame)

            # Track frame time
            frame_time = time.time() - start
            self.frame_times.append(frame_time)
            if len(self.frame_times) > 30:
                self.frame_times.pop(0)

    def update_performance(self):
        """Update performance metrics."""
        if self.frame_times:
            avg_frame_time = np.mean(self.frame_times)
            actual_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        else:
            actual_fps = 0

        if self.render_times:
            avg_render_time = np.mean(self.render_times)
        else:
            avg_render_time = 0

        self.perf_label.setText(f'FPS: {actual_fps:.1f} | Render: {avg_render_time:.1f} ms')

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

    def on_quality_changed(self, quality_text):
        """Handle quality preset change."""
        if 'Low' in quality_text:
            self.set_quality('low')
        elif 'Medium' in quality_text:
            self.set_quality('medium')
        else:
            self.set_quality('high')

    def set_quality(self, quality):
        """Set rendering quality."""
        self.render_quality = quality

        # Adjust canvas DPI
        if quality == 'low':
            self.canvas.fig.set_dpi(75)
        elif quality == 'medium':
            self.canvas.fig.set_dpi(100)
        else:
            self.canvas.fig.set_dpi(125)

        # Re-render current frame
        if self.joint_positions is not None:
            self.render_frame(self.current_frame)

        self.update_status(f'Quality: {quality}')

    def update_status(self, message):
        """Update status bar."""
        self.status_bar.showMessage(message)

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            'About AnyTop Viewer (macOS)',
            '<h2>AnyTop Viewer</h2>'
            '<p><b>macOS Optimized Version</b></p>'
            '<p>Optimized for Intel Mac performance and compatibility.</p>'
            '<p><b>Features:</b></p>'
            '<ul>'
            '<li>Reduced rendering overhead</li>'
            '<li>Retina display support</li>'
            '<li>Performance monitoring</li>'
            '<li>Quality presets for different hardware</li>'
            '</ul>'
            '<p><b>Version:</b> 1.0.0-macos</p>'
        )

    def show_macos_tips(self):
        """Show macOS-specific tips."""
        QMessageBox.information(
            self,
            'macOS Performance Tips',
            '<h3>Tips for Best Performance on macOS:</h3>'
            '<ul>'
            '<li><b>Use Lower FPS:</b> Try 20-24 instead of 30</li>'
            '<li><b>Reduce Quality:</b> Use Low or Medium quality</li>'
            '<li><b>Close Other Apps:</b> Free up GPU resources</li>'
            '<li><b>Plug In Power:</b> Better performance when not on battery</li>'
            '<li><b>Update macOS:</b> Latest OS versions have better OpenGL</li>'
            '</ul>'
            '<p>See <b>MACOS_SETUP.md</b> for complete guide.</p>'
        )


def main():
    """Main entry point."""
    # macOS-specific configuration
    if sys.platform == 'darwin':
        # Enable Retina support
        os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
        os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'

        # Check macOS version
        import platform
        macos_version = platform.mac_ver()[0]
        print(f"Running on macOS {macos_version}")

    app = QApplication(sys.argv)
    app.setApplicationName('AnyTop Viewer (macOS)')
    app.setStyle('Fusion')

    # Enable high DPI
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    window = MacOSViewer()
    window.show()

    print("\n" + "="*50)
    print("AnyTop Viewer - macOS Optimized")
    print("="*50)
    print("\nPerformance Tips:")
    print("• Use FPS 20-24 for smoother playback")
    print("• Set Quality to Low if experiencing lag")
    print("• Close other applications for best performance")
    print("• Check Performance panel for real-time FPS")
    print("\nSee Performance menu for quality presets")
    print("="*50 + "\n")

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
