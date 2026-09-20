#include <cmath>
#include <algorithm>

struct Vector2D {
    float x{0.0f};
    float y{0.0f};
};

Vector2D processScaledRadialDeadzone(float xIn, float yIn, float dMin, float dMax, float gamma) {
    float r = std::sqrt(xIn * xIn + yIn * yIn);
    if (r <= dMin || r < 1e-6f) {
        return {0.0f, 0.0f};
    }
    
    float rNorm = std::clamp((r - dMin) / (dMax - dMin), 0.0f, 1.0f);
    float rScaled = std::pow(rNorm, gamma);
    return {(xIn / r) * rScaled, (yIn / r) * rScaled};
}
