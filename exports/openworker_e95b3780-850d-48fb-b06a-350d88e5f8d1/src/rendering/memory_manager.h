#pragma once

#include <d3d12.h>
#include <memory>

// Memory manager for explicit CPU/GPU memory allocation
class MemoryManager {
public:
    MemoryManager(DirectXDevice* device);
    ~MemoryManager();

    void* AllocateGpuMemory(size_t size);
    void* AllocateCpuMemory(size_t size);
    void FreeMemory(void* ptr);

private:
    DirectXDevice* device;
    ID3D12Heap* gpuHeap;
    ID3D12Heap* cpuHeap;
    std::unordered_map<void*, size_t> allocatedMemory;
};