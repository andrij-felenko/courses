#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define MU_0 (4.0 * M_PI * 1e-7)

typedef struct {
    double x;
    double y;
    double current;
} Wire2D;

typedef struct {
    double x_min, x_max;
    double y_min, y_max;
    size_t nx, ny;
} GridBounds;

/* Обчислення B_z поля від множини провідників у точці (x, y) */
double compute_bz(double x, double y, const Wire2D* wires, size_t num_wires) {
    double bz_total = 0.0;
    for (size_t k = 0; k < num_wires; ++k) {
        double dx = x - wires[k].x;
        double dy = y - wires[k].y;
        double r2 = dx * dx + dy * dy;
        
        /* Запобігання діленню на нуль поруч із провідником (регуляризація) */
        if (r2 < 1e-12) {
            r2 = 1e-12;
        }
        
        /* Перпендикулярне поле B_z = (μ₀ · I / 2π) · (dx / r²) */
        double b_mag = (MU_0 * wires[k].current) / (2.0 * M_PI * r2);
        bz_total += b_mag * dx;
    }
    return bz_total;
}

/* 2D квадратура трапецій для обчислення магнітного потоку */
int integrate_magnetic_flux(const GridBounds* bounds, const Wire2D* wires, 
                            size_t num_wires, double* out_flux) {
    if (!bounds || !wires || !out_flux || bounds->nx == 0 || bounds->ny == 0) {
        return -1; /* Некоректні аргументи */
    }
    
    double dx = (bounds->x_max - bounds->x_min) / (double)bounds->nx;
    double dy = (bounds->y_max - bounds->y_min) / (double)bounds->ny;
    double total_flux = 0.0;

    for (size_t i = 0; i <= bounds->nx; ++i) {
        double x = bounds->x_min + (double)i * dx;
        double weight_x = (i == 0 || i == bounds->nx) ? 0.5 : 1.0;

        for (size_t j = 0; j <= bounds->ny; ++j) {
            double y = bounds->y_min + (double)j * dy;
            double weight_y = (j == 0 || j == bounds->ny) ? 0.5 : 1.0;

            double bz = compute_bz(x, y, wires, num_wires);
            total_flux += weight_x * weight_y * bz;
        }
    }

    *out_flux = total_flux * dx * dy;
    return 0; /* Успіх */
}

int main(void) {
    Wire2D wires[] = {
        { .x = 0.0, .y = 0.0, .current = 10.0 } /* Провідник 10 А в початку координат */
    };
    
    GridBounds bounds = {
        .x_min = 0.01, .x_max = 0.05, /* Рамка шириною від 1 см до 5 см */
        .y_min = 0.00, .y_max = 0.10, /* Висота 10 см */
        .nx = 200, .ny = 200
    };

    double flux = 0.0;
    if (integrate_magnetic_flux(&bounds, wires, 1, &flux) == 0) {
        printf("Чисельний потік: %.6e Wb\n", flux);
        
        /* Теоретичне аналітичне значення Φ = (μ₀ · I · h / 2π) · ln(b/a) */
        double flux_exact = (MU_0 * 10.0 * 0.10 / (2.0 * M_PI)) * log(0.05 / 0.01);
        printf("Аналітичний потік: %.6e Wb\n", flux_exact);
        printf("Відносна похибка: %.4f%%\n", fabs((flux - flux_exact) / flux_exact) * 100.0);
    } else {
        fprintf(stderr, "Помилка обчислення потоку!\n");
        return 1;
    }

    return 0;
}
