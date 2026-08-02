#pragma once

#include <d3d12.h>
#include <dxgi1_4.h>
#include <memory>

// Swapchain management
class SwapChain {
public:
    SwapChain(DirectXDevice* device);
    ~SwapChain();

    ID3D12Resource* GetBackBuffer(UINT index) const { return backBuffers[index]; }
    ID3D12RenderTargetView GetRTV(UINT index) const { return rtvs[index]; }
    ID3D12DepthStencilView GetDSV() const { return dsv; }

private:
    DirectXDevice* device;
    IDXGISwapChain3* swapChain;
    std::vector<ID3D12Resource*> backBuffers;
    std::vector<ID3D12RenderTargetView> rtvs;
    ID3D12DepthStencilView dsv;
};