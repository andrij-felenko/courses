#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846
#define EPSILON_0 8.8541878128e-12
#define MU_0 (4.0 * PI * 1e-7)

typedef struct {
    double x;
    double y;
    double v;          /* Скалярний потенціал у точці */
    double sigma_s;    /* Поверхнева густина заряду */
} CircuitPoint;

typedef struct {
    double x;
    double y;
    double Ex;
    double Ey;
    double Bz;
    double Sx;
    double Sy;
} FieldPoint;

/* Обчислення геометрії контуру, потенціалу V(s) та поверхневих зарядів σ_s */
void init_circuit(CircuitPoint *pts, size_t n_pts, double width, double height, double v0, double r_wire) {
    double perimeter = 2.0 * (width + height);
    double geom_factor = (2.0 * PI * EPSILON_0) / (r_wire * log(perimeter / r_wire));
    
    for (size_t i = 0; i < n_pts; ++i) {
        double s = ((double)i / (double)n_pts) * perimeter;
        
        /* Розгортання прямокутного контуру */
        if (s < width) {
            pts[i].x = s - width / 2.0;
            pts[i].y = height / 2.0;
        } else if (s < width + height) {
            pts[i].x = width / 2.0;
            pts[i].y = height / 2.0 - (s - width);
        } else if (s < 2.0 * width + height) {
            pts[i].x = width / 2.0 - (s - (width + height));
            pts[i].y = -height / 2.0;
        } else {
            pts[i].x = -width / 2.0;
            pts[i].y = -height / 2.0 + (s - (2.0 * width + height));
        }
        
        /* Потенціал спадає лінійно від +V0/2 до -V0/2 */
        double frac = (double)i / (double)n_pts;
        pts[i].v = (0.5 - frac) * v0;
        pts[i].sigma_s = geom_factor * pts[i].v;
    }
}

/* Обчислення вектора полів та Пойнтінга у довільній точці простору (px, py) */
FieldPoint compute_fields(const CircuitPoint *pts, size_t n_pts, double current, double r_wire, double px, double py) {
    FieldPoint fp = {px, py, 0.0, 0.0, 0.0, 0.0, 0.0};
    double ds = (2.0 * (0.4 + 0.2)) / (double)n_pts;
    double softening = 1e-4; /* Регуляризація знаменника 0.1 мм */
    
    for (size_t i = 0; i < n_pts; ++i) {
        double rx = px - pts[i].x;
        double ry = py - pts[i].y;
        double r2 = rx * rx + ry * ry + softening * softening;
        double r = sqrt(r2);
        
        /* Внесок Кулона від поверхневого заряду */
        double dq = pts[i].sigma_s * (2.0 * PI * r_wire) * ds;
        double dE = dq / (4.0 * PI * EPSILON_0 * r2);
        fp.Ex += dE * (rx / r);
        fp.Ey += dE * (ry / r);
        
        /* Внесок Біо-Савара від струму */
        double dB = (MU_0 * current) / (2.0 * PI * r);
        fp.Bz += dB;
    }
    
    /* Вектор Пойнтінга S = (1/μ0) * (E x B) */
    fp.Sx = (fp.Ey * fp.Bz) / MU_0;
    fp.Sy = (-fp.Ex * fp.Bz) / MU_0;
    
    return fp;
}

int main(void) {
    const size_t N_POINTS = 400;
    const double V0 = 12.0;           /* Вольти */
    const double R_LOAD = 6.0;        /* Оми */
    const double I_CURRENT = V0 / R_LOAD; /* 2.0 Ампери */
    const double R_WIRE = 0.001;      /* 1 мм радіус */
    
    CircuitPoint *pts = (CircuitPoint *)malloc(N_POINTS * sizeof(CircuitPoint));
    if (!pts) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }
    
    init_circuit(pts, N_POINTS, 0.4, 0.2, V0, R_WIRE);
    
    /* Точка спостереження поблизу бічної поверхні резистора */
    FieldPoint fp = compute_fields(pts, N_POINTS, I_CURRENT, R_WIRE, 0.19, 0.0);
    
    printf("=== Симуляція полів у колі зі струмом (C) ===\n");
    printf("Напруга ЕРС: %.2f V, Струм: %.2f A, Потужність P = I^2*R: %.2f Вт\n", V0, I_CURRENT, I_CURRENT * I_CURRENT * R_LOAD);
    printf("Точка спостереження поблизу резистора (0.19 м, 0.0 м):\n");
    printf("  Електричне поле Ex: %.3e В/м, Ey: %.3e В/м\n", fp.Ex, fp.Ey);
    printf("  Магнітне поле  Bz: %.3e Тл\n", fp.Bz);
    printf("  Вектор Пойнтінга Sx: %.3e Вт/м², Sy: %.3e Вт/м²\n", fp.Sx, fp.Sy);
    
    free(pts);
    return 0;
}
