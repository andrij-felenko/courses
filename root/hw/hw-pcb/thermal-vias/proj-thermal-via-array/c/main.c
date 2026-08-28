#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Константи матеріалів
#define K_COPPER 385.0       // Теплопровідність міді, Вт/(м·К)
#define K_SOLDER 58.0        // Теплопровідність припою SAC305, Вт/(м·К)

// Вхідні геометричні та теплові параметри
typedef struct {
    double pcb_thickness_m;      // Товщина плати (h), м
    double via_drill_diam_m;     // Діаметр свердла via (d), м
    double via_plating_thk_m;    // Товщина міднення стінки (t), м
    int    via_count;            // Кількість отворів (N)
    double pad_side_a_m;         // Сторона прямокутного термопада (a), м
    double pad_side_b_m;         // Сторона прямокутного термопада (b), м
    double plane_radius_m;       // Ефективний радіус розтікання міді, м
    double plane_copper_thk_m;   // Товщина мідного полігону, м
    double r_jc_k_w;             // Опір кристал-корпус (R_theta_JC), К/Вт
    double r_tim_k_w;            // Опір термоінтерфейсу (R_theta_TIM), К/Вт
    double r_hs_k_w;             // Опір радіатора (R_theta_HS), К/Вт
    double ambient_temp_c;       // Температура середовища (T_A), °C
    double power_dissipation_w;  // Потужність розсіювання (P), Вт
} ThermalParams;

// Результати розрахунку
typedef struct {
    double single_via_area_m2;
    double single_via_rth_k_w;
    double array_rth_k_w;
    double solder_rth_k_w;
    double plane_spread_rth_k_w;
    double total_rth_ja_k_w;
    double junction_temp_c;
    bool   solder_wicking_risk;
    bool   is_safe_temp;
} ThermalReport;

// Функція розрахунку теплового режиму
ThermalReport calculate_thermal_profile(const ThermalParams *p) {
    ThermalReport rep;
    
    // 1. Площа поперечного перерізу та опір одного via
    double d = p->via_drill_diam_m;
    double t = p->via_plating_thk_m;
    rep.single_via_area_m2 = M_PI * (d * t - t * t);
    rep.single_via_rth_k_w = p->pcb_thickness_m / (K_COPPER * rep.single_via_area_m2);
    
    // 2. Паралельний опір масиву
    rep.array_rth_k_w = rep.single_via_rth_k_w / (double)p->via_count;
    
    // 3. Опір шару припою (товщина 50 мкм)
    double pad_area = p->pad_side_a_m * p->pad_side_b_m;
    double solder_thk = 5.0e-5; // 50 мкм
    rep.solder_rth_k_w = solder_thk / (K_SOLDER * pad_area);
    
    // 4. Опір розтікання на нижній площині
    double r_pad_eff = sqrt(pad_area / M_PI);
    if (p->plane_radius_m > r_pad_eff && p->plane_copper_thk_m > 0.0) {
        rep.plane_spread_rth_k_w = log(p->plane_radius_m / r_pad_eff) / 
                                   (2.0 * M_PI * K_COPPER * p->plane_copper_thk_m);
    } else {
        rep.plane_spread_rth_k_w = 0.0;
    }
    
    // 5. Сумарний тепловий опір
    rep.total_rth_ja_k_w = p->r_jc_k_w + rep.solder_rth_k_w + rep.array_rth_k_w + 
                           rep.plane_spread_rth_k_w + p->r_tim_k_w + p->r_hs_k_w;
    
    // 6. Температура переходу
    rep.junction_temp_c = p->ambient_temp_c + p->power_dissipation_w * rep.total_rth_ja_k_w;
    
    // 7. Технологічні прапорці
    rep.solder_wicking_risk = (p->via_drill_diam_m > 3.5e-4); // d > 0.35 мм
    rep.is_safe_temp = (rep.junction_temp_c <= 125.0);        // ліміт 125 °C
    
    return rep;
}

int main(void) {
    ThermalParams config = {
        .pcb_thickness_m     = 1.6e-3,   // 1.6 мм
        .via_drill_diam_m    = 3.0e-4,   // 0.3 мм
        .via_plating_thk_m   = 2.5e-5,   // 25 мкм
        .via_count           = 16,       // матриця 4x4
        .pad_side_a_m        = 5.0e-3,   // 5 мм
        .pad_side_b_m        = 5.0e-3,   // 5 мм
        .plane_radius_m      = 2.5e-2,   // 25 мм
        .plane_copper_thk_m  = 3.5e-5,   // 35 мкм (1 oz)
        .r_jc_k_w            = 2.0,      // 2.0 К/Вт
        .r_tim_k_w           = 3.0,      // 3.0 К/Вт (термопрокладка)
        .r_hs_k_w            = 6.0,      // 6.0 К/Вт (невеликий радіатор)
        .ambient_temp_c      = 25.0,     // 25 °C
        .power_dissipation_w = 4.6       // 4.6 Вт
    };
    
    ThermalReport report = calculate_thermal_profile(&config);
    
    printf("=== ЗВІТ ТЕПЛОВОГО РОЗРАХУНКУ ===\n");
    printf("Одиничний via: площа Cu = %.4f мм2, R_th = %.2f К/Вт\n", 
           report.single_via_area_m2 * 1.0e6, report.single_via_rth_k_w);
    printf("Масив із %d via: R_th = %.2f К/Вт\n", config.via_count, report.array_rth_k_w);
    printf("Шар припою: R_th = %.3f К/Вт\n", report.solder_rth_k_w);
    printf("Розтікання у міді: R_th = %.2f К/Вт\n", report.plane_spread_rth_k_w);
    printf("Повний опір R_th(JA): %.2f К/Вт\n", report.total_rth_ja_k_w);
    printf("Температура кристала T_J: %.2f °C\n", report.junction_temp_c);
    printf("Ризик втягування припою: %s\n", report.solder_wicking_risk ? "ТАК (d > 0.35 мм!)" : "НІ (норма)");
    printf("Статус безпеки кристала: %s\n", report.is_safe_temp ? "НОРМА (T_J <= 125 °C)" : "ПЕРЕГРІВ!");
    
    return 0;
}
