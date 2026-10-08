#include <vector>
#include <algorithm>

class RtdCalculator {
public:
    struct LutEntry {
        float r;
        float t;
    };

    static float calcCvdPositive(float r_t, float r0, float a, float b) {
        float poly_term = 1.0f - (r_t / r0);
        float discriminant = (a * a) - (4.0f * b * poly_term);
        if (discriminant < 0.0f) {
            return -999.0f;
        }
        return (-a + std::sqrt(discriminant)) / (2.0f * b);
    }

    static float calcLut(float r_t, const LutEntry* lut, size_t size) {
        if (r_t <= lut[0].r) return lut[0].t;
        if (r_t >= lut[size - 1].r) return lut[size - 1].t;

        for (size_t i = 0; i < size - 1; ++i) {
            if (r_t >= lut[i].r && r_t <= lut[i + 1].r) {
                float r_diff = lut[i + 1].r - lut[i].r;
                float t_diff = lut[i + 1].t - lut[i].t;
                return lut[i].t + ((r_t - lut[i].r) * t_diff / r_diff);
            }
        }
        return 0.0f;
    }
};
