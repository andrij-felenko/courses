#include <cstdint>

namespace atmospheric {

using Q16 = int32_t;

class MagnusCalculator {
public:
    // Інтерфейс для обчислень float32 (при наявності апаратного FPU)
    static float saturationVaporPressure(float temp, const MagnusParams& params) noexcept;
    static float dewPoint(float temp, float rh, const MagnusParams& params) noexcept;
    static float absoluteHumidity(float temp, float rh, const MagnusParams& params) noexcept;

    // Інтерфейс для обчислень Q16.16 (оптимізовано для МК без FPU)
    static Q16 saturationVaporPressure(Q16 temp, const MagnusParams& params) noexcept;
    static Q16 dewPoint(Q16 temp, Q16 rh, const MagnusParams& params) noexcept;
    static Q16 absoluteHumidity(Q16 temp, Q16 rh, const MagnusParams& params) noexcept;
};

} // namespace atmospheric
