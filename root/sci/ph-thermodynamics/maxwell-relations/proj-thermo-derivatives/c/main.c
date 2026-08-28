#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// Термодинамічна модель Ван-дер-Ваальса у мові C
typedef struct {
    double a; // Па·м⁶/моль²
    double b; // м³/моль
    double R; // Дж/(моль·К)
    double Cv_ideal;
} vdw_gas_t;

typedef struct {
    double dPdT_num;
    double dSdV_num;
    double abs_error;
    double internal_pressure;
} maxwell_check_t;

// Обчислення тиску P(T, V)
double vdw_pressure(const vdw_gas_t *gas, double T, double V) {
    return (gas->R * T) / (V - gas->b) - gas->a / (V * V);
}

// Чисельне диференціювання (∂P/∂T)_V
double compute_dPdT_c(const vdw_gas_t *gas, double T, double V, double h_T) {
    double P_plus  = vdw_pressure(gas, T + h_T, V);
    double P_minus = vdw_pressure(gas, T - h_T, V);
    return (P_plus - P_minus) / (2.0 * h_T);
}

// Чисельне диференціювання (∂P/∂V)_T
double compute_dPdV_c(const vdw_gas_t *gas, double T, double V, double h_V) {
    double P_plus  = vdw_pressure(gas, T, V + h_V);
    double P_minus = vdw_pressure(gas, T, V - h_V);
    return (P_plus - P_minus) / (2.0 * h_V);
}

// Функція перевірки співвідношення Максвелла
int verify_maxwell_c(const vdw_gas_t *gas, double T, double V, maxwell_check_t *out) {
    if (!gas || !out || T <= 0.0 || V <= gas->b) {
        return -1; // Некоректні аргументи
    }

    double h_T = 1e-4;
    double dPdT_num = compute_dPdT_c(gas, T, V, h_T);
    double dPdT_exact = gas->R / (V - gas->b);

    out->dPdT_num = dPdT_num;
    out->dSdV_num = dPdT_num; // За 3-м співвідношенням Максвелла
    out->abs_error = fabs(dPdT_num - dPdT_exact);
    
    double P_val = vdw_pressure(gas, T, V);
    out->internal_pressure = T * dPdT_num - P_val;

    return 0; // Успіх
}

void compute_grid_c(const vdw_gas_t *gas, double T_start, double T_end, int steps, double V_val) {
    printf("%10s %15s %18s %18s %15s\n", "T (K)", "P (Па)", "(∂U/∂V)_T (Па)", "a/V² (Теорія)", "μ_JT (К/Па)");
    printf("----------------------------------------------------------------------------\n");

    double dT = (T_end - T_start) / steps;
    double h_T = 1e-4;
    double h_V = 1e-6;

    for (int i = 0; i <= steps; ++i) {
        double T = T_start + i * dT;
        double P = vdw_pressure(gas, T, V_val);
        double dPdT = compute_dPdT_c(gas, T, V_val, h_T);
        double dPdV = compute_dPdV_c(gas, T, V_val, h_V);

        double int_press = T * dPdT - P;
        double exact_int_press = gas->a / (V_val * V_val);

        double dVdT_p = -dPdT / dPdV;
        double Cp = gas->Cv_ideal + T * (dPdT * dPdT) / (-dPdV);
        double mu_JT = (1.0 / Cp) * (T * dVdT_p - V_val);

        printf("%10.2f %15.4e %18.4e %18.4e %15.4e\n", T, P, int_press, exact_int_press, mu_JT);
    }
}

int main(void) {
    vdw_gas_t gas = {
        .a = 0.137,
        .b = 3.87e-5,
        .R = 8.31446,
        .Cv_ideal = 2.5 * 8.31446
    };

    maxwell_check_t check;
    if (verify_maxwell_c(&gas, 300.0, 1.0e-3, &check) == 0) {
        printf("--- C результати перевірки Максвелла ---\n");
        printf("(∂P/∂T)_V чисельне : %.6f Па/К\n", check.dPdT_num);
        printf("Похибка різниці   : %.6e Па/К\n", check.abs_error);
        printf("(∂U/∂V)_T калоричне: %.2f Па\n\n", check.internal_pressure);
    }

    compute_grid_c(&gas, 200.0, 600.0, 5, 1.0e-3);
    return 0;
}
