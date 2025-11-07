# TrueBones FBX Zoo - Complete Visualization Guide

This guide explains how to use the advanced visualizers with the TrueBones FBX Zoo asset pack to create **full 3D animated visualizations** with meshes, textures, and skeletal skinning.

## 🎯 Overview

The TrueBones FBX Zoo (https://truebones.gumroad.com/l/skZMC) contains:
- **75+ animal character models** in FBX format
- **Texture maps** for realistic rendering
- **BVH animations** for motion data
- **iClone files** for additional workflows

Our advanced visualizers can load these assets and create **interactive 3D visualizations** with:
- ✅ **Full 3D meshes** (not just skeletons)
- ✅ **Texture mapping** (diffuse, normal, specular)
- ✅ **Skeletal skinning** (mesh deformation)
- ✅ **Real-time animation playback**
- ✅ **Interactive camera controls**

---

## 📦 Prerequisites

### 1. Install TrueBones FBX Zoo

Purchase and download from: https://truebones.gumroad.com/l/skZMC

Extract the ZIP file to a convenient location, e.g.:
```
~/TrueBones_FBX_Zoo/
├── Animals/
│   ├── Horse/
│   │   ├── Horse.fbx
│   │   ├── Textures/
│   │   │   ├── Horse_Diffuse.png
│   │   │   ├── Horse_Normal.png
│   │   │   └── Horse_Specular.png
│   │   └── Animations/
│   │       ├── Walk.bvh
│   │       └── Run.bvh
│   ├── Bear/
│   ├── Lion/
│   └── ... (70+ more animals)
└── README.txt
```

### 2. Install Python Dependencies

```bash
cd visualization
pip install -r requirements_visualizer.txt
```

Or install just what you need:

**For PyVista Visualizer (RECOMMENDED):**
```bash
pip install pyvista numpy Pillow
```

**For Advanced Vedo/Trimesh Visualizer:**
```bash
pip install vedo trimesh pyassimp Pillow numpy
```

---

## 🚀 Quick Start

### Option 1: PyVista Visualizer (Recommended)

```bash
# Basic usage with FBX + motion
python pyvista_visualizer.py \
    --fbx ~/TrueBones_FBX_Zoo/Animals/Horse/Horse.fbx \
    --motion ../assets/Horse___Walk_123.npy \
    --skeleton Horse

# With custom texture
python pyvista_visualizer.py \
    --obj ~/TrueBones_FBX_Zoo/Animals/Horse/Horse.obj \
    --texture ~/TrueBones_FBX_Zoo/Animals/Horse/Textures/Horse_Diffuse.png \
    --motion ../assets/Horse___Walk_123.npy
```

### Option 2: Advanced Vedo Visualizer

```bash
# With FBX model
python advanced_visualizer.py \
    --fbx ~/TrueBones_FBX_Zoo/Animals/Bear/Bear.fbx \
    --motion ../assets/Bear___Walk_456.npy \
    --skeleton Bear

# With BVH animation instead of NPY
python advanced_visualizer.py \
    --fbx ~/TrueBones_FBX_Zoo/Animals/Lion/Lion.fbx \
    --animation ~/TrueBones_FBX_Zoo/Animals/Lion/Animations/Run.bvh \
    --skeleton Lion
```

---

## 📖 Detailed Usage

### PyVista Visualizer (`pyvista_visualizer.py`)

**Best for:** Production-quality rendering with textures

```bash
python pyvista_visualizer.py [OPTIONS]
```

**Options:**
- `--fbx PATH`: Path to FBX model file
- `--obj PATH`: Path to OBJ model file (alternative to FBX)
- `--texture PATH`: Path to texture image (for OBJ files)
- `--motion PATH`: Path to NPY motion file (required)
- `--skeleton TYPE`: Skeleton type (e.g., Horse, Bear, Lion)
- `--fps FPS`: Frames per second (default: 30)

**Features:**
- ✅ Excellent texture mapping
- ✅ High-quality rendering
- ✅ Smooth shading
- ✅ Interactive camera (rotate, pan, zoom)
- ✅ Real-time playback

**Controls:**
- `SPACE`: Play/Pause
- `←/→`: Previous/Next frame
- `+/-`: Speed up/slow down
- `R`: Reset to frame 0
- `Q`: Quit
- `Mouse`: Rotate/Pan/Zoom

### Advanced Vedo Visualizer (`advanced_visualizer.py`)

**Best for:** Full skinning support and mesh deformation

```bash
python advanced_visualizer.py [OPTIONS]
```

**Options:**
- `--fbx PATH`: Path to FBX model file
- `--animation PATH`: Path to BVH animation file
- `--motion PATH`: Path to NPY motion file
- `--skeleton TYPE`: Skeleton type
- `--fps FPS`: Frames per second
- `--texture PATH`: Additional texture file

**Features:**
- ✅ Skeletal skinning (bone weights + deformation)
- ✅ Multi-mesh support
- ✅ Texture mapping
- ✅ BVH and NPY animation support
- ✅ Bone influence visualization

**Controls:**
- Same as PyVista visualizer

---

## 🔧 Workflow Examples

### Example 1: Visualize TrueBones Horse with AnyTop Motion

```bash
# 1. Extract TrueBones Horse model
TRUEBONES=~/TrueBones_FBX_Zoo
HORSE_FBX=$TRUEBONES/Animals/Horse/Horse.fbx

# 2. Use AnyTop-generated motion
MOTION=../assets/Horse___Walk_123.npy

# 3. Visualize
python pyvista_visualizer.py \
    --fbx $HORSE_FBX \
    --motion $MOTION \
    --skeleton Horse \
    --fps 30
```

### Example 2: Apply Generated Motion to New Animal

```bash
# Generate motion for Bear using AnyTop
cd ..
python sample/generate.py --skeleton Bear --text "a bear walking slowly"

# Visualize with TrueBones Bear model
cd visualization
python pyvista_visualizer.py \
    --fbx ~/TrueBones_FBX_Zoo/Animals/Bear/Bear.fbx \
    --motion ../results/bear_walk_generated.npy \
    --skeleton Bear
```

### Example 3: Batch Process Multiple Animals

```bash
#!/bin/bash
# visualize_all_animals.sh

TRUEBONES=~/TrueBones_FBX_Zoo
MOTIONS=../assets

for ANIMAL in Horse Bear Lion Tiger Elephant; do
    echo "Visualizing $ANIMAL..."

    FBX=$TRUEBONES/Animals/$ANIMAL/$ANIMAL.fbx
    MOTION=$MOTIONS/${ANIMAL}___Walk_*.npy

    python pyvista_visualizer.py \
        --fbx $FBX \
        --motion $MOTION \
        --skeleton $ANIMAL \
        --fps 30
done
```

### Example 4: Export High-Quality Video

```python
# render_video.py
import pyvista as pv
import numpy as np
from pyvista_visualizer import PyVistaVisualizer

# Load model and motion
viz = PyVistaVisualizer(skeleton_type='Horse', fps=30)
viz.load_fbx('~/TrueBones_FBX_Zoo/Animals/Horse/Horse.fbx')
viz.load_motion_npy('../assets/Horse___Walk_123.npy')

# Setup plotter for video export
plotter = pv.Plotter(off_screen=True, window_size=[1920, 1080])
plotter.set_background('white')

# Render each frame
frames = []
for frame_idx in range(viz.n_frames):
    viz._update_frame(plotter, frame_idx)
    frame = plotter.screenshot(return_img=True)
    frames.append(frame)

# Save as video using imageio
import imageio
imageio.mimsave('horse_walk.mp4', frames, fps=30, quality=9)
```

---

## 🎨 Texture Setup

### Understanding TrueBones Textures

TrueBones models typically include multiple texture maps:

```
Textures/
├── Animal_Diffuse.png    # Base color/albedo
├── Animal_Normal.png     # Normal map for detail
├── Animal_Specular.png   # Specular/roughness
└── Animal_Ambient.png    # Ambient occlusion
```

### Applying Textures

**For FBX files:**
Textures are usually embedded or referenced automatically. The visualizer will attempt to load them.

**For OBJ files:**
Specify the texture explicitly:
```bash
python pyvista_visualizer.py \
    --obj model.obj \
    --texture Textures/Animal_Diffuse.png \
    --motion animation.npy
```

**For manual texture mapping:**
Edit the visualizer code to load multiple textures:
```python
# In pyvista_visualizer.py
diffuse = pv.read_texture('Textures/Animal_Diffuse.png')
normal = pv.read_texture('Textures/Animal_Normal.png')

plotter.add_mesh(mesh, texture=diffuse, pbr=True)
```

---

## 🦴 Skeletal Skinning

### How Skinning Works

1. **Bone Weights**: Each vertex has weights for 1-4 bones
2. **Bone Indices**: Each vertex references specific bones
3. **Deformation**: Vertex position = Σ (bone_transform × weight)

### Enabling Skinning

The visualizers automatically extract skinning data from FBX files if available.

**Check if your model has skinning:**
```python
import pyassimp

scene = pyassimp.load('model.fbx')
mesh = scene.meshes[0]

if hasattr(mesh, 'bones') and len(mesh.bones) > 0:
    print(f"Model has {len(mesh.bones)} bones")
    for bone in mesh.bones:
        print(f"  {bone.name}: {len(bone.weights)} vertices")
else:
    print("No skinning data found")
```

### Manual Skinning Setup

If your FBX doesn't have skinning data, you can set it up manually:

```python
# Example: Assign all vertices to root bone
n_verts = len(mesh.vertices)
bone_weights = np.zeros((n_verts, 4))
bone_indices = np.zeros((n_verts, 4), dtype=int)

# All weight on bone 0 (root)
bone_weights[:, 0] = 1.0
bone_indices[:, 0] = 0

mesh.bone_weights = bone_weights
mesh.bone_indices = bone_indices
```

---

## 🎬 Animation Pipeline

### Complete Pipeline: TrueBones → AnyTop → Visualization

```
1. TrueBones FBX Model (3D Mesh + Skeleton + Textures)
   ↓
2. AnyTop Motion Generation (NPY motion file)
   ↓
3. Advanced Visualizer (Combines mesh + motion)
   ↓
4. Interactive 3D Animation or Video Export
```

### Step-by-Step:

**Step 1: Prepare TrueBones Model**
```bash
# Extract FBX and locate textures
ANIMAL=Horse
FBX=~/TrueBones_FBX_Zoo/Animals/$ANIMAL/$ANIMAL.fbx
TEXTURE=~/TrueBones_FBX_Zoo/Animals/$ANIMAL/Textures/${ANIMAL}_Diffuse.png
```

**Step 2: Generate Motion with AnyTop**
```bash
cd /home/user/Anytop
python sample/generate.py \
    --skeleton Horse \
    --text "a horse galloping across a field" \
    --output results/horse_gallop.npy
```

**Step 3: Visualize Combined Result**
```bash
cd visualization
python pyvista_visualizer.py \
    --fbx $FBX \
    --motion ../results/horse_gallop.npy \
    --skeleton Horse \
    --fps 30
```

**Step 4: Export Video (Optional)**
```python
# Use the rendering script to export MP4
python render_video.py \
    --fbx $FBX \
    --motion ../results/horse_gallop.npy \
    --output horse_gallop.mp4 \
    --resolution 1920x1080 \
    --fps 30
```

---

## 🐛 Troubleshooting

### Issue: "Cannot load FBX file"

**Solution:**
1. Try converting FBX to OBJ:
   ```bash
   # Using Blender command-line
   blender --background --python - <<EOF
   import bpy
   bpy.ops.import_scene.fbx(filepath='model.fbx')
   bpy.ops.export_scene.obj(filepath='model.obj')
   EOF
   ```

2. Use OBJ with visualizer:
   ```bash
   python pyvista_visualizer.py --obj model.obj --motion animation.npy
   ```

### Issue: "Textures not loading"

**Solution:**
1. Check texture paths are correct
2. Ensure textures are in common format (PNG, JPG, TGA)
3. Specify texture manually:
   ```bash
   python pyvista_visualizer.py --obj model.obj --texture diffuse.png --motion anim.npy
   ```

### Issue: "Skeleton doesn't match motion"

**Solution:**
1. Verify skeleton type matches:
   ```bash
   # List available skeleton types
   python -c "from data_loaders.truebones.truebones_utils.param_utils import t2m_kinematic_chain; print(list(t2m_kinematic_chain.keys()))"
   ```

2. Use correct skeleton type:
   ```bash
   python pyvista_visualizer.py --fbx model.fbx --motion anim.npy --skeleton CorrectType
   ```

### Issue: "Mesh looks distorted"

**Solution:**
1. Check if skinning data exists
2. Try without skinning (rigid transform):
   ```python
   # In visualizer, set bone_weights to None
   viz.bone_weights[0] = None
   viz.bone_indices[0] = None
   ```

### Issue: "Animation too fast/slow"

**Solution:**
```bash
# Adjust FPS
python pyvista_visualizer.py --fbx model.fbx --motion anim.npy --fps 60
```

---

## 📊 Performance Tips

### For Smooth Playback

1. **Reduce mesh complexity:**
   ```python
   import trimesh
   mesh = trimesh.load('model.fbx')
   simplified = mesh.simplify_quadratic_decimation(face_count=10000)
   simplified.export('model_lowpoly.obj')
   ```

2. **Optimize textures:**
   ```bash
   # Resize large textures
   convert large_texture.png -resize 2048x2048 optimized_texture.png
   ```

3. **Use GPU acceleration:**
   PyVista automatically uses GPU when available. Check:
   ```python
   import pyvista as pv
   print(pv.Report())  # Shows GPU info
   ```

### For Video Rendering

- Use `off_screen=True` for faster rendering
- Render at lower resolution first, then scale up
- Use parallel rendering for multiple views:
  ```python
  from concurrent.futures import ThreadPoolExecutor
  # Render frames in parallel
  ```

---

## 🎓 Advanced Customization

### Custom Shaders

PyVista supports custom shaders for advanced effects:

```python
# Example: Toon shading
import pyvista as pv

plotter = pv.Plotter()
mesh = pv.read('model.fbx')

# Apply toon shading
mesh.plot(lighting=False, color='lightblue', smooth_shading=False)
```

### Multi-View Rendering

```python
# Split screen with multiple cameras
plotter = pv.Plotter(shape=(1, 2))

# Left view
plotter.subplot(0, 0)
plotter.add_mesh(mesh, texture=diffuse)
plotter.camera_position = 'xy'

# Right view
plotter.subplot(0, 1)
plotter.add_mesh(mesh, texture=normal)
plotter.camera_position = 'xz'

plotter.show()
```

### Physics Simulation

Combine with PyBullet for physics:

```python
import pybullet as p

# Load mesh into physics sim
collision_shape = p.createCollisionShapeFromArray(mesh.vertices, mesh.faces)
body_id = p.createMultiBody(collision_shape)

# Simulate and visualize
# ... (advanced topic)
```

---

## 📚 Resources

### TrueBones
- **Product Page**: https://truebones.gumroad.com/l/skZMC
- **Discord**: Join for support and tutorials
- **Price**: $195 (or 20×$9.75/month)
- **License**: 100% Royalty-Free for commercial use

### Libraries
- **PyVista**: https://docs.pyvista.org/
- **Vedo**: https://vedo.embl.es/
- **Trimesh**: https://trimsh.org/
- **PyAssimp**: https://github.com/assimp/assimp

### Related
- **Blender**: https://www.blender.org/ (for FBX conversion)
- **iClone**: https://www.reallusion.com/iclone/ (alternative workflow)

---

## 🎯 Summary

### What You Can Do

✅ Load **full 3D animal models** from TrueBones FBX Zoo
✅ Apply **textures** (diffuse, normal, specular)
✅ Perform **skeletal skinning** for realistic deformation
✅ Play **BVH or NPY animations** in real-time
✅ **Interactive camera** controls (rotate, pan, zoom)
✅ **Export high-quality videos** for production

### Recommended Workflow

1. **Buy TrueBones FBX Zoo** ($195, 75+ animals)
2. **Install PyVista**: `pip install pyvista`
3. **Run visualizer**:
   ```bash
   python pyvista_visualizer.py --fbx model.fbx --motion animation.npy
   ```
4. **Enjoy beautiful 3D animations!**

---

## 💡 Next Steps

- Explore all 75+ animal models in TrueBones
- Generate custom motions with AnyTop
- Create production videos for your projects
- Experiment with textures and shaders
- Build custom workflows for your needs

Happy visualizing! 🎨✨
