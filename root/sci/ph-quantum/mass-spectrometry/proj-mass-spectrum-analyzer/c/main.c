#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фізичні константи в атомних одиницях маси та МеВ */
#define AMU_TO_MEV 931.49410242
#define MASS_PROTON 1.007276466621
#define MASS_NEUTRON 1.00866491595
#define MASS_ELECTRON 0.000548579909

/* Структура для експериментальної точки TOF-ICR спектра */
typedef struct {
    double freq_hz;       /* Частота ВЧ збудження, Гц */
    double tof_us;        /* Середній час прольоту, мкс */
    double tof_err_us;    /* Статистична похибка часу, мкс */
} tof_point_t;

/* Результат обробки резонансної лінії */
typedef struct {
    double nu_c_hz;       /* Визначена циклотронна частота, Гц */
    double nu_c_err_hz;   /* Похибка циклотронної частоти, Гц */
    double t_base_us;     /* Фоновий час прольоту поза резонансом */
    double depth_us;      /* Глибина резонансного провалу */
    double fwhm_hz;       /* Ширина резонансної лінії (FWHM) */
    double chi2_red;      /* Приведена величина хі-квадрат */
} resonance_result_t;

/* Підгонка резонансної кривої TOF-ICR методом ітераційного пошуку мінімуму */
int fit_tof_icr_spectrum(const tof_point_t *data, size_t count, resonance_result_t *out_res) {
    if (!data || count < 5 || !out_res) return -1;

    /* 1. Початкова оцінка параметрів */
    double min_tof = 1e9, max_tof = -1e9;
    double freq_at_min = 0.0;
    
    for (size_t i = 0; i < count; ++i) {
        if (data[i].tof_us < min_tof) {
            min_tof = data[i].tof_us;
            freq_at_min = data[i].freq_hz;
        }
        if (data[i].tof_us > max_tof) {
            max_tof = data[i].tof_us;
        }
    }

    double best_nu_c = freq_at_min;
    double best_base = max_tof;
    double best_depth = max_tof - min_tof;
    double best_sigma = 25.0; /* Початкове наближення ширини, Гц */
    double min_chi2 = 1e18;

    /* 2. Сітковий та градієнтний пошук мінімуму Хі-квадрат */
    for (double f_step = -50.0; f_step <= 50.0; f_step += 0.5) {
        double trial_nu_c = freq_at_min + f_step;
        for (double trial_sigma = 10.0; trial_sigma <= 60.0; trial_sigma += 2.0) {
            double current_chi2 = 0.0;
            for (size_t i = 0; i < count; ++i) {
                double diff_f = data[i].freq_hz - trial_nu_c;
                double calc_tof = max_tof - best_depth * exp(-(diff_f * diff_f) / (2.0 * trial_sigma * trial_sigma));
                double err = (data[i].tof_err_us > 0.0) ? data[i].tof_err_us : 1.0;
                double res = (data[i].tof_us - calc_tof) / err;
                current_chi2 += res * res;
            }
            if (current_chi2 < min_chi2) {
                min_chi2 = current_chi2;
                best_nu_c = trial_nu_c;
                best_sigma = trial_sigma;
            }
        }
    }

    /* 3. Оцінка похибки частоти через статистику Хі-квадрат */
    double fwhm = 2.35482 * best_sigma;
    double nu_c_uncert = best_sigma / sqrt((double)count);

    out_res->nu_c_hz = best_nu_c;
    out_res->nu_c_err_hz = nu_c_uncert;
    out_res->t_base_us = max_tof;
    out_res->depth_us = best_depth;
    out_res->fwhm_hz = fwhm;
    out_res->chi2_red = min_chi2 / (count > 4 ? count - 4 : 1);

    return 0;
}

