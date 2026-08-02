#include "swapchain.h"
#include "device.h"
#include "command_list.h"
#include "memory_manager.h"

SwapChain::SwapChain(DirectXDevice* device)
    : device(device)
{
    // Create swapchain with 2 backbuffers
    DXGI_SWAP_CHAIN_DESC1 swapDesc = {0};
    swapDesc.BufferCount = 2;
    swapDesc.Width = 1920;
    swapDesc.Height = 1080;
    swapDesc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
    swapDesc.SampleDesc.Count = 1;
    swapDesc.SwapEffect = DXGI_SWAP_EFFECT_FLIP_DISCARD;
    swapDesc.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;

    // Create swapchain
    IDXGISwapChain3* tempSwapChain;
    device->GetDevice()->CreateSwapChainForHwnd(
        device->GetCommandQueue(),
        hwnd,
        &swapDesc,
        nullptr,
        nullptr,
        &tempSwapChain);

    // Query for IDXGISwapChain3 interface
    tempSwapChain->QueryInterface(
        IID_PPV_ARGS(&swapChain));
    tempSwapChain->Release();

    // Create backbuffers
    for (UINT i = 0; i < 2; ++i)
    {
        swapChain->GetBuffer(i, IID_PPV_ARGS(&backBuffers[i]));
    }

    // Create RTVs for backbuffers
    for (UINT i = 0; i < 2; ++i)
    {
        device->GetDevice()->CreateRenderTargetView(
            backBuffers[i],
            nullptr,
            &rtvs[i]);
    }

    // Create depth stencil texture
    CD3DX12_HEAP_PROPERTIES heapProps(D3D12_HEAP_TYPE_DEFAULT);
    CD3DX12_RESOURCE_DESC depthStencilDesc = CD3DX12_RESOURCE_DESC::Tex2D(
        DXGI_FORMAT_D24_UNORM_S8_UINT,
        1920,
        1080,
        1,
        1,
        1,
        D3D12_RESOURCE_FLAG_ALLOW_DEPTH_STENCIL);

    device->GetDevice()->CreateCommittedResource(
        &heapProps,
        D3D12_HEAP_FLAG_NONE,
        &depthStencilDesc,
        D3D12_RESOURCE_STATE_DEPTH_WRITE,
        nullptr,
        IID_PPV_ARGS(&depthStencilResource));

    // Create DSV
    device->GetDevice()->CreateDepthStencilView(
        depthStencilResource,
        &CD3DX12_DEPTH_STENCIL_VIEW_DESC::DepthStencilTarget,
        D3D12_DSV_DIMENSION_TEXTURE2D,
        &dsv);
}