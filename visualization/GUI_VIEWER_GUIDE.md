# AnyTop Unified GUI Viewer Guide

Modern desktop applications for visualizing skeletal animations with an intuitive graphical interface.

## 🎯 Overview

We provide **two GUI applications**:

### 1. **AnyTop Viewer** (`anytop_viewer.py`) ⭐ RECOMMENDED
- **Full-featured** 3D visualization with PyVista
- FBX/OBJ mesh support with textures
- High-quality interactive rendering
- Production-ready output

### 2. **AnyTop Simple Viewer** (`anytop_viewer_simple.py`)
- **Lightweight** alternative using Matplotlib
- Skeleton-only visualization
- Fewer dependencies
- Good fallback option

---

## 📦 Installation

### Full Installation (Recommended)

```bash
cd visualization
pip install -r requirements_visualizer.txt
```

This installs:
- PySide6 (Qt GUI framework)
- PyVistaQt (3D visualization)
- All visualization dependencies

### Minimal Installation (Simple Viewer Only)

```bash
pip install PySide6 numpy matplotlib
```

---

## 🚀 Quick Start

### AnyTop Viewer (Full-Featured)

```bash
cd visualization
python anytop_viewer.py
```

Then:
1. Click **"Load Motion File (.npy)"**
2. Select your animation file (e.g., `../assets/Horse___Walk_123.npy`)
3. Optionally click **"Load Mesh File"** to add 3D model
4. Press **▶ Play** to watch the animation!

### AnyTop Simple Viewer (Lightweight)

```bash
cd visualization
python anytop_viewer_simple.py
```

Same workflow as above, but without mesh loading.

---

## 🎮 User Interface Guide

### Main Window Layout

```
┌──────────────────────────────────────────────────────────┐
│ File  View  Help                           [Menu Bar]    │
├─────────────────────────────────┬────────────────────────┤
│                                 │  FILES                 │
│                                 │  ├─ Motion: [Load...]  │
│                                 │  └─ Mesh:  [Load...]  │
│                                 │                        │
│      3D Viewer Area            │  SETTINGS              │
│   (Interactive Rotation/Zoom)  │  ├─ Skeleton Type      │
│                                 │  └─ FPS                │
│                                 │                        │
│                                 │  PLAYBACK              │
│                                 │  ├─ Frame: [slider]    │
│                                 │  ├─ ▶ Play / ⏸ Pause  │
│                                 │  └─ Speed: [slider]    │
│                                 │                        │
│                                 │  INFO                  │
│                                 │  └─ Animation details  │
├─────────────────────────────────┴────────────────────────┤
│ Status: Ready                                  [Status]  │
└──────────────────────────────────────────────────────────┘
```

### Menu Bar

**File Menu:**
- `Open Motion... (Ctrl+O)` - Load NPY motion file
- `Open Mesh... (Ctrl+M)` - Load FBX/OBJ 3D model
- `Export Video...` - Export animation as video (coming soon)
- `Exit (Ctrl+Q)` - Close application

**View Menu:**
- `Reset Camera (R)` - Reset 3D camera to default position
- `Toggle Skeleton (S)` - Show/hide skeleton
- `Toggle Mesh (M)` - Show/hide mesh

**Help Menu:**
- `About` - Show application information

### Control Panel

#### Files Section
- **Load Motion File**: Browse and load `.npy` animation files
- **Load Mesh File**: Browse and load `.fbx`, `.obj`, `.stl`, or `.ply` 3D models

#### Settings Section
- **Skeleton Type**: Select from 70+ animal skeletons
  - Auto-detected from filename
  - Manual selection available

- **FPS**: Set frames per second (1-120)
  - Default: 30 FPS
  - Affects playback speed

#### Playback Section
- **Frame Counter**: Shows current frame / total frames
- **Timeline Slider**: Scrub through animation
  - Drag to navigate frames
  - Works when paused

- **▶ Play / ⏸ Pause**: Start/stop animation
- **⏮ Reset**: Return to first frame
- **Speed Slider**: Adjust playback speed (0.1x - 2.0x)

