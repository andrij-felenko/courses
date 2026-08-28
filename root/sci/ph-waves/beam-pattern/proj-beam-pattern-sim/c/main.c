#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Конструкція специфікації випромінювача
typedef struct {
    double freq_hz;       // Робоча частота, Гц
    double sound_speed;   // Швидкість звуку в середовищі, м/с
    double aperture_d;    // Розмір апертури / діаметр D, м
    int num_elements;     // Кількість елементів масиву (для решітки)
    double elem_spacing;  // Крок елементів d, м
    double steer_angle_deg; // Кут електронного сканування, град
} transducer_config_t;

// Специфікація виявлених параметрів спрямованості
typedef struct {
    double beamwidth_3db_deg; // Ширина променя за рівнем -3 dB, град
    double sll_db;            // Рівень першої бічної пелюстки, dB
    double first_null_deg;    // Перший нульовий кут, град
} beam_metrics_t;

// Обчислення функції Бесселя першого порядку J1(x) за наближенням Абрамовіца-Стіган
static double bessel_j1(double x) {
    double ax = fabs(x);
    if (ax < 3.75) {
        double y = (x / 3.75) * (x / 3.75);
        double ans = x * (0.5 + y * (-0.56249985 + y * (0.21093573 + 
                     y * (-0.03954289 + y * (0.00443319 + y * -0.00031761)))));
        return ans;
    } else {
        double y = 3.75 / ax;
        double f1 = 0.79788456 + y * (-0.00000077 + y * (-0.00552740 + 
                    y * (0.00095120 + y * (-0.00066738 + y * 0.00015649))));
        double theta1 = ax - 2.35619449 + y * (0.04166397 + y * (-0.00003954 + 
                        y * (0.00262573 + y * (-0.00054125 + y * 0.00029333))));
        double ans = (1.0 / sqrt(ax)) * f1 * cos(theta1);
        return (x < 0.0) ? -ans : ans;
    }
}

// Нормована спрямованість кругового поршня 2*J1(v)/v
static double compute_circular_piston(double theta_rad, double k, double diameter) {
    double radius = diameter / 2.0;
    double v = k * radius * sin(theta_rad);
    if (fabs(v) < 1e-6) {
        return 1.0;
    }
    return fabs(2.0 * bessel_j1(v) / v);
}

// Спрямованість дискретної фазованої решітки N елементів
static double compute_phased_array(double theta_rad, double k, int n_elem, double d_elem, double steer_rad) {
    double psi = k * d_elem * (sin(theta_rad) - sin(steer_rad));
    if (fabs(psi) < 1e-6) {
        return 1.0;
    }
    double num = sin((double)n_elem * psi / 2.0);
    double den = (double)n_elem * sin(psi / 2.0);
    return fabs(num / den);
}

// Обчислення масиву спрямованості та метрик
bool calculate_beam_pattern(const transducer_config_t *cfg,
                            double *angles_deg,
                            double *pattern_db,
                            size_t num_points,
                            beam_metrics_t *metrics) {
    if (!cfg || !angles_deg || !pattern_db || num_points < 2 || !metrics) {
        return false;
    }

    double lambda = cfg->sound_speed / cfg->freq_hz;
    double k = 2.0 * M_PI / lambda;
    double steer_rad = cfg->steer_angle_deg * M_PI / 180.0;

    double max_val = 0.0;
    size_t main_peak_idx = 0;

    for (size_t i = 0; i < num_points; ++i) {
        double theta_deg = -90.0 + (180.0 * (double)i / (double)(num_points - 1));
        angles_deg[i] = theta_deg;
        double theta_rad = theta_deg * M_PI / 180.0;

        double r_val = 0.0;
        if (cfg->num_elements > 1) {
            r_val = compute_phased_array(theta_rad, k, cfg->num_elements, cfg->elem_spacing, steer_rad);
        } else {
            r_val = compute_circular_piston(theta_rad, k, cfg->aperture_d);
        }

        if (r_val > max_val) {
            max_val = r_val;
            main_peak_idx = i;
        }

        double db = 20.0 * log10(r_val > 1e-4 ? r_val : 1e-4);
        pattern_db[i] = db;
    }

    // Нормалізація дБ масиву відносно максимуму
    double max_db = pattern_db[main_peak_idx];
    for (size_t i = 0; i < num_points; ++i) {
        pattern_db[i] -= max_db;
    }

    // Знаходження кутів -3 dB
    double left_3db = angles_deg[0];
    double right_3db = angles_deg[num_points - 1];

    for (size_t i = main_peak_idx; i > 0; --i) {
        if (pattern_db[i] <= -3.0) {
            left_3db = angles_deg[i];
            break;
        }
    }
    for (size_t i = main_peak_idx; i < num_points; ++i) {
        if (pattern_db[i] <= -3.0) {
            right_3db = angles_deg[i];
            break;
        }
    }
    metrics->beamwidth_3db_deg = right_3db - left_3db;

    // Пошук першої бічної пелюстки (SLL)
    double side_max_db = -100.0;
    bool in_main_lobe = true;

    for (size_t i = main_peak_idx; i < num_points - 1; ++i) {
        if (in_main_lobe) {
            if (pattern_db[i + 1] > pattern_db[i] && pattern_db[i] < -15.0) {
                in_main_lobe = false; // Вийшли з головної пелюстки через перший нуль
            }
        } else {
            if (pattern_db[i] > side_max_db) {
                side_max_db = pattern_db[i];
            }
        }
    }
    metrics->sll_db = side_max_db;
    metrics->first_null_deg = fabsf((float)(right_3db * 1.8));

    return true;
}

int main(void) {
    transducer_config_t config = {
        .freq_hz = 40000.0,      // 40 кГц ультразвук
        .sound_speed = 1500.0,   // у воді
        .aperture_d = 0.15,      // 15 см діаметр поршня
        .num_elements = 1,       // Суцільний поршень
        .elem_spacing = 0.0,
        .steer_angle_deg = 0.0
    };

    const size_t N_PTS = 361;
    double *angles = (double*)malloc(N_PTS * sizeof(double));
    double *pattern = (double*)malloc(N_PTS * sizeof(double));
    beam_metrics_t metrics;

    if (!angles || !pattern) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        free(angles);
        free(pattern);
        return 1;
    }

    if (calculate_beam_pattern(&config, angles, pattern, N_PTS, &metrics)) {
        printf("=== Результати обчислення спрямованості (C) ===\n");
        printf("Частота: %.1f кГц, Апертура D = %.2f м\n", config.freq_hz / 1000.0, config.aperture_d);
        printf("Ширина променя (-3 dB): %.2f°\n", metrics.beamwidth_3db_deg);
        printf("Рівень першої бічної пелюстки (SLL): %.2f dB\n", metrics.sll_db);
        printf("\nЗріз кутів та амплітуд (дБ):\n");
        for (size_t i = 0; i < N_PTS; i += 30) {
            printf("  Кут %6.1f° : %6.2f dB\n", angles[i], pattern[i]);
        }
    }

    free(angles);
    free(pattern);
    return 0;
}
