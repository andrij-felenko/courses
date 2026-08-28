#include <stdio.h>
#include <math.h>

/* Фундаментальні фізичні константи */
#define HBAR 1.0545718e-34
#define E_CHARGE 1.6021766e-19
#define KB 1.380649e-23
#define PI 3.14159265358979323846

/* Структура параметрів гетероструктури YIG/Pt */
typedef struct {
    double Ms;          /* Намагніченість насичення YIG (А/м) */
    double lambda_mp;   /* Магнон-фононна довжина релаксації (м) */
    double g_mix;       /* Спінова міжфазна провідність (м^-2) */
    double rho_pt;      /* Питомий опір Pt (Ом·м) */
    double lambda_sd;   /* Довжина спінової дифузії Pt (м) */
    double theta_sh;    /* Кут спінового Холла */
    double L_length;    /* Довжина контакту (м) */
} SseSystemParams;

/* Обчислення густини інжектованого спінового струму */
double calc_injected_spin_current(const SseSystemParams* p, double grad_T) {
    return (p->g_mix * KB * p->lambda_mp / (2.0 * PI * p->Ms)) * grad_T;
}

/* Обчислення напруги ISHE з обробкою граничних випадків */
double calc_ishe_voltage(const SseSystemParams* p, double Js_z, double d_pt_meters) {
    double x = d_pt_meters / (2.0 * p->lambda_sd);
    double F_factor;
    
    if (x < 1e-4) {
        F_factor = 1.0 / (2.0 * p->lambda_sd);
    } else {
        F_factor = tanh(x) / d_pt_meters;
    }
    
    double prefactor = p->L_length * p->theta_sh * p->rho_pt * p->lambda_sd * (2.0 * E_CHARGE / HBAR);
    return prefactor * Js_z * F_factor;
}

int main(void) {
    SseSystemParams params = {
        .Ms = 1.4e5,
        .lambda_mp = 500e-9,
        .g_mix = 1.2e19,
        .rho_pt = 20e-8,
        .lambda_sd = 1.5e-9,
        .theta_sh = 0.08,
        .L_length = 5.0e-3
    };

    double grad_T = 1.0e6; /* 1 К/мкм */
    double test_thicknesses_nm[] = {0.5, 1.0, 1.5, 3.0, 4.5, 6.0, 10.0};
    size_t num_tests = sizeof(test_thicknesses_nm) / sizeof(test_thicknesses_nm[0]);

    double Js_z = calc_injected_spin_current(&params, grad_T);

    printf("=== C Симулятор спінового ефекту Зеєбека ===\n");
    printf("Градієнт температури ∇T = %.1e К/м\n", grad_T);
    printf("Спіновий струм J_s^z = %.4e Дж/м²\n\n", Js_z);
    printf("%-12s | %-15s\n", "d_Pt (нм)", "V_ISHE (мкВ)");
    printf("-----------------------------------\n");

    for (size_t i = 0; i < num_tests; i++) {
        double d_m = test_thicknesses_nm[i] * 1e-9;
        double v_volts = calc_ishe_voltage(&params, Js_z, d_m);
        printf("%-12.1f | %-15.4f\n", test_thicknesses_nm[i], v_volts * 1e6);
    }

    return 0;
}