#### Info Section
- Displays animation statistics:
  - Total frames
  - Number of joints
  - Animation duration
  - Current skeleton type

---

## 🖱️ 3D Viewer Controls

### Mouse Controls

**AnyTop Viewer (PyVista):**
- **Left Click + Drag**: Rotate camera
- **Middle Click + Drag**: Pan camera
- **Right Click + Drag**: Zoom camera
- **Scroll Wheel**: Zoom in/out

**AnyTop Simple Viewer (Matplotlib):**
- **Left Click + Drag**: Rotate view
- **Right Click + Drag**: Zoom
- **Middle Click + Drag**: Pan

### Keyboard Shortcuts

Global:
- `Ctrl+O`: Open motion file
- `Ctrl+M`: Open mesh file
- `Ctrl+Q`: Quit application
- `Space`: Play/Pause (when viewer is focused)
- `R`: Reset camera
- `S`: Toggle skeleton visibility
- `M`: Toggle mesh visibility

---

## 📖 Step-by-Step Tutorials

### Tutorial 1: Basic Skeleton Visualization

1. **Launch Application**
   ```bash
   python anytop_viewer.py
   ```

2. **Load Motion**
   - Click **"Load Motion File (.npy)"**
   - Navigate to `../assets/`
   - Select `Horse___Walk_123.npy`
   - Application auto-detects skeleton type as "Horse"

3. **View Animation**
   - Animation loads and displays first frame
   - Click **▶ Play** to watch
   - Use timeline slider to scrub through frames

4. **Adjust Playback**
   - Change **Speed** slider for faster/slower playback
   - Change **FPS** to 60 for smoother animation

### Tutorial 2: Viewing with 3D Mesh

1. **Load Motion** (as above)

2. **Load 3D Model**
   - Click **"Load Mesh File (.fbx, .obj)"**
   - Select your FBX or OBJ file
   - Mesh appears in viewer, positioned at skeleton root

3. **Customize View**
   - Rotate camera with mouse to find best angle
   - Adjust zoom level
   - Toggle skeleton visibility to see just the mesh

### Tutorial 3: TrueBones Integration

**Prerequisites:** TrueBones FBX Zoo purchased and extracted

1. **Load TrueBones Model**
   ```bash
   python anytop_viewer.py
   ```
   - Load Motion: `../assets/Horse___Walk_123.npy`
   - Load Mesh: `~/TrueBones_FBX_Zoo/Animals/Horse/Horse.fbx`

2. **View Results**
   - Professional 3D horse model with skeleton
   - Textures automatically loaded from FBX
   - Real-time interactive visualization

3. **Export** (when feature is implemented)
   - `File → Export Video...`
   - Choose output format (MP4, AVI)
   - Render high-quality video

### Tutorial 4: Comparing Different Skeletons

1. **Load Animation**
   - Load any NPY file

2. **Switch Skeleton Types**
   - Change "Skeleton Type" dropdown
   - Try: Horse → Bear → Spider → Ostrich
   - See how bone structure changes

3. **Understand Skeleton Topology**
   - Quadrupeds: 4 legs (Horse, Bear, Lion)
   - Bipeds: 2 legs (Ostrich, Flamingo)
   - Multi-legged: 6-8 legs (Spider, Scorpion)
   - See kinematic chains visualized

---

## 🎨 Customization

### Changing Colors

Edit `anytop_viewer.py`:

```python
# Line ~450 (in render_frame method)

# Bone color
self.viewer.add_mesh(cylinder, color='lightblue', opacity=0.8)
# Change to: color='green', opacity=1.0

# Joint color
self.viewer.add_mesh(sphere, color='red')
# Change to: color='yellow'

# Mesh color (when no texture)
self.viewer.add_mesh(transformed_mesh, color='tan', smooth_shading=True)
# Change to: color='white'
```

### Adjusting Sizes

```python
# Bone thickness (line ~460)
radius=0.02  # Make thicker: 0.05

# Joint size (line ~475)
radius=0.03  # Make larger: 0.06
```

