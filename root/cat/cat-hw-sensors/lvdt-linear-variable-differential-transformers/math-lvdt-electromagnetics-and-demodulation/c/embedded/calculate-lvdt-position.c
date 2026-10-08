// Обчислення ратіометричного значення та позиції LVDT у C
#include <math.h>

typedef struct {
    float k_m; // Конструктивна чутливість (1/мм)
} LvdtConfig;

float calculate_lvdt_position(float u_s1_rms, float u_s2_rms, const LvdtConfig *cfg) {
    float u_sum = u_s1_rms + u_s2_rms;
    if (u_sum < 1e-6f) {
        return 0.0f; // Захист від ділення на нуль
    }
    float r_ratio = (u_s1_rms - u_s2_rms) / u_sum;
    return r_ratio / cfg->k_m;
}
