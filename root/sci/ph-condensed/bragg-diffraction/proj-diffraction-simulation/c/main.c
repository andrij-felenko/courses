#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef enum {
    LATTICE_SC,
    LATTICE_BCC,
    LATTICE_FCC,
    LATTICE_DIAMOND
} LatticeType;

typedef struct {
    int h, k, l;
    double d_spacing;
    double theta_deg;
    double two_theta_deg;
    double intensity;
} PeakInfo;

// Аналітичний розрахунок квадрата структурного фактора |S(h,k,l)|^2
double get_structure_factor_square(LatticeType type, int h, int k, int l) {
    int sum = h + k + l;
    int h_even = (h % 2 == 0);
    int k_even = (k % 2 == 0);
    int l_even = (l % 2 == 0);

    switch (type) {
        case LATTICE_SC:
            return 1.0;

        case LATTICE_BCC:
            return (sum % 2 == 0) ? 4.0 : 0.0;

        case LATTICE_FCC:
            if ((h_even == k_even) && (k_even == l_even)) {
                return 16.0;
            }
            return 0.0;

        case LATTICE_DIAMOND:
            if ((h_even == k_even) && (k_even == l_even)) {
                if (h_even) {
                    return (sum % 4 == 0) ? 64.0 : 0.0;
                } else {
                    return 32.0;
                }
            }
            return 0.0;

        default:
            return 0.0;
    }
}

// Компаратор для сортування піків за кутом 2*theta
int compare_peaks(const void *a, const void *b) {
    const PeakInfo *p1 = (const PeakInfo *)a;
    const PeakInfo *p2 = (const PeakInfo *)b;
    if (p1->two_theta_deg < p2->two_theta_deg) return -1;
    if (p1->two_theta_deg > p2->two_theta_deg) return 1;
    return 0;
}

void run_diffraction_simulation(LatticeType lattice, double a_nm, double lambda_nm, int max_hkl) {
    PeakInfo peaks[256];
    int count = 0;

    for (int h = 0; h <= max_hkl; ++h) {
        for (int k = 0; k <= max_hkl; ++k) {
            for (int l = 0; l <= max_hkl; ++l) {
                if (h == 0 && k == 0 && l == 0) continue;

                double s_sq = get_structure_factor_square(lattice, h, k, l);
                if (s_sq <= 0.001) continue; // Систематичне згасання

                double hkl_sq = (double)(h * h + k * k + l * l);
                double d = a_nm / sqrt(hkl_sq);
                double sin_t = lambda_nm / (2.0 * d);

                if (sin_t <= 1.0) {
                    double t_rad = asin(sin_t);
                    double t_deg = t_rad * (180.0 / M_PI);

                    peaks[count].h = h;
                    peaks[count].k = k;
                    peaks[count].l = l;
                    peaks[count].d_spacing = d;
                    peaks[count].theta_deg = t_deg;
                    peaks[count].two_theta_deg = 2.0 * t_deg;
                    peaks[count].intensity = s_sq;
                    count++;
                }
            }
        }
    }

    qsort(peaks, count, sizeof(PeakInfo), compare_peaks);

    printf("=========================================================================\n");
    printf("СИМУЛЯЦІЯ ДИФРАКЦІЇ (параметр a = %.4f нм, lambda = %.4f нм)\n", a_nm, lambda_nm);
    printf("=========================================================================\n");
    printf("  (h k l)  |  d (нм)   |  theta (deg) | 2*theta (deg) | Інтенсивність\n");
    printf("-------------------------------------------------------------------------\n");
    for (int i = 0; i < count; ++i) {
        printf("  (%d %d %d)  |  %8.4f  |  %11.2f | %13.2f | %12.1f\n",
               peaks[i].h, peaks[i].k, peaks[i].l,
               peaks[i].d_spacing, peaks[i].theta_deg,
               peaks[i].two_theta_deg, peaks[i].intensity);
    }
    printf("-------------------------------------------------------------------------\n");
    printf(" Дозволених піків у спектрі: %d\n\n", count);
}

int main(void) {
    double a_si = 0.5431;    // Параметр ґратки кремнію Si (нм)
    double lambda_cu = 0.15406; // Cu K-alpha1 (нм)

    printf("--- РЕЗУЛЬТАТ ДЛЯ КРЕМНІЮ (Si, Структура Алмазу) ---\n");
    run_diffraction_simulation(LATTICE_DIAMOND, a_si, lambda_cu, 4);

    printf("--- РЕЗУЛЬТАТ ДЛЯ МІДІ (Cu, FCC ґратка) ---\n");
    run_diffraction_simulation(LATTICE_FCC, 0.3615, lambda_cu, 3);

    return 0;
}
