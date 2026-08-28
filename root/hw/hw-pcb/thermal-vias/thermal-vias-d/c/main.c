#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Розрахунок теплового балансу вузла друкованої плати
typedef struct {
    double pcb_thickness_m;      // Товщина плати (h), м
    double via_drill_m;          // Діаметр отвору via (d), м
    double via_copper_thk_m;     // Товщина металізації via (t), м
    int    via_count;            // Кількість отворів у матриці (N)
    double r_jc_k_w;             // Опір кристал-корпус (R_theta_JC), К/Вт
    double r_tim_k_w;            // Опір термопрокладки (R_theta_TIM), К/Вт
    double r_heatsink_k_w;       // Опір радіатора (R_theta_SA), К/Вт
    double ambient_temp_c;       // Температура середовища (T_A), °C
    double power_dissipation_w;  // Потужність, що розсіюється (P), Вт
} ThermalCircuitConfig;

typedef struct {
    double r_single_via_k_w;
    double r_via_array_k_w;
    double r_total_ja_k_w;
    double junction_temp_c;
    bool   is_safe;
} ThermalCircuitResult;

ThermalCircuitResult solve_pcb_thermal(const ThermalCircuitConfig *cfg) {
    const double k_copper = 385.0; // Вт/(м·К)
    ThermalCircuitResult res;

    // Площа поперечного перерізу мідної гільзи: A = pi * (d*t - t^2)
    double d = cfg->via_drill_m;
    double t = cfg->via_copper_thk_m;
    double a_copper = M_PI * (d * t - t * t);

    // Опір одного via та масиву
    res.r_single_via_k_w = cfg->pcb_thickness_m / (k_copper * a_copper);
    res.r_via_array_k_w  = res.r_single_via_k_w / (double)cfg->via_count;

    // Сумарний тепловий опір (додаємо типовий опір розтікання у міді 3.0 К/Вт і припій 0.1 К/Вт)
    double r_pcb_extras = 3.1;
    res.r_total_ja_k_w = cfg->r_jc_k_w + res.r_via_array_k_w + r_pcb_extras + 
                         cfg->r_tim_k_w + cfg->r_heatsink_k_w;

    // Температура напівпровідникового переходу T_J
    res.junction_temp_c = cfg->ambient_temp_c + cfg->power_dissipation_w * res.r_total_ja_k_w;
    res.is_safe = (res.junction_temp_c <= 125.0);

    return res;
}

int main(void) {
    ThermalCircuitConfig cfg = {
        .pcb_thickness_m     = 0.0016, // 1.6 мм
        .via_drill_m         = 0.0003, // 0.3 мм
        .via_copper_thk_m    = 0.000025, // 25 мкм
        .via_count           = 16,     // Матриця 4x4
        .r_jc_k_w            = 2.0,    // 2.0 К/Вт
        .r_tim_k_w           = 3.0,    // 3.0 К/Вт
        .r_heatsink_k_w      = 6.0,    // 6.0 К/Вт
        .ambient_temp_c      = 25.0,   // 25 °C
        .power_dissipation_w = 4.6     // 4.6 Вт
    };

    ThermalCircuitResult r = solve_pcb_thermal(&cfg);

    printf("Одиничний via: R_th = %.1f K/W\n", r.r_single_via_k_w);
    printf("Матриця 16 via: R_th = %.2f K/W\n", r.r_via_array_k_w);
    printf("Повний опір R_th(JA): %.2f K/W\n", r.r_total_ja_k_w);
    printf("Температура кристала T_J: %.1f C (%s)\n", 
           r.junction_temp_c, r.is_safe ? "НОРМА" : "ПЕРЕГРІВ!");

    return 0;
}
