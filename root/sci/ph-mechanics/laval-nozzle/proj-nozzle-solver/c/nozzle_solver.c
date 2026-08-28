/* nozzle_solver.c — Чисельний модуль розрахунку сопла Лаваля мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define MAX_POINTS 500
#define EPSILON 1e-7
#define MAX_ITER 100

typedef struct {
    double gamma;       /* Показник адіабати (напр. 1.4) */
    double R;           /* Газова стала, Дж/(кг·К) (напр. 287.05) */
    double P0;          /* Повний тиск на вході, Па */
    double T0;          /* Повна температура на вході, К */
    double P_amb;       /* Протитиск навколишнього середовища, Па */
} gas_props_t;

typedef struct {
    double x;           /* Координата уздовж осі, м */
    double A;           /* Площа поперечного перерізу, м² */
    double M;           /* Число Маха */
    double P;           /* Статичний тиск, Па */
    double T;           /* Статична температура, К */
    double rho;         /* Густина, кг/м³ */
    double u;           /* Швидкість, м/с */
    bool is_shock;      /* Прапорець скачка ущільнення */
} flow_point_t;

/* Обчислення відношення A / A* за числом Маха */
double area_ratio_from_mach(double M, double gamma) {
    if (M <= 0.0) return 1e9;
    double g_term = (2.0 / (gamma + 1.0)) * (1.0 + 0.5 * (gamma - 1.0) * M * M);
    double exp_val = (gamma + 1.0) / (2.0 * (gamma - 1.0));
    return (1.0 / M) * pow(g_term, exp_val);
}

/* Чисельний розв'язок M за заданим A / A* методом Ньютона — Рафсона */
double solve_mach_from_area_ratio(double AR, double gamma, bool is_supersonic) {
    if (fabs(AR - 1.0) < 1e-6) return 1.0;
    
    double M = is_supersonic ? 2.5 : 0.2;
    for (int iter = 0; iter < MAX_ITER; iter++) {
        double current_AR = area_ratio_from_mach(M, gamma);
        double dAR_dM = current_AR * (M * M - 1.0) / (M * (1.0 + 0.5 * (gamma - 1.0) * M * M));
        
        double f = current_AR - AR;
        if (fabs(f) < EPSILON) break;
        
        M = M - f / dAR_dM;
        
        /* Затискання гілок */
        if (!is_supersonic && M >= 1.0) M = 0.9999;
        if (is_supersonic && M <= 1.0) M = 1.0001;
    }
    return M;
}

/* Обчислення термодинамічних параметрів за числом Маха */
void compute_point_state(flow_point_t *pt, double P0, double T0, double gamma, double R) {
    double M = pt->M;
    double temp_ratio = 1.0 / (1.0 + 0.5 * (gamma - 1.0) * M * M);
    double press_ratio = pow(temp_ratio, gamma / (gamma - 1.0));
    
    pt->T = T0 * temp_ratio;
    pt->P = P0 * press_ratio;
    pt->rho = pt->P / (R * pt->T);
    double a = sqrt(gamma * R * pt->T);
    pt->u = M * a;
}

/* Основний розрахунок 1D профілю сопла */
bool solve_nozzle_flow(const gas_props_t *gas, const double *x_arr, const double *A_arr, 
                       int num_pts, int throat_idx, flow_point_t *out_mesh) {
    if (!gas || !x_arr || !A_arr || !out_mesh || num_pts <= 0) return false;
    
    double A_throat = A_arr[throat_idx];
    
    for (int i = 0; i < num_pts; i++) {
        out_mesh[i].x = x_arr[i];
        out_mesh[i].A = A_arr[i];
        out_mesh[i].is_shock = false;
        
        double AR = A_arr[i] / A_throat;
        bool is_super = (i > throat_idx);
        
        out_mesh[i].M = solve_mach_from_area_ratio(AR, gas->gamma, is_super);
        compute_point_state(&out_mesh[i], gas->P0, gas->T0, gas->gamma, gas->R);
    }
    return true;
}

int main(void) {
    gas_props_t air = { .gamma = 1.4, .R = 287.05, .P0 = 1000000.0, .T0 = 300.0, .P_amb = 101325.0 };
    
    int n = 11;
    double x[11] = { 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0 };
    double A[11] = { 0.02, 0.015, 0.012, 0.01, 0.011, 0.014, 0.018, 0.023, 0.029, 0.035, 0.04 };
    int throat_index = 3; /* A = 0.01 в x = 0.3 */
    
    flow_point_t mesh[11];
    if (solve_nozzle_flow(&air, x, A, n, throat_index, mesh)) {
        printf("--- РОЗРАХУНОК СОПЛА ЛАВАЛЯ (C) ---\n");
        printf("x(m)\tA(m2)\tMach\tP(kPa)\tT(K)\tu(m/s)\n");
        for (int i = 0; i < n; i++) {
            printf("%.2f\t%.4f\t%.3f\t%.1f\t%.1f\t%.1f\n", 
                   mesh[i].x, mesh[i].A, mesh[i].M, mesh[i].P / 1000.0, mesh[i].T, mesh[i].u);
        }
    }
    return 0;
}
