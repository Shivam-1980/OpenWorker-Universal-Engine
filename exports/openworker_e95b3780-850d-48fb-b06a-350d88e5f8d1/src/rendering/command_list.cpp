#include "command_list.h"
#include "device.h"
#include "swapchain.h"
#include "memory_manager.h"

CommandList::CommandList(DirectXDevice* device)
    : device(device)
{
    // Create command allocator
    device->GetDevice()->CreateCommandAllocator(
        D3D12_COMMAND_LIST_TYPE_DIRECT,
        IID_PPV_ARGS(&commandAllocator));

    // Create command list
    device->GetDevice()->CreateCommandList(
        0,
        D3D12_COMMAND_LIST_TYPE_DIRECT,
        commandAllocator,
        nullptr,
        IID_PPV_ARGS(&commandList));

    // Create fence for synchronization
    device->GetDevice()->CreateFence(
        0,
        D3D12_FENCE_FLAG_SHARED |
        D3D12_FENCE_FLAG_SIGNALED,
        IID_PPV_ARGS(&fence));
}

void CommandList::Begin()
{
    // Reset command allocator
    commandAllocator->Reset();

    // Reset command list
    commandList->Reset(commandAllocator, nullptr);

    // Begin recording commands
    commandList->BeginCommandList();
}

void CommandList::End()
{
    // End recording commands
    commandList->EndCommandList();
}

void CommandList::Execute()
{
    // Execute command list
    device->GetCommandQueue()->ExecuteCommandLists(1, &commandList);

    // Signal fence
    fenceValue++;
    fence->Signal(fenceValue, 0);

    // Wait for fence
    while (fence->GetCompletedValue() < fenceValue)
    {
        Sleep(1);
    }
}