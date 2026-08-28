#include <cmath>

// Резонансна частота контуру Колпітца за котушкою й парою конденсаторів.
// L — у генрі, C1, C2 — у фарадах; результат — у герцах.
float colpitts_freq(float L, float C1, float C2)
{
    float Cs = (C1 * C2) / (C1 + C2);     // послідовна ємність дільника
    return 1.0f / (2.0f * static_cast<float>(M_PI) * std::sqrt(L * Cs));
}
// colpitts_freq(1e-6f, 1000e-12f, 1000e-12f) -> ~7.12e6 Гц (7.12 МГц)
