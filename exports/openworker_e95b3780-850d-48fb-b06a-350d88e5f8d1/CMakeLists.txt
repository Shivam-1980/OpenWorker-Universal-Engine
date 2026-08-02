cmake_minimum_required(VERSION 3.16)
project(DirectX12Renderer CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

file(GLOB_RECURSE SOURCES "src/*.cpp")
file(GLOB_RECURSE HEADERS "include/*.h" "src/rendering/*.h")

# Build as a Windows GUI application (WinMain entry point)
add_executable(${PROJECT_NAME} WIN32 ${SOURCES} ${HEADERS})

target_include_directories(${PROJECT_NAME} PRIVATE include src src/rendering)
target_link_libraries(${PROJECT_NAME} PRIVATE d3d12.lib dxgi.lib d3dcompiler.lib dxguid.lib)