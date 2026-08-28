#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double x;
    double y;
    double amplitude;
    double phase_shift;
} HuygensSource;

typedef struct {
    double y;
    double intensity;
} ScreenPoint;

/**
 * Чисельне моделювання хвильового фронту Гюйгенса мовою C.
 */
int simulate_huygens_c(
    double wavelength,
    double slit_width,
    int num_sources,
    double screen_dist,
    double screen_width,
    int num_screen_pts,
    ScreenPoint* out_screen
) {
    if (!out_screen || num_sources <= 0 || num_screen_pts <= 0) return -1;

    HuygensSource* sources = (HuygensSource*)malloc(num_sources * sizeof(HuygensSource));
    if (!sources) return -2;

    double k = 2.0 * M_PI / wavelength;
    double dy_src = (num_sources > 1) ? (slit_width / (num_sources - 1)) : 0.0;
    double start_y_src = -slit_width / 2.0;

    /* Ініціалізація точкових джерел Гюйгенса */
    for (int n = 0; n < num_sources; ++n) {
        sources[n].x = 0.0;
        sources[n].y = start_y_src + n * dy_src;
        sources[n].amplitude = 1.0 / num_sources;
        sources[n].phase_shift = 0.0;
    }

    double dy_scr = (num_screen_pts > 1) ? (screen_width / (num_screen_pts - 1)) : 0.0;
    double start_y_scr = -screen_width / 2.0;
    double eps = (wavelength / 20.0) * (wavelength / 20.0);
    double max_intensity = 0.0;

    /* Сумування комплексних хвиль у кожній точці екрана */
    for (int i = 0; i < num_screen_pts; ++i) {
        double px = screen_dist;
        double py = start_y_scr + i * dy_scr;
        double re_total = 0.0;
        double im_total = 0.0;

        for (int n = 0; n < num_sources; ++n) {
            double dx = px - sources[n].x;
            double dy = py - sources[n].y;
            double r = sqrt(dx * dx + dy * dy + eps);
            double cos_theta = dx / r;
            double k_factor = 0.5 * (1.0 + cos_theta);

            double phase = k * r + sources[n].phase_shift - (M_PI / 2.0);
            double amp_factor = (sources[n].amplitude / sqrt(r)) * k_factor;

            re_total += amp_factor * cos(phase);
            im_total += amp_factor * sin(phase);
        }

        double intensity = re_total * re_total + im_total * im_total;
        out_screen[i].y = py;
        out_screen[i].intensity = intensity;

        if (intensity > max_intensity) {
            max_intensity = intensity;
        }
    }

    /* Нормування інтенсивності */
    if (max_intensity > 0.0) {
        for (int i = 0; i < num_screen_pts; ++i) {
            out_screen[i].intensity /= max_intensity;
        }
    }

    free(sources);
    return 0;
}

int main(void) {
    const int num_pts = 400;
    ScreenPoint* screen = (ScreenPoint*)malloc(num_pts * sizeof(ScreenPoint));
    
    if (simulate_huygens_c(0.5e-6, 5.0e-6, 200, 50e-6, 80e-6, num_pts, screen) == 0) {
        printf("C модель успішно виконана. I(0) = %.4f\n", screen[num_pts / 2].intensity);
    }
    
    free(screen);
    return 0;
}