### Background Color

```python
# Line ~80 (in create_viewer_widget)
self.viewer.set_background('black')
# Change to: 'white', 'gray', or [R, G, B] like [0.2, 0.3, 0.4]
```

---

## 🔧 Advanced Features

### Loading Multiple Files via Command Line

```bash
# Load motion file at startup
python anytop_viewer.py --motion ../assets/Horse___Walk_123.npy

# Load both motion and mesh
python anytop_viewer.py \
    --motion ../assets/Horse___Walk_123.npy \
    --mesh ~/models/horse.fbx
```

(Note: Command-line arguments need to be implemented)

### Batch Processing

Create a script to process multiple animations:

```python
import subprocess

animations = [
    'Horse___Walk_123.npy',
    'Bear___Run_456.npy',
    'Lion___Jump_789.npy'
]

for anim in animations:
    subprocess.run(['python', 'anytop_viewer.py', '--motion', f'../assets/{anim}'])
```

### Screenshot Export

In the viewer, add screenshot capability:

```python
# Add to menu bar
screenshot_action = QAction('Save Screenshot...', self)
screenshot_action.setShortcut('Ctrl+S')
screenshot_action.triggered.connect(self.save_screenshot)

def save_screenshot(self):
    file_path, _ = QFileDialog.getSaveFileName(
        self, 'Save Screenshot', 'screenshot.png', 'PNG (*.png);;JPG (*.jpg)'
    )
    if file_path and self.viewer:
        self.viewer.screenshot(file_path)
```

---

## 🐛 Troubleshooting

### Issue: "PySide6 not available"

**Solution:**
```bash
pip install PySide6
```

### Issue: "pyvistaqt not available"

**Solution 1:** Install pyvistaqt
```bash
pip install pyvistaqt
```

**Solution 2:** Use Simple Viewer instead
```bash
python anytop_viewer_simple.py
```

### Issue: Black screen in 3D viewer

**Causes:**
1. No animation loaded yet
2. Graphics driver issue
3. PyVista not properly initialized

**Solutions:**
1. Load a motion file
2. Update graphics drivers
3. Try Simple Viewer as fallback

### Issue: Animation loads but doesn't display

**Check:**
1. Skeleton type matches animation
2. Frame slider is not at first position
3. Console for error messages

**Solution:**
```bash
# Run with verbose output
python anytop_viewer.py 2>&1 | tee debug.log
```

### Issue: Mesh loads but looks distorted

**Causes:**
1. Wrong skeleton type selected
2. Mesh scale doesn't match skeleton
3. No skinning data in FBX

**Solutions:**
1. Select correct skeleton type from dropdown
2. Scale mesh in 3D software before loading
3. Use mesh as reference only (rigid transform)

### Issue: Slow playback / laggy

**Solutions:**
1. Reduce FPS to 15-20
2. Use simpler mesh (lower poly count)
3. Close other applications
4. Use Simple Viewer for better performance

### Issue: "Failed to load FBX"

**Solutions:**
1. Convert FBX to OBJ:
   ```bash
   # Using Blender
   blender --background --python-expr "
   import bpy
   bpy.ops.import_scene.fbx(filepath='model.fbx')
   bpy.ops.export_scene.obj(filepath='model.obj')
   "
   ```

2. Try loading OBJ instead
3. Check FBX version (2011-2020 recommended)

---

## 💡 Tips & Best Practices

### Performance Tips

1. **For Large Animations:**
   - Use Simple Viewer for skeleton-only
   - Reduce FPS to 15-20
   - Downsample frames if needed

2. **For Complex Meshes:**
   - Simplify mesh in Blender/Maya first
   - Remove unnecessary detail
   - Use lower-resolution textures

3. **For Real-Time Interaction:**
   - Keep meshes under 50k triangles
   - Use 2K textures max
   - Close other GPU-intensive apps

### Workflow Tips

1. **Preview First:**
   - Use Simple Viewer for quick skeleton preview
   - Switch to full Viewer when satisfied
   - Load mesh only when needed

