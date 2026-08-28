#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define CONST_HC_EV_NM 1239.8419  /* h*c у еВ·нм */
#define SILICON_EG_EV   1.12      /* Ширина забороненої зони кремнію при 300K */

typedef struct {
    double wavelength_nm;
    double reflection_R;
    double alpha_cm1;
    double iqe;
    double eqe;
    double responsivity_a_w;
} PhotodiodeSpectrumPoint;

/* Наближений розрахунок коефіцієнта поглинання кремнію α(λ) у см⁻¹ */
static double silicon_absorption_coefficient(double lambda_nm) {
    if (lambda_nm >= 1107.0) {
        return 0.0; /* Нижче ширини забороненої зони поглинання відсутнє */
    }
    double photon_energy_ev = CONST_HC_EV_NM / lambda_nm;
    double diff = photon_energy_ev - SILICON_EG_EV;
    if (diff <= 0.0) {
        return 0.0;
    }
    /* Спрощена модель феноменологічного поглинання Si */
    return 5000.0 * diff * diff + 1e5 * pow(diff, 3.5);
}

/* Модель відбиття від поверхні з одношаровим AR-покриттям */
static double surface_reflection(double lambda_nm, double target_lambda_nm) {
    double n_si = 3.8;
    double r_bare = pow((n_si - 1.0) / (n_si + 1.0), 2.0); /* ~34% без покриття */
    
    /* Зменшення відбиття біля мінімуму AR-покриття */
    double dev = (lambda_nm - target_lambda_nm) / target_lambda_nm;
    double r_ar = r_bare * (dev * dev + 0.05);
    return (r_ar > r_bare) ? r_bare : r_ar;
}

/* Обчислення спектра квантової ефективності */
int simulate_photodiode_spectrum(
    double w_depletion_um,
    double l_diffusion_um,
    double ar_min_lambda_nm,
    PhotodiodeSpectrumPoint *out_pts,
    size_t count
) {
    if (!out_pts || count == 0) {
        return -1;
    }

    double w_cm = w_depletion_um * 1e-4;
    double ln_cm = l_diffusion_um * 1e-4;

    for (size_t i = 0; i < count; i++) {
        double lambda = 300.0 + (double)i * (850.0 / (double)(count - 1));
        double r = surface_reflection(lambda, ar_min_lambda_nm);
        double alpha = silicon_absorption_coefficient(lambda);

        double iqe = 0.0;
        if (alpha > 0.0) {
            /* Збір у виснаженому шарі W та дифузія з L_n */
            double exp_aw = exp(-alpha * w_cm);
            double collection_factor = 1.0 - (exp_aw / (1.0 + alpha * ln_cm));
            iqe = collection_factor;
            if (iqe > 1.0) iqe = 1.0;
            if (iqe < 0.0) iqe = 0.0;
        }

        double eqe = (1.0 - r) * iqe;
        double responsivity = (eqe * (lambda * 1e-3)) / 1.23984;

        out_pts[i].wavelength_nm = lambda;
        out_pts[i].reflection_R = r;
        out_pts[i].alpha_cm1 = alpha;
        out_pts[i].iqe = iqe;
        out_pts[i].eqe = eqe;
        out_pts[i].responsivity_a_w = responsivity;
    }

    return 0;
}

int main(void) {
    const size_t steps = 10;
    PhotodiodeSpectrumPoint points[10];

    /* PIN-фотодіод: W = 20 мкм, L_n = 50 мкм, AR-покриття оптимізовано на 633 нм */
    if (simulate_photodiode_spectrum(20.0, 50.0, 633.0, points, steps) == 0) {
        printf("λ (нм) | R (%%)  | α (см⁻¹) | IQE (%%) | EQE (%%) | R_λ (А/Вт)\n");
        printf("-------+--------+----------+---------+---------+-----------\n");
        for (size_t i = 0; i < steps; i++) {
            printf("%6.1f | %6.2f | %8.1f | %7.2f | %7.2f | %9.4f\n",
                   points[i].wavelength_nm,
                   points[i].reflection_R * 100.0,
                   points[i].alpha_cm1,
                   points[i].iqe * 100.0,
                   points[i].eqe * 100.0,
                   points[i].responsivity_a_w);
        }
    }
    return 0;
}
