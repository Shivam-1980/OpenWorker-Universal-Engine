#pragma once
#include <iostream>
#include <vector>
#include <memory>
#include <cmath>
#include <SDL.h>

// Forward declarations
class FluidSimulation;

struct Vec2 {
    float x, y;
    Vec2() : x(0), y(0) {}
    Vec2(float x, float y) : x(x), y(y) {}
    float length() const { return std::sqrt(x*x + y*y); }
    Vec2 operator+(const Vec2& v) const { return {x + v.x, y + v.y}; }
    Vec2 operator*(float s) const { return {x * s, y * s}; }
    Vec2 operator/(float s) const { return {x / s, y / s}; }
};

class FluidSimulation {
public:
    FluidSimulation(int width, int height)
        : width(width), height(height), velocityGrid(width * height, Vec2(0, 0)), pressureGrid(width * height, 0.0f) {}

    void Initialize(SDL_Renderer* renderer) {
        this->renderer = renderer;
        // Initialize velocity field with some turbulence
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                int index = y * width + x;
                velocityGrid[index] = Vec2(0.01f * (x - width/2), 0.01f * (y - height/2));
            }
        }
    }

    void Update(float dt) {
        // Apply forces (gravity)
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++s) {
                int index = y * width + x;
                velocityGrid[index] = velocityGrid[index] * (1.0f - viscosity * dt) + Vec2(0, -gravity * dt);
            }
        }

        // Semi-Lagrangian advection
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                int index = y * width + x;
                Vec2 pos = Vec2(x, y);
                Vec2 samplePos = pos - velocityGrid[index] * dt;
                int sampleX = std::clamp(static_cast<int>(samplePos.x), 0, width - 1);
                int sampleY = std::clamp(static_cast<int>(samplePos.y), 0, height - 1);
                velocityGrid[index] = velocityGrid[sampleY * width + sampleX];
            }
        }

        // Pressure projection (simple solver)
        std::vector<float> divergence(height * width, 0.0f);
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                int index = y * width + x;
                divergence[index] = 
                    (velocityGrid[index].x - velocityGrid[index].x) * 0.5f + 
                    (velocityGrid[index].y - velocityGrid[index].y) * 0.5f;
            }
        }

        std::vector<float> pressure(height * width, 0.0f);
        for (int iter = 0; iter < 10; ++iter) {
            for (int y = 0; y < height; ++y) {
                for (int x = 0; x < width; ++x) {
                    int index = y * width + x;
                    pressure[index] = 
                        (divergence[index] + 
                         (pressure[(y+1)*width +x] + pressure[(y-1)*width +x]) * 0.5f +
                         (pressure[y*width + (x+1)] + pressure[y*width + (x-1)]) * 0.5f) * dt;
                }
            }
        }

        // Apply pressure to velocity
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                int index = y * width + x;
                velocityGrid[index] = velocityGrid[index] - 
                    Vec2(pressure[index] - pressure[(y+1)*width +x], 
                         pressure[index] - pressure[y*width + (x+1)]) * dt;
            }
        }
    }

    void Render() {
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
        SDL_RenderClear(renderer);

        SDL_SetRenderDrawColor(renderer, 0, 255, 0, 255);
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                int index = y * width + x;
                Vec2 v = velocityGrid[index];
                float mag = v.length();
                if (mag > 0.1f) {
                    SDL_SetRenderDrawColor(renderer, 
                        static_cast<Uint8>(mag * 255.0f), 
                        static_cast<Uint8>(mag * 255.0f), 
                        static_cast<Uint8>(mag * 255.0f), 255);
                    SDL_RenderDrawPoint(renderer, x, y);
                }
            }
        }

        SDL_RenderPresent(renderer);
    }

private:
    int width, height;
    std::vector<Vec2> velocityGrid;
    std::vector<float> pressureGrid;
    SDL_Renderer* renderer;
    static constexpr float gravity = 9.81f;
    static constexpr float viscosity = 0.1f;
};

int main(int argc, char* argv[]) {
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        std::cerr << "SDL init failed: " << SDL_GetError() << std::endl;
        return 1;
    }

    const int width = 800;
    const int height = 600;
    SDL_Window* window = SDL_CreateWindow("Fluid Simulation", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width, height, 0);
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);

    FluidSimulation simulation(width, height);
    simulation.Initialize(renderer);

    const float dt = 1.0f / 60.0f;
    Uint32 lastTime = SDL_GetTicks();
    while (true) {
        Uint32 currentTime = SDL_GetTicks();
        float deltaTime = (currentTime - lastTime) / 1000.0f;
        lastTime = currentTime;

        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                goto cleanup;
            }
        }

        simulation.Update(deltaTime);
        simulation.Render();
    }

cleanup:
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}