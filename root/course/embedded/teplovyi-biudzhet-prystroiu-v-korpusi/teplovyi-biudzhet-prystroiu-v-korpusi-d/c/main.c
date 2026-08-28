#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define STEFAN_BOLTZMANN 5.670374e-8

typedef struct {
    double length_m;
    double width_m;
    double height_m;
    double wall_thick_m;
    double wall_k;          // Теплопровідність стінки (Вт/(м·К))
    double wall_emissivity; // Емісійна здатність поверхні
    double t_ambient_c;     // Температура довкілля (°C)
} Enclosure;

typedef struct {
    double p_watts;         // Теплові втрати (Вт)
    double r_th_jc;         // Опір кристал-корпус (°C/Вт)
    double r_th_bridge;     // Опір термомосту на стінку (°C/Вт)
    double t_j_max_c;       // Межа кристала (°C)
} Component;

typedef struct {
    double t_wall_out_c;
    double t_wall_in_c;
    double t_case_c;
    double t_junction_c;
    double r_th_ext;
    bool   is_safe;
} Result;

bool calculate_temperatures(const Enclosure *enc, const Component *comp, Result *res) {
    double a_vert = 2.0 * (enc->length_m + enc->width_m) * enc->height_m;
    double a_horiz = 2.0 * enc->length_m * enc->width_m;
    double a_total = a_vert + a_horiz;

    double r_wall = enc->wall_thick_m / (enc->wall_k * a_total);
    double t_amb_k = enc->t_ambient_c + 273.15;
    double t_wall_out = enc->t_ambient_c + 10.0; // Початкове наближення

    // Ітераційний розв'язувач для знаходження температури стінки
    for (int i = 0; i < 50; ++i) {
        double delta_t = fabs(t_wall_out - enc->t_ambient_c);
        if (delta_t < 0.1) delta_t = 0.1;

        // Конвекція для вертикального корпусу
        double h_c = 1.42 * pow(delta_t / enc->height_m, 0.25);
        if (h_c < 2.5) h_c = 2.5;

        // Радіаційна тепловіддача
        double t_w_k = t_wall_out + 273.15;
        double t_mean_k = 0.5 * (t_w_k + t_amb_k);
        double h_r = 4.0 * enc->wall_emissivity * STEFAN_BOLTZMANN * pow(t_mean_k, 3.0);

        double r_ext = 1.0 / ((h_c + h_r) * a_total);
        double next_t = enc->t_ambient_c + comp->p_watts * r_ext;

        if (fabs(next_t - t_wall_out) < 0.005) {
            t_wall_out = next_t;
            res->r_th_ext = r_ext;
            break;
        }
        t_wall_out = 0.6 * t_wall_out + 0.4 * next_t;
    }

    res->t_wall_out_c = t_wall_out;
    res->t_wall_in_c  = t_wall_out + comp->p_watts * r_wall;
    res->t_case_c     = res->t_wall_in_c + comp->p_watts * comp->r_th_bridge;
    res->t_junction_c = res->t_case_c + comp->p_watts * comp->r_th_jc;
    res->is_safe      = (res->t_junction_c < comp->t_j_max_c);

    return true;
}
