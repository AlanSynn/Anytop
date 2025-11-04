# Interactive Skeleton Animation Visualizers

This directory contains three Python-based interactive visualizers for skeletal animations that work **without Blender**. Each visualizer can display textures (bone colors), bones (skeleton structure), and movement (animations) in real-time.

## Overview

We provide three different visualization backends, each with their own strengths:

| Visualizer | Backend | Ease of Use | Performance | Customization | Best For |
|------------|---------|-------------|-------------|---------------|----------|
| **Vedo** | VTK | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Quick visualization, scientific use |
| **Open3D** | Custom | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | High performance, production use |
| **PyGame+ModernGL** | OpenGL | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Custom shaders, full control |

## Installation

### Install All Dependencies (Recommended)

```bash
cd visualization
pip install -r requirements_visualizer.txt
```

### Install Individual Backends

**For Vedo visualizer only:**
```bash
pip install vedo numpy
```

**For Open3D visualizer only:**
```bash
pip install open3d numpy
```

**For PyGame+ModernGL visualizer only:**
```bash
pip install pygame moderngl PyOpenGL numpy
```

## Usage

### 1. Vedo Visualizer (Recommended)

The easiest to use with the most features out of the box.

```bash
# Basic usage (auto-detects skeleton type from filename)
python interactive_visualizer.py path/to/animation.npy

# Specify skeleton type explicitly
python interactive_visualizer.py assets/Hound___Attack_470.npy --skeleton Hound

# Adjust playback speed (FPS)
python interactive_visualizer.py assets/Horse___Walk_123.npy --fps 60
```

**Controls:**
- `SPACE`: Play/Pause animation
- `→` / `←`: Next/Previous frame
- `+` / `-`: Increase/Decrease playback speed
- `R`: Reset to first frame
- `Q` / `ESC`: Quit
- `Mouse`: Rotate, pan, and zoom camera

### 2. Open3D Visualizer

High-performance visualizer with excellent rendering quality.

```bash
# Basic usage
python interactive_visualizer_open3d.py path/to/animation.npy

# With options
python interactive_visualizer_open3d.py assets/Ostrich___Attack_581.npy --skeleton Ostrich --fps 30
```

**Controls:**
- `SPACE`: Play/Pause animation
- `→` / `←`: Next/Previous frame
- `+` / `-`: Increase/Decrease playback speed
- `R`: Reset to first frame
- `Mouse Left Button + Drag`: Rotate camera
- `Mouse Right Button + Drag`: Pan camera
- `Mouse Wheel`: Zoom in/out

### 3. PyGame + ModernGL Visualizer

Low-level OpenGL visualizer for maximum control and customization.

```bash
# Basic usage
python interactive_visualizer_pygame.py path/to/animation.npy

# With options
python interactive_visualizer_pygame.py assets/Scorpion___SlowForward_837.npy --skeleton Scorpion
```

**Controls:**
- `SPACE`: Play/Pause animation
- `→` / `←`: Next/Previous frame
- `+` / `-`: Increase/Decrease playback speed
- `R`: Reset to first frame
- `Mouse Drag`: Rotate camera
- `ESC`: Quit

## Examples

### Visualize Horse Animation
```bash
# If file contains "Horse" in the name, skeleton type is auto-detected
python interactive_visualizer.py dataset/truebones/zoo/truebones_processed/motions/Horse___Walk_123.npy
```

### Visualize Ostrich Animation
```bash
python interactive_visualizer.py assets/Ostrich___Attack_581.npy --skeleton Ostrich --fps 30
```

### Visualize Spider Animation
```bash
python interactive_visualizer_open3d.py dataset/motions/Spider___Crawl_456.npy --skeleton Spider
```

## Supported Skeleton Types

The visualizers support all skeleton types in the dataset. Common types include:

### Bipeds
- Ostrich, Flamingo, Raptor, Chicken, Trex, Tyranno

### Quadrupeds (45+ variants)
- Horse, Camel, Bear, Cat, Dog, Elephant, Lion, Tiger, Wolf, Zebra, etc.

### Millipeds
- Cricket, Spider, Scorpion, Ant, Centipede, Crab, Roach, Isopod

### Snakes
- Anaconda, KingCobra

### Flying
- Bat, Dragon, Bird, Eagle, Pteranodon

### Others
- Turtle, Frog, Seal, and many more!

**Note:** If the skeleton type is not specified, the visualizer will attempt to auto-detect it from the filename.

## Data Format

The visualizers expect `.npy` files with motion data in the following format:

```python
# Shape: (n_frames, n_joints, 13)
# Features per joint:
#   [0:3]   - RIC Position (Root-Invariant Centered, 3D)
#   [3:9]   - 6D Rotation representation
#   [9:12]  - Local velocity (3D)
#   [12]    - Foot contact flag (binary)
```

## Visualization Features

### Bones
- Rendered as cylinders connecting joints
- Color: Light blue (customizable in code)
- Thickness: Proportional to skeleton size

