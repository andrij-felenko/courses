#include <cmath>
#include <algorithm>

namespace FlightDynamics {

struct AirspeedCascade {
    float ias_mps{0.0f};   // приладова нестислива швидкість (м/с)
    float cas_mps{0.0f};   // калібрована швидкість Сен-Венана (м/с)
    float tas_mps{0.0f};   // істинна повітряна швидкість (м/с)
    float mach{0.0f};      // число Маха
    float density{1.225f}; // дійсна густина повітря (кг/м³)
};

constexpr float P0_ISA = 101325.0f;        // Па
constexpr float RHO0_ISA = 1.2250f;        // кг/м³
constexpr float A0_ISA = 340.294f;         // м/с
constexpr float R_SPECIFIC = 287.058f;     // Дж/(кг·К)
constexpr float GAMMA_EXP = 2.0f / 7.0f;   // (1.4 - 1) / 1.4

[[nodiscard]] inline AirspeedCascade calculateAirspeeds(
    float delta_p_pa, 
    float p_static_pa = P0_ISA, 
    float temp_c = 15.0f) noexcept 
{
    AirspeedCascade res;
    const float dp = std::max(0.0f, delta_p_pa);
    const float p_stat = (p_static_pa > 1000.0f) ? p_static_pa : P0_ISA;

    // 1. Приладова швидкість (IAS)
    res.ias_mps = std::sqrt((2.0f * dp) / RHO0_ISA);

    // 2. Калібрована швидкість Сен-Венана (CAS)
    const float ratio_p0 = (dp / P0_ISA) + 1.0f;
    res.cas_mps = A0_ISA * std::sqrt(5.0f * (std::pow(ratio_p0, GAMMA_EXP) - 1.0f));

    // 3. Число Маха
    const float ratio_stat = (dp / p_stat) + 1.0f;
    res.mach = std::sqrt(5.0f * (std::pow(ratio_stat, GAMMA_EXP) - 1.0f));

    // 4. Дійсна густина повітря
    const float t_kelvin = temp_c + 273.15f;
    res.density = p_stat / (R_SPECIFIC * t_kelvin);

    // 5. Істинна швидкість (TAS)
    res.tas_mps = (res.density > 0.05f) 
                  ? res.cas_mps * std::sqrt(RHO0_ISA / res.density) 
                  : res.cas_mps;

    return res;
}

} // namespace FlightDynamics
