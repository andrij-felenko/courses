#include <iostream>
#include <cassert>

using namespace drone::control;

void test_quad_cpp() {
    typename ControlAllocator<4>::Config cfg{};
    cfg.minLimits.fill(0.0f);
    cfg.maxLimits.fill(1.0f);

    // Псевдообернена матриця Quad-X
    cfg.pseudoInverse = {{
        { 0.25f,  0.25f,   0.25f,   0.25f },
        { 0.25f,  0.25f,  -0.25f,  -0.25f },
        { 0.25f, -0.25f,   0.25f,  -0.25f },
        { 0.25f, -0.25f,  -0.25f,   0.25f }
    }};

    ControlAllocator<4> allocator(cfg);

    // Тест: Режим висіння з маневром крену
    std::array<float, 4> tau{ 2.0f, 0.4f, 0.0f, 0.0f };
    auto u = allocator.allocate(tau);

    assert(u[0] == 0.6f); // 0.5 + 0.1
    assert(u[1] == 0.6f); // 0.5 + 0.1
    assert(u[2] == 0.4f); // 0.5 - 0.1
    assert(u[3] == 0.4f); // 0.5 - 0.1
}

int main() {
    test_quad_cpp();
    return 0;
}
