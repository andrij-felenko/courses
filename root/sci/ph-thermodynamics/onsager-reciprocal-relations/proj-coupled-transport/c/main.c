#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Структура для зберігання коефіцієнтів феноменологічної матриці Онсагера L */
typedef struct {
    double L_qq; /* Коефіцієнт тепло-тепло (Вт·К/м) */
    double L_qe; /* Коефіцієнт тепло-заряд (В·К·См/м) */
    double L_eq; /* Коефіцієнт заряд-тепло (В·К·См/м) */
    double L_ee; /* Коефіцієнт заряд-заряд (К·См/м) */
} OnsagerMatrix;

/* Макроскопічні характеристики термоелектричного матеріалу */
typedef struct {
    double sigma;   /* Питома електропровідність (См/м) */
    double kappa;   /* Питома теплопровідність (Вт/(м·К)) */
    double seebeck; /* Коефіцієнт Зеебека (В/К) */
} ThermoMaterial;

/* Результати чисельного моделювання термоелектричного переносу */
typedef struct {
    double heat_flux;          /* Потік тепла J_q (Вт/м²) */
    double current_density;    /* Густина струму J_e (А/м²) */
    double open_circuit_v;     /* Напруга холостого ходу (В) */
    double peltier_coeff;      /* Обчислений коефіцієнт Пельтьє (В) */
    double electrical_power_w; /* Корисна електрична потужність (Вт) */
    double efficiency_percent; /* Коефіцієнт корисної дії (%) */
    double zt_figure_of_merit; /* Безрозмірна добротність ZT */
} TransportResult;

/* Обчислення елементів матриці Онсагера за макроскопічними параметрами */
OnsagerMatrix compute_onsager_matrix(const ThermoMaterial* mat, double temp_k) {
    OnsagerMatrix L;
    L.L_ee = mat->sigma * temp_k;
    L.L_eq = mat->seebeck * mat->sigma * temp_k * temp_k;
    
    /* Застосування співвідношення взаємності Онсагера L_qe = L_eq */
    L.L_qe = L.L_eq; 
    
    L.L_qq = (mat->kappa + mat->seebeck * mat->seebeck * mat->sigma * temp_k) * temp_k * temp_k;
    return L;
}

/* Перевірка термодинамічної стабільності (додатна визначеність матриці L) */
bool validate_thermodynamic_stability(const OnsagerMatrix* L) {
    if (!L) return false;
    double det = L->L_qq * L->L_ee - L->L_qe * L->L_eq;
    return (L->L_qq > 0.0) && (L->L_ee > 0.0) && (det >= 0.0);
}

/* Симуляція процесів переносу у термоелектричному стрижні */
bool simulate_thermoelectric_leg(const ThermoMaterial* mat,
                                 double t_hot, double t_cold,
                                 double length, double cross_section_area,
                                 double load_resistance,
                                 TransportResult* res) {
    if (!mat || !res || length <= 0.0 || cross_section_area <= 0.0 || t_hot <= t_cold) {
        return false;
    }

    double t_avg = 0.5 * (t_hot + t_cold);
    OnsagerMatrix L = compute_onsager_matrix(mat, t_avg);

    if (!validate_thermodynamic_stability(&L)) {
        fprintf(stderr, "Помилка: порушено умову стабільності матриці Онсагера!\n");
        return false;
    }

    /* Обчислення добротності ZT */
    res->zt_figure_of_merit = (mat->seebeck * mat->seebeck * mat->sigma / mat->kappa) * t_avg;

    /* Термодинамічна сила градієнта температури X_q = ∇(1/T) */
    double X_q = -(t_hot - t_cold) / (t_avg * t_avg * length);

    /* Генерована термо-ЕРС Зеебека */
    res->open_circuit_v = mat->seebeck * (t_hot - t_cold);
    res->peltier_coeff = L.L_qe / L.L_ee; /* Співвідношення Кельвіна: Π = L_qe / L_ee = S · T */

    /* Внутрішній опір стрижня та розрахунок струму */
    double internal_resistance = length / (mat->sigma * cross_section_area);
    double total_current = res->open_circuit_v / (internal_resistance + load_resistance);
    res->current_density = total_current / cross_section_area;
    
    /* Термодинамічна сила електричного потенціалу X_e = -∇(φ/T) */
    double grad_phi = -res->current_density / mat->sigma;
    double X_e = -grad_phi / t_avg;

    /* Обчислення теплового потоку за рівнянням Онсагера */
    res->heat_flux = L.L_qq * X_q + L.L_qe * X_e;

    /* Потужність та ККД перетворення */
    res->electrical_power_w = total_current * total_current * load_resistance;
    double total_thermal_input_w = res->heat_flux * cross_section_area;
    res->efficiency_percent = (res->electrical_power_w / total_thermal_input_w) * 100.0;

    return true;
}

int main(void) {
    /* Параметри матеріалу телуриду вісмуту Bi2Te3 */
    ThermoMaterial bi2te3 = {
        .sigma = 100000.0,   /* Питома провідність 10^5 См/м */
        .kappa = 1.5,        /* Питома теплопровідність 1.5 Вт/(м·К) */
        .seebeck = 200e-6    /* Коефіцієнт Зеебека 200 мкВ/К */
    };

    double t_hot = 373.15;            /* 100 °C */
    double t_cold = 293.15;           /* 20 °C */
    double leg_length = 0.005;        /* Довжина 5 мм */
    double area = 1e-6;               /* Переріз 1 мм² */
    double r_load = 0.25;             /* Опір навантаження 0.25 Ом */

    TransportResult result;
    if (simulate_thermoelectric_leg(&bi2te3, t_hot, t_cold, leg_length, area, r_load, &result)) {
        printf("=== Результати розрахунку термоелектричного елемента (C) ===\n");
        printf("Різниця температур ΔT: %.2f K\n", t_hot - t_cold);
        printf("Добротність матеріалу ZT: %.4f\n", result.zt_figure_of_merit);
        printf("Генерована термо-ЕРС:   %.4f В\n", result.open_circuit_v);
        printf("Коефіцієнт Пельтьє Π:   %.4f В (Очікувано S·T: %.4f В)\n",
               result.peltier_coeff, bi2te3.seebeck * 0.5 * (t_hot + t_cold));
        printf("Густина тепла J_q:      %.2f Вт/м²\n", result.heat_flux);
        printf("Густина струму J_e:     %.2f А/м²\n", result.current_density);
        printf("Корисна потужність P:   %.6f Вт\n", result.electrical_power_w);
        printf("ККД перетворення:       %.2f %%\n", result.efficiency_percent);
    }

    return 0;
}
