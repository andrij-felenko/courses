#include <cmath>
#include <numbers>
#include <print>

constexpr float C_SOUND = 343.0f;    // швидкість звуку при 20 °C, м/с
constexpr float PI = std::numbers::pi_v<float>;

// Довжина круглого порту (метри) під настройку fb.
// V_litres — об'єм коробки; d_m — діаметр порту в метрах.
float port_length_m(float fb, float V_litres, float d_m)
{
    float V = V_litres * 1e-3f;              // літри → м³
    float r = d_m * 0.5f;
    float A = PI * r * r;                    // площа перерізу, м²
    float w = 2.0f * PI * fb;                // кутова частота

    float L_eff  = C_SOUND * C_SOUND * A / (w * w * V);  // ефективна довжина
    float L_end  = 2.0f * 0.85f * r;         // поправка: ~0.85·d, обидва кінці
    float L_phys = L_eff - L_end;            // стільки різати трубу
    return L_phys;
}

int main()
{
    float fb = 35.0f, V = 30.0f, d = 0.05f;
    float L = port_length_m(fb, V, d);
    std::println("Фізична довжина порту = {:.1f} см", L * 100.0f);
}
