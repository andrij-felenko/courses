#include <math.h>

typedef struct {
    float ias_mps;   // приладова нестислива швидкість (м/с)
    float cas_mps;   // калібрована швидкість Сен-Венана (м/с)
    float tas_mps;   // істинна повітряна швидкість (м/с)
    float mach;      // число Маха
    float density;   // дійсна густина повітря (кг/м³)
} AirspeedCascade;

AirspeedCascade calculate_airspeeds(float delta_p_pa, float p_static_pa, float temp_c) {
    AirspeedCascade res;
    const float P0 = 101325.0f;        // тиск на рівні моря ISA (Па)
    const float RHO0 = 1.2250f;        // густина на рівні моря ISA (кг/м³)
    const float A0 = 340.294f;         // швидкість звуку ISA (м/с)
    const float R_SPEC = 287.058f;     // газова стала повітря (Дж/(кг·К))
    const float GAMMA_EXP = 2.0f / 7.0f; // (gamma - 1) / gamma для gamma = 1.4

    if (delta_p_pa < 0.0f) delta_p_pa = 0.0f;
    if (p_static_pa < 1000.0f) p_static_pa = P0;

    // 1. Приладова швидкість (неврахована стисливість)
    res.ias_mps = sqrtf((2.0f * delta_p_pa) / RHO0);

    // 2. Калібрована швидкість Сен-Венана
    float ratio_p0 = (delta_p_pa / P0) + 1.0f;
    res.cas_mps = A0 * sqrtf(5.0f * (powf(ratio_p0, GAMMA_EXP) - 1.0f));

    // 3. Число Маха за статичним тиском
    float ratio_stat = (delta_p_pa / p_static_pa) + 1.0f;
    res.mach = sqrtf(5.0f * (powf(ratio_stat, GAMMA_EXP) - 1.0f));

    // 4. Дійсна густина повітря
    float t_kelvin = temp_c + 273.15f;
    res.density = p_static_pa / (R_SPEC * t_kelvin);

    // 5. Істинна швидкість TAS (точна з поправкою на густину)
    res.tas_mps = res.cas_mps * sqrtf(RHO0 / res.density);

    return res;
}
