#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define AIR_DENSITY_SEA_LEVEL 1.225f /* кг/м³ */
#define PI_F                  3.14159265358979323846f
#define GRAVITY_M_S2          9.80665f

typedef struct {
    float thrust_newtons;    /* необхідна тяга одного гвинта, Н */
    float radius_meters;     /* радіус гвинта, м */
    float air_density;       /* густина повітря, кг/м³ */
    float figure_of_merit;   /* очікуваний FM (0.50..0.85) */
} HoverInput;

typedef struct {
    float disk_area_m2;      /* площа диска A, м² */
    float disk_loading_pa;   /* навантаження на диск DL = T/A, Па */
    float induced_vel_m_s;   /* індукована швидкість на диску v_i, м/с */
    float wake_vel_m_s;      /* швидкість у сліді w = 2*v_i, м/с */
    float ideal_power_watts; /* ідеальна індукована потужність P_i, Вт */
    float actual_shaft_watts;/* реальна механічна потужність P_shaft, Вт */
    float power_loading_n_kw;/* питома тяга, Н/кВт */
    float power_loading_g_w; /* питома тяга, г/Вт */
} HoverOutput;

bool calculate_hover_performance(const HoverInput* in, HoverOutput* out) {
    if (!in || !out) return false;
    if (in->thrust_newtons <= 0.0f || in->radius_meters <= 0.0f) return false;
    if (in->air_density <= 0.0f || in->figure_of_merit <= 0.0f || in->figure_of_merit > 1.0f) return false;

    float A = PI_F * in->radius_meters * in->radius_meters;
    float T = in->thrust_newtons;
    float rho = in->air_density;

    float DL = T / A;
    /* v_i = sqrt( T / (2 * rho * A) ) */
    float v_i = sqrtf(T / (2.0f * rho * A));
    float w = 2.0f * v_i;

    /* P_i = T * v_i */
    float P_ideal = T * v_i;
    float P_shaft = P_ideal / in->figure_of_merit;

    float PL_N_kW = (T / P_shaft) * 1000.0f;
    float PL_g_W = (T / (P_shaft * GRAVITY_M_S2)) * 1000.0f;

    out->disk_area_m2 = A;
    out->disk_loading_pa = DL;
    out->induced_vel_m_s = v_i;
    out->wake_vel_m_s = w;
    out->ideal_power_watts = P_ideal;
    out->actual_shaft_watts = P_shaft;
    out->power_loading_n_kw = PL_N_kW;
    out->power_loading_g_w = PL_g_W;

    return true;
}

int main(void) {
    /* Порівняння трьох конфігурацій для створення тяги T = 10 Н (на один мотор) */
    const char* names[] = {
        "5-дюймовий гоночний гвинт (R = 6.35 см)",
        "15-дюймовий дрон (R = 19.05 см)",
        "30-дюймовий вантажний ротор (R = 38.1 см)"
    };
    float radii[] = { 0.0635f, 0.1905f, 0.3810f };
    float fms[]   = { 0.55f,   0.68f,   0.75f };

    printf("=== Розрахунок висіння за теорією імпульсу (T = 10.0 Н на гвинт) ===\n\n");

    for (int i = 0; i < 3; ++i) {
        HoverInput input = {
            .thrust_newtons = 10.0f,
            .radius_meters = radii[i],
            .air_density = AIR_DENSITY_SEA_LEVEL,
            .figure_of_merit = fms[i]
        };
        HoverOutput res;

        if (calculate_hover_performance(&input, &res)) {
            printf("[%s]\n", names[i]);
            printf("  Площа диска A:          %.4f м²\n", res.disk_area_m2);
            printf("  Навантаження на диск DL: %6.1f Па (Н/м²)\n", res.disk_loading_pa);
            printf("  Швидкість на диску v_i:  %5.2f м/с (у сліді w: %.2f м/с)\n", res.induced_vel_m_s, res.wake_vel_m_s);
            printf("  Ідеальна потужність P_i: %6.1f Вт\n", res.ideal_power_watts);
            printf("  Потужність на валу P:   %6.1f Вт (FM = %.2f)\n", res.actual_shaft_watts, fms[i]);
            printf("  Питома тяга:             %5.1f Н/кВт (%.2f г/Вт)\n\n", res.power_loading_n_kw, res.power_loading_g_w);
        }
    }

    return 0;
}
