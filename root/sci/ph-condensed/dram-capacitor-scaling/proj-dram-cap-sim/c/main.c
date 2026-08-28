#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define EPSILON_0 8.8541878176e-12
#define Q_E       1.602176634e-19
#define K_B       1.380649e-23
#define T_KELVIN  358.15

typedef struct {
    const char* name;
    double k_rel;
    double k_opt;
} Material;

typedef struct {
    int node_nm;
    int aspect_ratio;
    const char* mat_name;
    double d_phys_nm;
    double eot_nm;
    double c_cell_ff;
    double j_leak_a_cm2;
    bool meets_target;
} SimResult;

SimResult run_simulation(int node_nm, int aspect_ratio, Material mat, double d_phys_nm, double v_dd) {
    double f_m = node_nm * 1e-9;
    double d_m = d_phys_nm * 1e-9;
    double d_pillar = f_m * 0.7;
    double h_m = d_pillar * aspect_ratio;

    double a_cap = M_PI * d_pillar * h_m + M_PI * pow(d_pillar / 2.0, 2.0);

    double c_farads = (EPSILON_0 * mat.k_rel * a_cap) / d_m;
    double c_ff = c_farads * 1e15;
    double eot_nm = d_phys_nm * (3.9 / mat.k_rel);

    double e_field = v_dd / d_m;
    double phi_t_j = 1.0 * Q_E;
    double beta_pf = sqrt(Q_E / (M_PI * EPSILON_0 * mat.k_opt));
    double delta_phi = Q_E * beta_pf * sqrt(e_field);

    double exp_factor = - (phi_t_j - delta_phi) / (K_B * T_KELVIN);
    double c_0 = 1.0e-4;
    double j_pf = (c_0 * e_field * exp(exp_factor)) / 100.0;

    SimResult res = { node_nm, aspect_ratio, mat.name, d_phys_nm, eot_nm, c_ff, j_pf, c_ff >= 25.0 };
    return res;
}

int main(void) {
    Material mat_ono  = {"ONO",  5.5, 2.20};
    Material mat_zro2 = {"ZrO2", 35.0, 4.84};
    Material mat_zaz  = {"ZAZ",  32.0, 4.50};
    Material mat_tio2 = {"TiO2", 80.0, 6.25};

    SimResult results[5];
    results[0] = run_simulation(90, 12, mat_ono,  5.0, 1.2);
    results[1] = run_simulation(45, 25, mat_zro2, 6.0, 1.1);
    results[2] = run_simulation(22, 35, mat_zaz,  5.0, 1.0);
    results[3] = run_simulation(14, 45, mat_zaz,  4.2, 0.8);
    results[4] = run_simulation(10, 50, mat_tio2, 3.8, 0.7);

    printf("==================================================================================\n");
    printf("Вузол    | AR     | Матеріал  | d_phys   | EOT      | C_cell     | Статус (>=25fF)\n");
    printf("==================================================================================\n");

    for (int i = 0; i < 5; i++) {
        printf("%3d нм   | %4d:1 | %-9s | %6.1fнм | %6.2fнм | %7.2f fF | %s\n",
               results[i].node_nm, results[i].aspect_ratio, results[i].mat_name,
               results[i].d_phys_nm, results[i].eot_nm, results[i].c_cell_ff,
               results[i].meets_target ? "В НОРМІ" : "НЕДОСТАТНЬО");
    }
    printf("==================================================================================\n");

    return 0;
}
