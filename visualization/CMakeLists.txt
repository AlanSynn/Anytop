# CMakeLists.txt for C++ Skeleton Visualizer
cmake_minimum_required(VERSION 3.10)
project(SkeletonVisualizer VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(OpenGL REQUIRED)
find_package(glfw3 REQUIRED)
find_package(GLEW REQUIRED)

# Optional: Find GLM
find_package(glm QUIET)

# Source files
set(SOURCES
    skeleton_visualizer.cpp
)

# Create executable
add_executable(skeleton_visualizer ${SOURCES})

# Include directories
target_include_directories(skeleton_visualizer PRIVATE
    ${OPENGL_INCLUDE_DIR}
    ${GLEW_INCLUDE_DIRS}
)

# Link libraries
target_link_libraries(skeleton_visualizer
    ${OPENGL_LIBRARIES}
    glfw
    GLEW::GLEW
    pthread
    dl
)

# Optional: Link GLM if found
if(glm_FOUND)
    target_link_libraries(skeleton_visualizer glm::glm)
endif()

# Installation
install(TARGETS skeleton_visualizer DESTINATION bin)

# Print configuration
message(STATUS "")
message(STATUS "Configuration Summary:")
message(STATUS "  OpenGL: ${OPENGL_LIBRARIES}")
message(STATUS "  GLFW: Found")
message(STATUS "  GLEW: ${GLEW_LIBRARIES}")
message(STATUS "  GLM: ${glm_FOUND}")
message(STATUS "")
message(STATUS "Build Instructions:")
message(STATUS "  mkdir build && cd build")
message(STATUS "  cmake ..")
message(STATUS "  make")
message(STATUS "  ./skeleton_visualizer <path_to_npy_file>")
message(STATUS "")
