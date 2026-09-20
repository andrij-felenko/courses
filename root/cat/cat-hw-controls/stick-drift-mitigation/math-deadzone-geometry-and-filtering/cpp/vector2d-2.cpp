#include <cmath>
#include <algorithm>
#include <array>

struct Vector2D {
    float x{0.0f};
    float y{0.0f};
};

class StickPipeline {
public:
    StickPipeline(float alpha, float dMin, float dMax, float gamma)
        : alpha_(alpha), dMin_(dMin), dMax_(dMax), gamma_(gamma) {}

    Vector2D process(float rawX, float rawY) {
        xBuf_[0] = xBuf_[1]; xBuf_[1] = xBuf_[2]; xBuf_[2] = rawX;
        yBuf_[0] = yBuf_[1]; yBuf_[1] = yBuf_[2]; yBuf_[2] = rawY;

        auto xSorted = xBuf_;
        auto ySorted = yBuf_;
        std::sort(xSorted.begin(), xSorted.end());
        std::sort(ySorted.begin(), ySorted.end());

        float medX = xSorted[1];
        float medY = ySorted[1];

        float r = std::sqrt(medX * medX + medY * medY);
        Vector2D scaled{0.0f, 0.0f};

        if (r > dMin_ && r > 1e-6f) {
            float rNorm = std::clamp((r - dMin_) / (dMax_ - dMin_), 0.0f, 1.0f);
            float rScaled = std::pow(rNorm, gamma_);
            scaled.x = (medX / r) * rScaled;
            scaled.y = (medY / r) * rScaled;
        }

        xEma_ += alpha_ * (scaled.x - xEma_);
        yEma_ += alpha_ * (scaled.y - yEma_);

        return {xEma_, yEma_};
    }

private:
    std::array<float, 3> xBuf_{0.0f, 0.0f, 0.0f};
    std::array<float, 3> yBuf_{0.0f, 0.0f, 0.0f};
    float xEma_{0.0f};
    float yEma_{0.0f};
    float alpha_;
    float dMin_;
    float dMax_;
    float gamma_;
};