2. **Organize Files:**
   ```
   project/
   ├── motions/
   │   ├── Horse_Walk.npy
   │   ├── Horse_Run.npy
   │   └── ...
   ├── meshes/
   │   ├── Horse.fbx
   │   ├── Bear.fbx
   │   └── ...
   └── exports/
       └── videos/
   ```

3. **Naming Convention:**
   - Include skeleton type in filename
   - Example: `Horse___Walk_001.npy`
   - Auto-detection works better

### Quality Tips

1. **Camera Angles:**
   - Start with side view (90° rotation)
   - Elevate camera slightly for better perspective
   - Use `View → Reset Camera` to start fresh

2. **Lighting:**
   - PyVista has good default lighting
   - Adjust in code if needed
   - Consider environment maps for realism

3. **Export Quality:**
   - Set resolution before export
   - Use high FPS (60) for smooth video
   - Export uncompressed first, compress later

---

## 🎓 Integration with AnyTop Workflow

### Complete Pipeline

```
1. Generate Motion with AnyTop
   ↓
   python sample/generate.py --skeleton Horse --text "a horse galloping"
   ↓ Creates: results/horse_gallop.npy

2. Preview in GUI
   ↓
   python anytop_viewer.py
   Load: results/horse_gallop.npy
   ↓ Interactive preview

3. Add TrueBones Model (optional)
   ↓
   Load Mesh: ~/TrueBones/Animals/Horse/Horse.fbx
   ↓ Full 3D visualization

4. Export (when implemented)
   ↓
   File → Export Video
   ↓ Final production video
```

### With Research Workflow

```
Experiment → Generate → Visualize → Analyze → Iterate
             (AnyTop)   (GUI)      (Study)   (Refine)
```

### With Production Workflow

```
Concept → Motion → Preview → Model → Render → Deliver
          (AnyTop) (GUI)     (TrueB) (Exp)   (MP4)
```

---

## 📊 Feature Comparison

| Feature | AnyTop Viewer | Simple Viewer | Blender | Command-Line |
|---------|---------------|---------------|---------|--------------|
| GUI | ✅ Modern | ✅ Basic | ✅ Complex | ❌ |
| 3D Meshes | ✅ | ❌ | ✅ | ✅ |
| Textures | ✅ | ❌ | ✅ | ✅ |
| Real-time | ✅ | ✅ | ⚠️ | ✅ |
| Playback Controls | ✅ | ✅ | ✅ | ✅ |
| Ease of Use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Performance | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🚀 Future Enhancements

Planned features:
- ✅ Load and visualize animations
- ✅ 3D mesh support
- ✅ Playback controls
- ⏳ Video export functionality
- ⏳ Screenshot capture
- ⏳ Multiple skeleton comparison
- ⏳ Timeline editing
- ⏳ Custom shader support
- ⏳ VR mode
- ⏳ Batch processing GUI
- ⏳ Motion retargeting UI
- ⏳ Physics preview

---

## 📚 Resources

### Documentation
- **This Guide**: GUI usage and tutorials
- **TRUEBONES_GUIDE.md**: TrueBones integration
- **README_INTERACTIVE.md**: Command-line visualizers

### Libraries
- **PySide6**: https://doc.qt.io/qtforpython/
- **PyVista**: https://docs.pyvista.org/
- **PyVistaQt**: https://qtdocs.pyvista.org/

### Support
- GitHub Issues: Report bugs and request features
- Documentation: Check guides for common issues
- Community: Join discussions

---

## 🎉 Summary

You now have a **professional desktop application** for visualizing skeletal animations with:

✅ **Modern GUI** with intuitive controls
✅ **3D interactive viewer** with mouse controls
✅ **Playback system** with timeline and speed control
✅ **Mesh support** for full 3D models
✅ **Texture rendering** with PyVista
✅ **Multiple skeleton types** (70+ animals)
✅ **TrueBones integration** for production quality

**Launch it now:**
```bash
cd visualization
python anytop_viewer.py
```

Enjoy your unified visualization experience! 🎨✨