### Joints
- Rendered as spheres at joint locations
- Color: Red (customizable in code)
- Size: Proportional to skeleton size

### Animation
- Real-time playback with adjustable speed
- Frame-by-frame navigation
- Smooth interpolation between frames

### Camera
- Orbital camera system
- Interactive rotation, panning, and zooming
- Configurable initial view

## Customization

### Changing Colors

**Vedo:**
```python
# In interactive_visualizer.py
def _create_joint(self, position, radius=0.05):
    return Sphere(position, r=radius, c='red')  # Change 'red' to any color

def _create_bone(self, start_pos, end_pos, radius=0.02):
    return Cylinder(start_pos, end_pos, r=radius, c='lightblue')  # Change color
```

**Open3D:**
```python
# In interactive_visualizer_open3d.py
self.bone_color = [0.2, 0.6, 0.9]  # RGB values [0-1]
self.joint_color = [0.9, 0.2, 0.2]  # RGB values [0-1]
```

**PyGame:**
```python
# In interactive_visualizer_pygame.py
color = [0.9, 0.2, 0.2]  # RGB for joints
color = [0.2, 0.6, 0.9]  # RGB for bones
```

### Adjusting Sizes

```python
# Joint sphere radius (default: 0.05)
sphere = self._create_sphere(pos, radius=0.1)

# Bone cylinder radius (default: 0.02)
cylinder = self._create_cylinder(start, end, radius=0.04)
```

### Adding Textures

To add actual texture mapping, you would need to:
1. Load texture images
2. Apply UV coordinates to the geometry
3. Bind textures in the rendering pipeline

For PyGame+ModernGL, this is straightforward - modify the shaders to include texture sampling.

## Troubleshooting

### Import Errors

If you get import errors, make sure you've installed the required packages:

```bash
pip install vedo open3d pygame moderngl numpy
```

### "Unknown skeleton type" Warning

If you see this warning, either:
1. Rename your file to include the skeleton type (e.g., `Horse___Walk.npy`)
2. Specify the skeleton type explicitly with `--skeleton` flag

### Animation Looks Wrong

- Check that your `.npy` file has the correct shape: `(frames, joints, 13)`
- Verify that the skeleton type matches the actual skeleton in the data
- Try adjusting the FPS with `--fps` flag

### Performance Issues

- **Vedo**: Reduce sphere/cylinder segments (modify the code)
- **Open3D**: Already optimized for performance
- **PyGame**: Reduce geometry detail in `_create_sphere_vertices` and `_create_cylinder_vertices`

### Camera Controls Not Working

- Make sure the visualizer window is in focus
- Try clicking on the window before using keyboard controls
- Mouse controls should work by dragging (left-click and drag)

## Advanced Usage

### Batch Visualization

Create a script to visualize multiple animations:

```python
import glob
import subprocess

for npy_file in glob.glob('assets/*.npy'):
    print(f"Visualizing: {npy_file}")
    subprocess.run(['python', 'interactive_visualizer.py', npy_file])
```

### Export Frames

To export frames for creating videos, modify the visualizers to save screenshots at each frame. Example for Open3D:

```python
# In the _update_visualization method:
vis.capture_screen_image(f"frame_{self.current_frame:04d}.png")
```

### Integration with Other Tools

These visualizers can be imported as modules:

```python
from interactive_visualizer import SkeletonVisualizer

motion_data = np.load('animation.npy')
viz = SkeletonVisualizer(motion_data, skeleton_type='Horse', fps=30)
viz.show()
```

## Comparison with Blender

| Feature | Blender | Interactive Visualizers |
|---------|---------|-------------------------|
| Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Speed | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Interactive | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Ease of Use | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Customization | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Rendering | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

**Use Blender for:** Final rendering, high-quality videos, complex materials
**Use Interactive Visualizers for:** Quick preview, debugging, real-time interaction, development workflow

## Future Enhancements

Potential improvements you can add:
- Texture mapping support
- Skinned mesh rendering
- Multiple skeleton comparison view
- Recording animations to video files
- Custom shader effects (shadows, lighting)
- VR support
- Network streaming

## C++ Implementation

If you need a C++ implementation for better performance or integration with C++ projects, you can use:

- **OpenGL + GLFW + GLM**: Low-level, maximum control
- **OpenSceneGraph**: High-level scene graph
- **Magnum**: Modern C++ graphics library
- **Three.cpp**: Port of Three.js to C++

The Python implementations provided here can serve as reference for the logic and structure.

## License

These visualizers are part of the Anytop project. See the main project LICENSE for details.

## Support

For issues or questions:
1. Check this README first
2. Review the code comments in each visualizer
3. Open an issue on the project repository

## Acknowledgments

- **Vedo**: https://vedo.embl.es/
- **Open3D**: https://www.open3d.org/
- **ModernGL**: https://moderngl.readthedocs.io/
- **PyGame**: https://www.pygame.org/
