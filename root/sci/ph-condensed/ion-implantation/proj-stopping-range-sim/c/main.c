/* Simulation of Ion Implantation via Monte Carlo (C99) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846
#define SI_DENSITY 5.02e22      /* Atom density of Si (atoms/cm^3) */
#define LAMBDA_STEP 2.5e-8      /* Free path step (cm) = 2.5 Angstrom */
#define E_DISPLACEMENT 15.0     /* Displacement energy threshold for Si (eV) */
#define E_SURFACE_BIND 4.7      /* Surface binding energy for Si sputtering (eV) */
#define MAX_HISTOGRAM_BINS 100

typedef struct {
    double energy_ev;       /* Current kinetic energy (eV) */
    double x_cm;            /* Depth coordinate (cm) */
    double y_cm;            /* Lateral coordinate (cm) */
    double dir_x;           /* Direction cosine X */
    double dir_y;           /* Direction cosine Y */
    int is_recoil;          /* Flag: 0 = primary ion, 1 = recoil Si atom */
} IonParticle;

typedef struct {
    double initial_energy_ev;
    double m1_amu;
    double z1;
    double m2_amu;
    double z2;
    double ke_coeff;        /* Electronic stopping factor (eV^0.5 / cm) */
    int total_ions;
    double depth_max_cm;
} SimConfig;

/* Simple uniform random generator [0, 1) */
static double rand_uniform(void) {
    return (double)rand() / ((double)RAND_MAX + 1.0);
}

/* Recursive cascade simulation for recoil atoms */
void simulate_recoil_cascade(const SimConfig *cfg, double start_x, double start_y, double start_energy, int *vacancies_hist) {
    if (start_energy < E_DISPLACEMENT) return;

    IonParticle recoil;
    recoil.energy_ev = start_energy - E_DISPLACEMENT;
    recoil.x_cm = start_x;
    recoil.y_cm = start_y;
    recoil.dir_x = (rand_uniform() - 0.5) * 2.0;
    recoil.dir_y = (rand_uniform() - 0.5) * 2.0;
    recoil.is_recoil = 1;

    double max_b = 1.5e-8;
    while (recoil.energy_ev > E_DISPLACEMENT && recoil.x_cm >= 0.0 && recoil.x_cm < cfg->depth_max_cm) {
        double dE_elec = cfg->ke_coeff * sqrt(recoil.energy_ev) * LAMBDA_STEP;
        recoil.energy_ev -= dE_elec;
        if (recoil.energy_ev <= 0.0) break;

        double r = rand_uniform();
        double b = sqrt(r) * max_b;
        double sin_half_theta = 1.0 / sqrt(1.0 + (b * b * 1e16) * (recoil.energy_ev / 500.0));
        double T_transferred = recoil.energy_ev * (sin_half_theta * sin_half_theta);

        if (T_transferred > E_DISPLACEMENT) {
            int bin = (int)((recoil.x_cm / cfg->depth_max_cm) * MAX_HISTOGRAM_BINS);
            if (bin >= 0 && bin < MAX_HISTOGRAM_BINS) {
                vacancies_hist[bin]++;
            }
            /* Secondary recoil cascade recursive call */
            if (T_transferred > 50.0) {
                simulate_recoil_cascade(cfg, recoil.x_cm, recoil.y_cm, T_transferred, vacancies_hist);
            }
        }

        recoil.energy_ev -= T_transferred;
        recoil.x_cm += recoil.dir_x * LAMBDA_STEP;
        recoil.y_cm += recoil.dir_y * LAMBDA_STEP;
    }
}

