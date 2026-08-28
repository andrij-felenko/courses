#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Структура конфігурації протяжного некогерентного джерела
typedef struct {
    double width_mm;
    double height_mm;
    double distance_R_mm;
    double wavelength_mm;
} SourceConfig;

// Обчислення ступеня просторової когерентності методом двовимірної сітки
double compute_spatial_coherence_2d(const SourceConfig* cfg, double dx_mm, double dy_mm, int grid_nodes) {
    double re_sum = 0.0;
    double im_sum = 0.0;
    double total_intensity = 0.0;
    
    double step_x = cfg->width_mm / grid_nodes;
    double step_y = cfg->height_mm / grid_nodes;
    double k = 2.0 * M_PI / cfg->wavelength_mm;
    
    for (int i = 0; i < grid_nodes; ++i) {
        double xi = -cfg->width_mm / 2.0 + (i + 0.5) * step_x;
        for (int j = 0; j < grid_nodes; ++j) {
            double eta = -cfg->height_mm / 2.0 + (j + 0.5) * step_y;
            
            // Рівномірний розподіл інтенсивності джерела
            double intensity = 1.0;
            double phase = k * (dx_mm * xi + dy_mm * eta) / cfg->distance_R_mm;
            
            re_sum += intensity * cos(phase) * step_x * step_y;
            im_sum += intensity * sin(phase) * step_x * step_y;
            total_intensity += intensity * step_x * step_y;
        }
    }
    
    double modulus = sqrt(re_sum * re_sum + im_sum * im_sum);
    return modulus / total_intensity;
}

int main(void) {
    SourceConfig cfg = {
        .width_mm = 2.0,
        .height_mm = 2.0,
        .distance_R_mm = 1000.0,  // 1000 мм (1 метр)
        .wavelength_mm = 0.0005    // 500 нм
    };
    
    printf("--- Просторова когерентність (Обчислення мовою C) ---\n");
    printf("Відстань d (мм) | |gamma_12| | Видність смуг V\n");
    printf("--------------------------------------------\n");
    
    for (double d = 0.0; d <= 0.4; d += 0.05) {
        double g = compute_spatial_coherence_2d(&cfg, d, 0.0, 100);
        printf("   %6.2f       | %6.4f   | %6.4f\n", d, g, g);
    }
    
    return 0;
}
