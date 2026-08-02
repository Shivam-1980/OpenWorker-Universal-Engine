#pragma once

#include <d3d12.h>
#include <memory>

// Command list management
class CommandList {
public:
    CommandList(DirectXDevice* device);
    ~CommandList();

    void Begin();
    void End();
    void Execute();

private:
    DirectXDevice* device;
    ID3D12GraphicsCommandList* commandList;
    ID3D12CommandAllocator* commandAllocator;
    ID3D12Fence* fence;
    UINT64 fenceValue;
};