/* c */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define KB_EV 8.617333262145e-5  /* Стала Больцмана в еВ/К */
#define M_0   9.1093837015e-31   /* Маса спокою електрона в кг */
#define H_J   6.62607015e-34     /* Стала Планка в Дж·с */
#define KB_J  1.380649e-23       /* Стала Больцмана в Дж/К */

/* Структура параметрів напівпровідника (Si) */
typedef struct {
    double Eg;       /* Ширина забороненої зони при 300K, еВ */
    double Nc300;    /* Eфективна густина станів N_c при 300K, см^-3 */
    double Nv300;    /* Eфективна густина станів N_v при 300K, см^-3 */
    double Nd;       /* Концентрація донорів, см^-3 */
    double Ed_bind;  /* Енергія зв'язку донора (E_c - E_d), еВ */
    double Na;       /* Концентрація акцепторів, см^-3 */
    double Ea_bind;  /* Енергія зв'язку акцептора (E_a - E_v), еВ */
} SemiParams;

/* Неузгодження заряду f(E_F) = p + Nd+ - n - Na- */
static double charge_imbalance(double Ef, double T, const SemiParams *p) {
    double kBT = KB_EV * T;
    
    /* Температурна маштабованість густини станів T^(3/2) */
    double Nc = p->Nc300 * pow(T / 300.0, 1.5);
    double Nv = p->Nv300 * pow(T / 300.0, 1.5);

    double n = Nc * exp(-(p->Eg - Ef) / kBT);
    double hole_p = Nv * exp(-Ef / kBT);

    double Nd_plus = p->Nd / (1.0 + 2.0 * exp((Ef - (p->Eg - p->Ed_bind)) / kBT));
    double Na_minus = p->Na / (1.0 + 4.0 * exp(((p->Ea_bind) - Ef) / kBT));

    return hole_p + Nd_plus - n - Na_minus;
}

/* Пошук корня рівняння бісекцією */
static double find_fermi_level(double T, const SemiParams *p) {
    double low = 0.0;       /* E_v = 0 еВ */
    double high = p->Eg;    /* E_c = Eg еВ */
    double mid = 0.5 * (low + high);

    for (int iter = 0; iter < 100; ++iter) {
        mid = 0.5 * (low + high);
        double f_mid = charge_imbalance(mid, T, p);

        if (fabs(f_mid) < 1.0e-6 || (high - low) < 1.0e-7) {
            break;
        }

        if (f_mid > 0.0) {
            low = mid;  /* Надлишок позитивного заряду -> піднімаємо E_F */
        } else {
            high = mid; /* Надлишок негативного заряду -> опускаємо E_F */
        }
    }
    return mid;
}

int main(void) {
    SemiParams silicon = {
        .Eg = 1.12,
        .Nc300 = 2.86e19,
        .Nv300 = 3.10e19,
        .Nd = 1.0e16,      /* n-тип легування 10^16 см^-3 */
        .Ed_bind = 0.045,  /* Фосфор у Si: E_c - E_d = 45 меВ */
        .Na = 0.0,
        .Ea_bind = 0.045
    };

    printf("========================================================================\n");
    printf("T (K)  | E_F (еВ) | n (см^-3)    | p (см^-3)    | n_i (см^-3)  | Режим\n");
    printf("========================================================================\n");

    for (double T = 50.0; T <= 600.0; T += 50.0) {
        double Ef = find_fermi_level(T, &silicon);
        double kBT = KB_EV * T;
        double Nc = silicon.Nc300 * pow(T / 300.0, 1.5);
        double Nv = silicon.Nv300 * pow(T / 300.0, 1.5);

        double n = Nc * exp(-(silicon.Eg - Ef) / kBT);
        double p = Nv * exp(-Ef / kBT);
        double ni = sqrt(Nc * Nv) * exp(-silicon.Eg / (2.0 * kBT));

        const char *regime = "Домішковий";
        if (T < 100.0) regime = "Виморожування";
        else if (n < 1.05 * ni) regime = "Власний";

        printf("%6.1f | %8.4f | %12.4e | %12.4e | %12.4e | %s\n",
               T, Ef, n, p, ni, regime);
    }
    printf("========================================================================\n");

    return 0;
}
