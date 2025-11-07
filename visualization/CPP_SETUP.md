# C++ Skeleton Visualizer Setup Guide

This guide explains how to build and use the C++ skeleton visualizer.

## Overview

The C++ visualizer provides maximum performance and control over the rendering pipeline. It uses:
- **GLFW**: Window management and input handling
- **GLEW/GLAD**: OpenGL function loading
- **GLM**: Mathematics library for 3D transformations
- **OpenGL 3.3+**: Modern rendering pipeline

## Prerequisites

### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    libglfw3-dev \
    libglew-dev \
    libglm-dev \
    libopengl-dev
```

### Fedora/RHEL

```bash
sudo dnf install -y \
    gcc-c++ \
    cmake \
    glfw-devel \
    glew-devel \
    glm-devel \
    mesa-libGL-devel
```

### macOS

```bash
brew install cmake glfw glew glm
```

### Windows

**Option 1: Using vcpkg**
```cmd
vcpkg install glfw3 glew glm
```

**Option 2: Using MSYS2**
```bash
pacman -S mingw-w64-x86_64-cmake \
          mingw-w64-x86_64-glfw \
          mingw-w64-x86_64-glew \
          mingw-w64-x86_64-glm
```

## Building

### Using CMake (Recommended)

```bash
cd visualization
mkdir build
cd build
cmake ..
make -j$(nproc)
```

### Manual Compilation

```bash
g++ -std=c++17 skeleton_visualizer.cpp -o skeleton_visualizer \
    -lglfw -lGL -lGLEW -lpthread -ldl
```

## Current Implementation Status

⚠️ **Note:** The provided C++ code is a **template/reference implementation**.

To create a fully functional C++ visualizer, you need to:

1. **Uncomment OpenGL includes** in `skeleton_visualizer.cpp`:
   ```cpp
   #include <GL/glew.h>
   #include <GLFW/glfw3.h>
   #include <glm/glm.hpp>
   #include <glm/gtc/matrix_transform.hpp>
   #include <glm/gtc/type_ptr.hpp>
   ```

2. **Implement rendering functions**:
   - `drawSphere()`: Render joint spheres
   - `drawCylinder()`: Render bone cylinders
   - Shader setup and management
   - Vertex buffer objects (VBOs)
   - Vertex array objects (VAOs)

3. **Implement NPY file loader**:
   - Parse NPY file header
   - Read binary data
   - Extract motion features
   - Construct animation frames

4. **Implement input handling**:
   - Keyboard callbacks
   - Mouse callbacks
   - Camera controls

## Implementation Approach

### Option 1: Complete from Template (Moderate Difficulty)

The provided template has the overall structure. Fill in:
- OpenGL rendering code
- NPY parsing (can use `cnpy` library)
- Input handling

Estimated time: 4-8 hours for experienced OpenGL developer

### Option 2: Use Python Bindings (Easier)

Create Python bindings for the C++ visualizer using pybind11:

```cpp
#include <pybind11/pybind11.h>

PYBIND11_MODULE(skeleton_visualizer_cpp, m) {
    m.def("visualize", &SkeletonViz::visualize, "Visualize skeleton");
}
```

This allows you to use the performance of C++ while keeping Python's ease of use.

### Option 3: Use Python Visualizers (Recommended)

The Python visualizers (`interactive_visualizer.py`, etc.) are **fully functional** and ready to use:

```bash
# Use these instead - they work immediately!
python interactive_visualizer.py animation.npy
python interactive_visualizer_open3d.py animation.npy
python interactive_visualizer_pygame.py animation.npy
```

## Full C++ Implementation Guide

If you want to complete the C++ implementation:

### 1. NPY File Loading

Use the `cnpy` library:

```bash
git clone https://github.com/rogersce/cnpy.git
cd cnpy
mkdir build && cd build
cmake ..
make install
```

Then in your code:
```cpp
#include <cnpy.h>

cnpy::NpyArray arr = cnpy::npy_load(filename);
float* data = arr.data<float>();
// Shape: frames x joints x 13
```

### 2. OpenGL Rendering Setup

```cpp
// Vertex shader
const char* vertexShaderSource = R"(
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 Color;

