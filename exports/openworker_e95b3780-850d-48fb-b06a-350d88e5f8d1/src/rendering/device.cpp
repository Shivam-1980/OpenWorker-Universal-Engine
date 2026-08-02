#include "device.h"
#include "swapchain.h"
#include "command_list.h"
#include "memory_manager.h"

DirectXDevice::DirectXDevice()
{
    // Create D3D12 device with feature level 11_0
    D3D12CreateDevice(nullptr, D3D_FEATURE_LEVEL_11_0, IID_PPV_ARGS(&device));

    // Create direct command queue
    D3D12_COMMAND_QUEUE_DESC queueDesc = {0};
    queueDesc.Type = D3D12_COMMAND_QUEUE_TYPE_DIRECT;
    device->CreateCommandQueue(&queueDesc, IID_PPV_ARGS(&commandQueue));

    // Initialize command allocators
    for (UINT i = 0; i < 2; ++i)
    {
        device->CreateCommandAllocator(D3D12_COMMAND_LIST_TYPE_DIRECT, 
                                      IID_PPV_ARGS(&commandAllocators[i]));
    }

    // Initialize fences for synchronization
    for (UINT i = 0; i < 2; ++i)
    {
        ID3D12Fence* fence = nullptr;
        device->CreateFence(0, D3D12_FENCE_FLAG_SHARED, IID_PPV_ARGS(&fence));
        fences.push_back(fence);
    }
    currentFenceValue = 1;
}

DirectXDevice::~DirectXDevice()
{
    // Release all resources
    for (auto& allocator : commandAllocators)
        allocator->Release();
    for (auto& fence : fences)
        fence->Release();
    commandQueue->Release();
    device->Release();
}