#pragma once

#include <d3d12.h>
#include <dxgi1_4.h>
#include <memory>

// DirectX 12 device management
class DirectXDevice {
public:
    DirectXDevice();
    ~DirectXDevice();

    ID3D12Device* GetDevice() const { return device; }
    ID3D12CommandQueue* GetCommandQueue() const { return commandQueue; }

private:
    ID3D12Device* device;
    ID3D12CommandQueue* commandQueue;
    std::vector<ID3D12CommandAllocator*> commandAllocators;
    std::vector<ID3D12Fence*> fences;
    UINT64 currentFenceValue;
};

// Explicit memory allocation
class MemoryManager {
public:
    MemoryManager();
    ~MemoryManager();

    ID3D12Heap* AllocateGpuMemory(size_t size, D3D12_HEAP_TYPE type);
    ID3D12Heap* AllocateCpuMemory(size_t size);

private:
    ID3D12Heap* cpuHeap;
    ID3D12Heap* gpuHeap;
};