/* Обчислення маси та енергії зв'язку ядра за відношенням частот R = nu_ref / nu_x */
void calculate_nuclear_binding_energy(double nu_x, double nu_x_err,
                                      double nu_ref, double nu_ref_err,
                                      double m_ref_amu, int Z, int A,
                                      double *out_mass_amu, double *out_mass_err,
                                      double *out_eb_mev, double *out_eb_err) {
    /* Відношення частот R = nu_ref / nu_x */
    double R = nu_ref / nu_x;
    double R_err = R * sqrt(pow(nu_ref_err / nu_ref, 2) + pow(nu_x_err / nu_x, 2));

    /* Обчислення атомної маси ізотопу X (припускаємо однакові заряди іонізації q_x = q_ref = +1) */
    double m_x_atom = R * (m_ref_amu - MASS_ELECTRON) + MASS_ELECTRON;
    double m_x_err = R_err * (m_ref_amu - MASS_ELECTRON);

    /* Обчислення маси ядра M_nuc = M_atom - Z * m_e */
    double m_nuc = m_x_atom - Z * MASS_ELECTRON;

    /* Дефект маси для ядра: Delta_m = Z*m_p + (A-Z)*m_n - M_nuc */
    int N = A - Z;
    double m_free_constituents = Z * MASS_PROTON + N * MASS_NEUTRON;
    double binding_energy_mev = (m_free_constituents - m_nuc) * AMU_TO_MEV;
    double binding_energy_err = m_x_err * AMU_TO_MEV;

    *out_mass_amu = m_x_atom;
    *out_mass_err = m_x_err;
    *out_eb_mev = binding_energy_mev;
    *out_eb_err = binding_energy_err;
}

int main(void) {
    printf("=== Аналіз TOF-ICR спектрів та розрахунок маси нукліду ===\n");

    /* Тестові експериментальні дані TOF-ICR для 85Rb+ навколо nu_c = 1264820 Гц */
    tof_point_t spectrum[] = {
        {1264720.0, 148.5, 1.2},
        {1264750.0, 145.2, 1.1},
        {1264780.0, 122.1, 1.3},
        {1264800.0, 95.4,  1.0},
        {1264820.0, 71.2,  0.9}, /* Резонансний мінімум */
        {1264840.0, 98.1,  1.1},
        {1264860.0, 125.6, 1.2},
        {1264890.0, 147.0, 1.0},
        {1264920.0, 149.1, 1.3}
    };
    size_t n_points = sizeof(spectrum) / sizeof(spectrum[0]);

    resonance_result_t res;
    if (fit_tof_icr_spectrum(spectrum, n_points, &res) == 0) {
        printf("Резонансна частота nu_c : %.3f +/- %.3f Гц\n", res.nu_c_hz, res.nu_c_err_hz);
        printf("Фоновий час T_base     : %.2f мкс\n", res.t_base_us);
        printf("Глибина резонансу ΔT   : %.2f мкс\n", res.depth_us);
        printf("Ширина ліній FWHM      : %.2f Гц\n", res.fwhm_hz);
        printf("Приведений Chi2        : %.3f\n", res.chi2_red);

        /* Використовуємо вуглець-12 як опорний референтну масу (m_ref = 12.0 а.о.м.) */
        double nu_ref = 8961420.0;    /* Частота 12C+ */
        double nu_ref_err = 0.05;
        double m_atom = 0.0, m_err = 0.0, eb_mev = 0.0, eb_err = 0.0;

        /* Обчислення маси Рубідію-85 (Z = 37, A = 85) */
        calculate_nuclear_binding_energy(res.nu_c_hz, res.nu_c_err_hz,
                                         nu_ref, nu_ref_err,
                                         84.9117897, 37, 85,
                                         &m_atom, &m_err, &eb_mev, &eb_err);

        printf("\n--- Розраховані атомні та ядерні параметри 85Rb ---\n");
        printf("Атомна маса M(85Rb)    : %.8f +/- %.8f а.о.м.\n", m_atom, m_err);
        printf("Повна енергія зв'язку  : %.3f +/- %.3f МеВ\n", eb_mev, eb_err);
        printf("Питома енергія зв'язку : %.4f МеВ/нуклон\n", eb_mev / 85.0);
    }

    return 0;
}
