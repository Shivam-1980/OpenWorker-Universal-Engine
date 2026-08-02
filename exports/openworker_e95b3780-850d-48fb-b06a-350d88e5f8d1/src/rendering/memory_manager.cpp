#include "memory_manager.h"
#include "device.h"
#include "swapchain.h"
#include "command_list.h"

MemoryManager::MemoryManager(DirectXDevice* device)
    : device(device)
{
    // Create GPU heap
    device->GetDevice()->CreateHeap(
        D3D12_HEAP_TYPE_DEFAULT,
        1024 * 1024 * 1024, // 1GB
        0,
        IID_PPV_ARGS(&gpuHeap));

    // Create CPU heap
    device->GetDevice()->CreateHeap(
        D3D12_HEAP_TYPE_UPLOAD,
        1024 * 1024 * 1024, // 1GB
        0,
        IID_PPV_ARGS(&cpuHeap));
}

MemoryManager::~MemoryManager()
{
    // Release heaps
    gpuHeap->Release();
    cpuHeap->Release();
}

void* MemoryManager::AllocateGpuMemory(size_t size)
{
    void* ptr;
    gpuHeap->AllocateFromHeap(
        size,
        0,
        &ptr);
    allocatedMemory[ptr] = size;
    return ptr;
}

void* MemoryManager::AllocateCpuMemory(size_t size)
{
    void* ptr;
    cpuHeap->AllocateFromHeap(
        size,
        0,
        &ptr);
    allocatedMemory[ptr] = size;
    return ptr;
}

void MemoryManager::FreeMemory(void* ptr)
{
    if (allocatedMemory.find(ptr) != allocatedMemory.end()) {
        allocatedMemory.erase(ptr);
        // Add code to properly release the memory resource
    }
}