#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846
#define HBAR 1.054571817e-34
#define EV_TO_JOULE 1.602176634e-19

typedef struct {
    double x;
    double y;
} Point2D;

typedef struct {
    double t_hopping;  // Інтеграл перескоку (еВ)
    double a_lattice;  // Період ґратки (метрів)
} LatticeParams;

// Дисперсія E(kx, ky) у джоулях
double calculate_energy(double kx, double ky, const LatticeParams* params) {
    double t_joule = params->t_hopping * EV_TO_JOULE;
    return -2.0 * t_joule * (cos(kx * params->a_lattice) + cos(ky * params->a_lattice));
}

// Обчислення площі замкненого многокутника за формулою Гаусса
double calculate_polygon_area(const Point2D* points, size_t count) {
    if (count < 3) return 0.0;
    double area = 0.0;
    for (size_t i = 0; i < count; ++i) {
        size_t next = (i + 1) % count;
        area += points[i].x * points[next].y - points[next].x * points[i].y;
    }
    return 0.5 * fabs(area);
}

// Обчислення площі орбіти у k-просторі для заданої енергії EF (у джоулях)
double compute_fermi_area(double ef_joule, const LatticeParams* params, size_t grid_size) {
    double k_max = PI / params->a_lattice;
    double step = (2.0 * k_max) / (double)(grid_size - 1);
    
    // Динамічний масив під точки контуру
    size_t capacity = grid_size * 4;
    Point2D* contour = (Point2D*)malloc(capacity * sizeof(Point2D));
    if (!contour) return 0.0;
    
    size_t contour_count = 0;
    
    // Спрощена маркувальна сітка для визначення точок E(k) = EF
    for (size_t i = 0; i < grid_size - 1; ++i) {
        double kx = -k_max + i * step;
        for (size_t j = 0; j < grid_size - 1; ++j) {
            double ky = -k_max + j * step;
            
            double e00 = calculate_energy(kx, ky, params);
            double e10 = calculate_energy(kx + step, ky, params);
            double e01 = calculate_energy(kx, ky + step, params);
            
            // Лінійна інтерполяція вздовж горизонтального ребра
            if ((e00 - ef_joule) * (e10 - ef_joule) <= 0.0 && fabs(e10 - e00) > 1e-30) {
                double frac = (ef_joule - e00) / (e10 - e00);
                if (contour_count < capacity) {
                    contour[contour_count].x = kx + frac * step;
                    contour[contour_count].y = ky;
                    contour_count++;
                }
            }
            // Лінійна інтерполяція вздовж вертикального ребра
            if ((e00 - ef_joule) * (e01 - ef_joule) <= 0.0 && fabs(e01 - e00) > 1e-30) {
                double frac = (ef_joule - e00) / (e01 - e00);
                if (contour_count < capacity) {
                    contour[contour_count].x = kx;
                    contour[contour_count].y = ky + frac * step;
                    contour_count++;
                }
            }
        }
    }
    
    double area = calculate_polygon_area(contour, contour_count);
    free(contour);
    return area;
}

// Розрахунок циклотронної маси m_c*
double compute_cyclotron_mass(double ef_ev, const LatticeParams* params, size_t grid_size) {
    double ef_joule = ef_ev * EV_TO_JOULE;
    double delta_e = 0.005 * EV_TO_JOULE; // ΔE = 5 меВ
    
    double area_plus = compute_fermi_area(ef_joule + delta_e, params, grid_size);
    double area_minus = compute_fermi_area(ef_joule - delta_e, params, grid_size);
    
    double dA_dE = (area_plus - area_minus) / (2.0 * delta_e);
    return (HBAR * HBAR / (2.0 * PI)) * dA_dE;
}

int main(void) {
    LatticeParams params = { .t_hopping = 1.0, .a_lattice = 3.0e-10 }; // t = 1 еВ, a = 3 Å
    size_t grid_N = 500;
    double target_ef = -1.5; // еВ (низьке заповнення, електронні орбіти)
    
    double mass = compute_cyclotron_mass(target_ef, &params, grid_N);
    double m_e = 9.1093837015e-31;
    
    printf("Енергія Фермі E_F: %.2f еВ\n", target_ef);
    printf("Циклотронна маса m_c*: %.4e кг (%.3f m_e)\n", mass, mass / m_e);
    
    return 0;
}