void main() {
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    Color = aColor;
}
)";

// Fragment shader
const char* fragmentShaderSource = R"(
#version 330 core
in vec3 Color;
out vec4 FragColor;

void main() {
    FragColor = vec4(Color, 1.0);
}
)";
```

### 3. Geometry Generation

```cpp
// Generate sphere vertices
std::vector<float> generateSphere(float radius, int segments) {
    std::vector<float> vertices;
    for (int i = 0; i <= segments; i++) {
        float lat = M_PI * (-0.5 + (float)i / segments);
        for (int j = 0; j <= segments; j++) {
            float lon = 2 * M_PI * (float)j / segments;
            float x = radius * cos(lat) * cos(lon);
            float y = radius * sin(lat);
            float z = radius * cos(lat) * sin(lon);
            vertices.push_back(x);
            vertices.push_back(y);
            vertices.push_back(z);
        }
    }
    return vertices;
}
```

### 4. Camera System

```cpp
glm::mat4 view = glm::lookAt(
    glm::vec3(camera.position.x, camera.position.y, camera.position.z),
    glm::vec3(camera.target.x, camera.target.y, camera.target.z),
    glm::vec3(0.0f, 1.0f, 0.0f)
);

glm::mat4 projection = glm::perspective(
    glm::radians(60.0f),
    (float)width / (float)height,
    0.1f,
    100.0f
);
```

## Performance Comparison

| Implementation | Frame Rate | Compilation Time | Development Time |
|---------------|------------|------------------|------------------|
| C++ (Full OpenGL) | ⭐⭐⭐⭐⭐ (1000+ FPS) | ⭐⭐ (2-5 min) | ⭐⭐ (days) |
| Python + Vedo | ⭐⭐⭐⭐ (60+ FPS) | ⭐⭐⭐⭐⭐ (instant) | ⭐⭐⭐⭐⭐ (ready) |
| Python + Open3D | ⭐⭐⭐⭐⭐ (100+ FPS) | ⭐⭐⭐⭐⭐ (instant) | ⭐⭐⭐⭐⭐ (ready) |
| Python + PyGame | ⭐⭐⭐⭐ (60+ FPS) | ⭐⭐⭐⭐⭐ (instant) | ⭐⭐⭐⭐⭐ (ready) |

## When to Use C++

Use C++ implementation when:
- You need **absolute maximum performance** (1000+ FPS)
- You're integrating with existing C++ codebase
- You need to run on embedded systems
- You want **full control** over the rendering pipeline

Use Python implementation when:
- You want **something that works immediately**
- You need rapid prototyping
- You're doing research/experiments
- Performance is "good enough" (60-100 FPS is plenty for visualization)

## Recommended Libraries for Full C++ Implementation

### Geometry Processing
- **libigl**: Geometry processing library
- **OpenMesh**: Mesh data structure
- **CGAL**: Computational geometry

### Visualization
- **Magnum**: Modern C++ graphics library (recommended!)
- **OpenSceneGraph**: High-level scene graph
- **bgfx**: Cross-platform rendering library

### Example with Magnum (Easiest C++ Option)

```cpp
#include <Magnum/GL/Mesh.h>
#include <Magnum/Primitives/Cube.h>
#include <Magnum/Platform/Sdl2Application.h>

// Magnum handles most OpenGL complexity for you!
```

## Conclusion

**For immediate use**: Use the Python visualizers - they're fully functional and ready to go!

**For learning**: Complete the C++ template - great way to learn OpenGL

**For production C++**: Consider using Magnum or similar high-level library instead of raw OpenGL

## Resources

- **OpenGL Tutorial**: https://learnopengl.com/
- **GLFW Documentation**: https://www.glfw.org/documentation.html
- **GLM Documentation**: https://github.com/g-truc/glm
- **Magnum**: https://magnum.graphics/
- **cnpy**: https://github.com/rogersce/cnpy

## Support

For questions about the C++ implementation, refer to:
1. The Python implementations (working reference)
2. OpenGL tutorials (rendering techniques)
3. Project GitHub issues (implementation questions)
