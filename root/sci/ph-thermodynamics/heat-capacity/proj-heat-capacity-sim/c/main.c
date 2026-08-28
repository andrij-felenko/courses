#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define R_GAS 8.314462618
#define PI 3.14159265358979323846

/* Структура для зберігання параметрів матеріалу */
typedef struct {
    const char* name;
    double debye_temp;       /* Температура Дебая, К */
    double einstein_temp;    /* Температура Ейнштейна, К */
    double sommerfeld_gamma; /* Коефіцієнт Зоммерфельда, Дж/(моль*К^2) */
} MaterialParams;

/* Підінтегральна функція Дебая: f(x) = x^4 * exp(x) / (exp(x) - 1)^2 */
static double debye_integrand(double x) {
    if (x < 1e-6) {
        return x * x;
    }
    if (x > 80.0) {
        return 0.0;
    }
    double exp_x = exp(x);
    double denom = exp_x - 1.0;
    return (x * x * x * x * exp_x) / (denom * denom);
}

/* Обчислення інтеграла Дебая методом Сімпсона */
double compute_debye_integral(double x_max, int num_steps) {
    if (x_max < 1e-4) {
        return (x_max * x_max * x_max) / 3.0;
    }
    if (x_max > 40.0) {
        return (4.0 * PI * PI * PI * PI) / 15.0;
    }

    if (num_steps % 2 != 0) num_steps++;
    double h = x_max / num_steps;
    double sum = debye_integrand(0.0) + debye_integrand(x_max);

    for (int i = 1; i < num_steps; i++) {
        double x = i * h;
        double weight = (i % 2 == 0) ? 2.0 : 4.0;
        sum += weight * debye_integrand(x);
    }

    return sum * (h / 3.0);
}

/* Молярна теплоємність за моделлю Ейнштейна */
double heat_capacity_einstein(double T, double T_E) {
    if (T <= 0.0) return 0.0;
    double x = T_E / T;
    if (x > 80.0) return 0.0;
    if (x < 1e-4) return 3.0 * R_GAS;

    double exp_x = exp(x);
    double denom = exp_x - 1.0;
    return 3.0 * R_GAS * (x * x * exp_x) / (denom * denom);
}

/* Молярна теплоємність за моделлю Дебая */
double heat_capacity_debye(double T, double Θ_D) {
    if (T <= 0.0) return 0.0;
    double x_max = Θ_D / T;
    if (x_max < 1e-4) {
        return 3.0 * R_GAS * (1.0 - (1.0 / 20.0) * x_max * x_max);
    }
    double integral = compute_debye_integral(x_max, 200);
    double factor = 9.0 * R_GAS * pow(T / Θ_D, 3.0);
    return factor * integral;
}

/* Електронна теплоємність Зоммерфельда */
double heat_capacity_electronic(double T, double gamma) {
    return gamma * T;
}

/* Обертальна теплоємність двоатомного газу з квантовим підсумовуванням */
double heat_capacity_rotational(double T, double T_rot) {
    if (T <= 0.0) return 0.0;
    double y = T_rot / T;
    if (y > 10.0) return 0.0; /* Повне виморожування обертання */

    double z = 0.0, z1 = 0.0, z2 = 0.0;
    for (int j = 0; j < 50; j++) {
        double ej = j * (j + 1) * y;
        if (ej > 80.0) break;
        double w = (2 * j + 1) * exp(-ej);
        z += w;
        z1 += w * ej;
        z2 += w * ej * ej;
    }

    double mean_e = z1 / z;
    double mean_e2 = z2 / z;
    double var_e = mean_e2 - mean_e * mean_e;
    return R_GAS * var_e;
}

/* Лінійна регресія для МНК у координатах (C/T) від T^2 */
void fit_low_temp_capacity(const double* T_arr, const double* C_arr, int n,
                            double* out_gamma, double* out_debye_temp) {
    double sum_x = 0.0, sum_y = 0.0, sum_xx = 0.0, sum_xy = 0.0;

    for (int i = 0; i < n; i++) {
        double x = T_arr[i] * T_arr[i]; /* T^2 */
        double y = C_arr[i] / T_arr[i]; /* C / T */
        sum_x += x;
        sum_y += y;
        sum_xx += x * x;
        sum_xy += x * y;
    }

    double delta = n * sum_xx - sum_x * sum_x;
    double gamma = (sum_y * sum_xx - sum_x * sum_xy) / delta;
    double A = (n * sum_xy - sum_x * sum_y) / delta;

    *out_gamma = gamma;
    *out_debye_temp = pow((12.0 * PI * PI * PI * PI * R_GAS) / (5.0 * A), 1.0 / 3.0);
}

int main(void) {
    MaterialParams copper = {"Мідь (Cu)", 343.0, 240.0, 0.000695};

    printf("=== МОДЕЛЮВАННЯ ТЕПЛОЄМНОСТІ МАТЕРІАЛУ: %s ===\n", copper.name);
    printf(" T (K) | C_Einstein |  C_Debye   | C_Electron | C_Total(Deb+El)\n");
    printf("-------+------------+------------+------------+----------------\n");

    double test_temps[] = {1.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 300.0, 500.0};
    int num_t = sizeof(test_temps) / sizeof(test_temps[0]);

    for (int i = 0; i < num_t; i++) {
        double T = test_temps[i];
        double c_einst = heat_capacity_einstein(T, copper.einstein_temp);
        double c_deb   = heat_capacity_debye(T, copper.debye_temp);
        double c_el    = heat_capacity_electronic(T, copper.sommerfeld_gamma);
        double c_tot   = c_deb + c_el;

        printf("%6.1f | %10.4f | %10.4f | %10.5f | %15.4f\n",
               T, c_einst, c_deb, c_el, c_tot);
    }

    printf("\n=== ОБЕРТАЛЬНА ТЕПЛОЄМНОСТЬ ГАЗУ ВОДНЮ H2 (T_rot = 85.4 K) ===\n");
    printf(" T (K) | C_rot / R | C_rot (Дж/(моль*К))\n");
    printf("-------+-----------+--------------------\n");
    double h2_temps[] = {10.0, 30.0, 50.0, 85.4, 150.0, 300.0};
    for (int i = 0; i < 6; i++) {
        double T = h2_temps[i];
        double crot = heat_capacity_rotational(T, 85.4);
        printf("%6.1f | %9.4f | %18.4f\n", T, crot / R_GAS, crot);
    }

    /* Моделювання МНК для низьких температур */
    printf("\n=== МНК ОБРОБКА НИЗЬКОТЕМПЕРАТУРНИХ ДАНИХ (1 K - 5 K) ===\n");
    double exp_T[5] = {1.0, 2.0, 3.0, 4.0, 5.0};
    double exp_C[5];
    double true_A = (12.0 * pow(PI, 4.0) * R_GAS) / (5.0 * pow(copper.debye_temp, 3.0));

    for (int i = 0; i < 5; i++) {
        exp_C[i] = copper.sommerfeld_gamma * exp_T[i] + true_A * pow(exp_T[i], 3.0);
    }

    double calc_gamma, calc_debye;
    fit_low_temp_capacity(exp_T, exp_C, 5, &calc_gamma, &calc_debye);

    printf("Відновлений gamma:  %.6f Дж/(моль*К^2)\n", calc_gamma);
    printf("Відновлена Theta_D: %.2f K\n", calc_debye);

    return 0;
}