/* Simulate trajectory of a single primary ion */
void simulate_ion(const SimConfig *cfg, IonParticle *ion, int *vacancies_hist, int *range_hist, int *sputtered_count) {
    ion->energy_ev = cfg->initial_energy_ev;
    ion->x_cm = 0.0;
    ion->y_cm = 0.0;
    ion->dir_x = 1.0; /* Injected straight inside (along X axis) */
    ion->dir_y = 0.0;
    ion->is_recoil = 0;

    double max_b = 1.5e-8; /* Max impact parameter (cm) */
    double t_max_factor = (4.0 * cfg->m1_amu * cfg->m2_amu) / 
                          ((cfg->m1_amu + cfg->m2_amu) * (cfg->m1_amu + cfg->m2_amu));

    while (ion->energy_ev > 5.0 && ion->x_cm >= 0.0 && ion->x_cm < cfg->depth_max_cm) {
        /* 1. Electronic stopping loss */
        double dE_elec = cfg->ke_coeff * sqrt(ion->energy_ev) * LAMBDA_STEP;
        ion->energy_ev -= dE_elec;
        if (ion->energy_ev <= 0.0) break;

        /* 2. Nuclear collision selection */
        double r = rand_uniform();
        double b = sqrt(r) * max_b;

        /* Reduced energy proxy for center-of-mass scattering angle */
        double sin_half_theta = 1.0 / sqrt(1.0 + (b * b * 1e16) * (ion->energy_ev / 1000.0));
        double T_transferred = t_max_factor * ion->energy_ev * (sin_half_theta * sin_half_theta);

        /* 3. Check for Frenkel vacancy creation & recoil cascade */
        if (T_transferred > E_DISPLACEMENT) {
            int bin = (int)((ion->x_cm / cfg->depth_max_cm) * MAX_HISTOGRAM_BINS);
            if (bin >= 0 && bin < MAX_HISTOGRAM_BINS) {
                vacancies_hist[bin]++;
            }
            if (ion->x_cm < 1.0e-7 && T_transferred > E_SURFACE_BIND) {
                (*sputtered_count)++;
            }
            /* Trigger secondary recoil atom tracking if transferred energy is high */
            if (T_transferred > 100.0) {
                simulate_recoil_cascade(cfg, ion->x_cm, ion->y_cm, T_transferred, vacancies_hist);
            }
        }

        ion->energy_ev -= T_transferred;

        /* 4. Angular deflection */
        double theta_lab = sin_half_theta * (cfg->m2_amu / (cfg->m1_amu + cfg->m2_amu));
        double phi = (rand_uniform() - 0.5) * 2.0 * theta_lab;

        double new_dir_x = ion->dir_x * cos(phi) - ion->dir_y * sin(phi);
        double new_dir_y = ion->dir_x * sin(phi) + ion->dir_y * cos(phi);
        double norm = sqrt(new_dir_x * new_dir_x + new_dir_y * new_dir_y);

        ion->dir_x = new_dir_x / norm;
        ion->dir_y = new_dir_y / norm;

        /* 5. Advance position */
        ion->x_cm += ion->dir_x * LAMBDA_STEP;
        ion->y_cm += ion->dir_y * LAMBDA_STEP;
    }

    /* Record final stopping range location */
    if (ion->x_cm >= 0.0 && ion->x_cm < cfg->depth_max_cm) {
        int bin = (int)((ion->x_cm / cfg->depth_max_cm) * MAX_HISTOGRAM_BINS);
        if (bin >= 0 && bin < MAX_HISTOGRAM_BINS) {
            range_hist[bin]++;
        }
    }
}

int main(void) {
    SimConfig cfg = {
        .initial_energy_ev = 50000.0, /* 50 keV Boron */
        .m1_amu = 11.0,
        .z1 = 5.0,
        .m2_amu = 28.08,
        .z2 = 14.0,
        .ke_coeff = 1.2e6,
        .total_ions = 10000,
        .depth_max_cm = 400e-7 /* 400 nm max depth */
    };

    int *vacancies_hist = (int*)calloc(MAX_HISTOGRAM_BINS, sizeof(int));
    int *range_hist = (int*)calloc(MAX_HISTOGRAM_BINS, sizeof(int));
    int sputtered_count = 0;

    if (!vacancies_hist || !range_hist) {
        free(vacancies_hist); free(range_hist);
        return 1;
    }

    srand(42);
    for (int i = 0; i < cfg.total_ions; ++i) {
        IonParticle ion;
        simulate_ion(&cfg, &ion, vacancies_hist, range_hist, &sputtered_count);
    }

    printf("=== Monte Carlo BCA Ion Implantation Simulation (C99) ===\n");
    printf("Total Ions Simulated: %d\n", cfg.total_ions);
    printf("Total Surface Sputtered Si Atoms: %d\n", sputtered_count);
    printf("Depth (nm) | Ion Stops (Count) | Vacancy Cascade (Count)\n");
    for (int i = 0; i < MAX_HISTOGRAM_BINS; i += 10) {
        double depth_nm = (i + 0.5) * (cfg.depth_max_cm * 1e7 / MAX_HISTOGRAM_BINS);
        printf("%9.1f  | %17d | %23d\n", depth_nm, range_hist[i], vacancies_hist[i]);
    }

    free(vacancies_hist);
    free(range_hist);
    return 0;
}
