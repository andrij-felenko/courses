#include <algorithm>
#include <cmath>

constexpr float q10 = 2.0f;   // множник Арреніуса на +10 °C (консервативно)

// Поправка SoC на саморозряд за час сну (лінійна модель).
// k_ref — паспортний темп, %/місяць за t_ref_C (напр. 2.0 за 25 °C).
float self_discharge_loss(float k_ref, float t_ref_C,
                          float t_cell_C, float sleep_months)
{
    float k = k_ref * std::pow(q10, (t_cell_C - t_ref_C) / 10.0f);  // темп при T
    return k * sleep_months;                                        // втрата, %
}

// на пробудженні:
soc_percent -= self_discharge_loss(2.0f, 25.0f, temp_C, months_asleep);
soc_percent = std::max(soc_percent, 0.0f);
