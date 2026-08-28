/* electrostatic_energy.c — Повний чисельний модуль розрахунку енергії зарядів на C99 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define EPSILON_0 8.8541878128e-12 /* Електрична стала у вакуумі, Ф/м */
#define K_COULOMB (1.0 / (4.0 * M_PI * EPSILON_0))
#define MIN_DISTANCE_SQ 1e-24      /* Порогова відстань для уникнення сингулярності (1 пм²) */

/* Структура для опису точкового заряду в 3D просторі */
typedef struct {
    double x, y, z;     /* Координати у метрах */
    double q;           /* Величина заряду у кулонах */
    double vx, vy, vz;  /* Швидкість для динамічних симуляцій, м/с */
    double m;           /* Маса частки у кг */
} Charge;

/* Структура 3D вектора напруженості поля */
typedef struct {
    double Ex, Ey, Ez;
} Vector3D;

/* Структура результату обчислення енергії */
typedef struct {
    double total_energy;    /* Обчислена потенціальна енергія у джоулях */
    size_t pair_count;      /* Кількість оброблених унікальних пар */
    bool status_ok;         /* Прапорець успішності обчислення */
} EnergyResult;

/*
 * Обчислює потенціальну енергію взаємодії системи з N точкових зарядів.
 * Приймає масив зарядів charges та їхню кількість count.
 */
EnergyResult calculate_interaction_energy(const Charge* charges, size_t count) {
    EnergyResult res = {0.0, 0, true};
    if (!charges || count < 2) {
        return res;
    }

    double sum = 0.0;
    for (size_t i = 0; i < count; ++i) {
        for (size_t j = i + 1; j < count; ++j) {
            double dx = charges[i].x - charges[j].x;
            double dy = charges[i].y - charges[j].y;
            double dz = charges[i].z - charges[j].z;
            double r_sq = dx * dx + dy * dy + dz * dz;

            if (r_sq < MIN_DISTANCE_SQ) {
                res.status_ok = false; /* Виявлено критичне зближення зарядів */
                return res;
            }

            double r = sqrt(r_sq);
            sum += (charges[i].q * charges[j].q) / r;
            res.pair_count++;
        }
    }

    res.total_energy = K_COULOMB * sum;
    return res;
}

/*
 * Обчислює скалярний потенціал у заданій точці простору (px, py, pz)
 * від усього масиву зарядів.
 */
double calculate_potential_at_point(const Charge* charges, size_t count, double px, double py, double pz) {
    if (!charges || count == 0) return 0.0;

    double potential = 0.0;
    for (size_t i = 0; i < count; ++i) {
        double dx = px - charges[i].x;
        double dy = py - charges[i].y;
        double dz = pz - charges[i].z;
        double r_sq = dx * dx + dy * dy + dz * dz;

        if (r_sq >= MIN_DISTANCE_SQ) {
            potential += charges[i].q / sqrt(r_sq);
        }
    }

    return K_COULOMB * potential;
}

/*
 * Обчислює вектор напруженості електричного поля E у точці (px, py, pz)
 */
Vector3D calculate_field_at_point(const Charge* charges, size_t count, double px, double py, double pz) {
    Vector3D E = {0.0, 0.0, 0.0};
    if (!charges || count == 0) return E;

    for (size_t i = 0; i < count; ++i) {
        double dx = px - charges[i].x;
        double dy = py - charges[i].y;
        double dz = pz - charges[i].z;
        double r_sq = dx * dx + dy * dy + dz * dz;

        if (r_sq >= MIN_DISTANCE_SQ) {
            double r = sqrt(r_sq);
            double factor = K_COULOMB * charges[i].q / (r_sq * r);
            E.Ex += factor * dx;
            E.Ey += factor * dy;
            E.Ez += factor * dz;
        }
    }

    return E;
}

/*
 * Обчислює 3D об'ємне інтегрування густини енергії поля w = 0.5 * eps0 * E^2 у заданій кубічній сітці
 */
double integrate_field_energy_grid(const Charge* charges, size_t count, 
                                   double min_x, double max_x, 
                                   double min_y, double max_y, 
                                   double min_z, double max_z, 
                                   int steps) {
    if (!charges || count == 0 || steps <= 0) return 0.0;

    double dx = (max_x - min_x) / steps;
    double dy = (max_y - min_y) / steps;
    double dz = (max_z - min_z) / steps;
    double dV = dx * dy * dz;

    double total_integrated_energy = 0.0;

    for (int ix = 0; ix < steps; ++ix) {
        double x = min_x + (ix + 0.5) * dx;
        for (int iy = 0; iy < steps; ++iy) {
            double y = min_y + (iy + 0.5) * dy;
            for (int iz = 0; iz < steps; ++iz) {
                double z = min_z + (iz + 0.5) * dz;

                Vector3D E = calculate_field_at_point(charges, count, x, y, z);
                double E_sq = E.Ex * E.Ex + E.Ey * E.Ey + E.Ez * E.Ez;
                double w = 0.5 * EPSILON_0 * E_sq;

                total_integrated_energy += w * dV;
            }
        }
    }

    return total_integrated_energy;
}

int main(void) {
    /* Тестова система: 4 заряди у вершинах квадрата зі стороною 1 см у площині XY */
    Charge system[4] = {
        {0.00, 0.00, 0.0,  1.0e-9, 0.0, 0.0, 0.0, 1.0e-12}, /* +1 нКл */
        {0.01, 0.00, 0.0, -1.0e-9, 0.0, 0.0, 0.0, 1.0e-12}, /* -1 нКл */
        {0.01, 0.01, 0.0,  1.0e-9, 0.0, 0.0, 0.0, 1.0e-12}, /* +1 нКл */
        {0.00, 0.01, 0.0, -1.0e-9, 0.0, 0.0, 0.0, 1.0e-12}  /* -1 нКл */
    };

    EnergyResult res = calculate_interaction_energy(system, 4);
    if (res.status_ok) {
        printf("=== Обчислення на C99 ===\n");
        printf("Кількість оброблених пар: %zu\n", res.pair_count);
        printf("Потенціальна енергія взаємодії системи: %.6e Дж\n", res.total_energy);

        /* Розрахунок потенціалу в центрі квадрата (0.5 см, 0.5 см, 0) */
        double phi_center = calculate_potential_at_point(system, 4, 0.005, 0.005, 0.0);
        printf("Потенціал у центрі системи: %.6f В\n", phi_center);

        /* 3D інтегрування енергії поля у кубі 4х4х4 см */
        double grid_energy = integrate_field_energy_grid(system, 4, -0.02, 0.03, -0.02, 0.03, -0.02, 0.03, 30);
        printf("Інтегрована енергія поля у сітці 30х30х30: %.6e Дж\n", grid_energy);
    } else {
        printf("Помилка: Виявлено сингулярність (заряди збігаються у просторі)!\n");
    }

    return 0;
}
