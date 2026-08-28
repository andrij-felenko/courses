#include <stdio.h>
#include <math.h>
#include <stdbool.h>

/* Стандартні коефіцієнти формули Вейцзеккера (у МеВ) */
#define AV 15.75
#define AS 17.80
#define AC 0.711
#define AA 23.70
#define AP 11.18

/* Масові та енергетичні константи */
#define MEV_PER_AMU 931.494028
#define MASS_PROTON_AMU 1.00727647
#define MASS_NEUTRON_AMU 1.00866491

typedef struct {
    int Z;
    int A;
    int N;
    double E_volume;
    double E_surface;
    double E_coulomb;
    double E_asymmetry;
    double E_pairing;
    double E_binding;
    double E_specific;
    double mass_defect_u;
    double atomic_mass_u;
} NuclearProperties;

/* Обчислення допоміжної функції кореня */
static inline double stroke_sqrt_a(int A) {
    return sqrt((double)A);
}

/* Розрахунок спарювального доданка E_p */
static double calc_pairing(int Z, int N, int A) {
    if (Z % 2 == 0 && N % 2 == 0) {
        return AP / stroke_sqrt_a(A);       /* парно-парні (найбільш стійкі) */
    } else if (Z % 2 != 0 && N % 2 != 0) {
        return -AP / stroke_sqrt_a(A);     /* непарно-непарні (найменш стійкі) */
    }
    return 0.0;                             /* непарно-парні або парно-непарні */
}

/* Обчислення ядерних характеристик */
bool calculate_nucleus(int Z, int A, NuclearProperties *res) {
    if (Z <= 0 || A <= 0 || Z > A) {
        return false;
    }
    
    int N = A - Z;
    double a_val = (double)A;
    double z_val = (double)Z;
    
    double ev = AV * a_val;
    double es = -AS * pow(a_val, 2.0 / 3.0);
    double ec = -AC * z_val * (z_val - 1.0) / pow(a_val, 1.0 / 3.0);
    double ea = -AA * pow(a_val - 2.0 * z_val, 2.0) / a_val;
    double ep = calc_pairing(Z, N, A);
    
    double eb = ev + es + ec + ea + ep;
    double spec = eb / a_val;
    double dm_u = eb / MEV_PER_AMU;
    double mass_u = z_val * MASS_PROTON_AMU + (double)N * MASS_NEUTRON_AMU - dm_u;
    
    res->Z = Z;
    res->A = A;
    res->N = N;
    res->E_volume = ev;
    res->E_surface = es;
    res->E_coulomb = ec;
    res->E_asymmetry = ea;
    res->E_pairing = ep;
    res->E_binding = eb;
    res->E_specific = spec;
    res->mass_defect_u = dm_u;
    res->atomic_mass_u = mass_u;
    
    return true;
}

/* Пошук оптимального Z на лінії бета-стабільності */
double find_z_beta_stable(int A) {
    double a_val = (double)A;
    return a_val / (2.0 + (AC / (2.0 * AA)) * pow(a_val, 2.0 / 3.0));
}

int main(void) {
    printf("=== КАЛЬКУЛЯТОР ВЕЙЦЗЕККЕРА (C) ===\n\n");
    
    NuclearProperties u235;
    if (calculate_nucleus(92, 235, &u235)) {
        printf("Нуклід: U-235 (Z=%d, A=%d, N=%d)\n", u235.Z, u235.A, u235.N);
        printf(" Об'ємний член (E_v):      +%8.2f МеВ\n", u235.E_volume);
        printf(" Поверхневий член (E_s):   %8.2f МеВ\n", u235.E_surface);
        printf(" Кулонівський член (E_c):  %8.2f МеВ\n", u235.E_coulomb);
        printf(" Член асиметрії (E_a):     %8.2f МеВ\n", u235.E_asymmetry);
        printf(" Член спарювання (E_p):    +%8.2f МеВ\n", u235.E_pairing);
        printf(" ----------------------------------------\n");
        printf(" Повна енергія зв'язку:     %8.2f МеВ\n", u235.E_binding);
        printf(" Питома енергія зв'язку:    %8.4f МеВ/нуклон\n", u235.E_specific);
        printf(" Дефект маси:               %8.5f а.о.м.\n", u235.mass_defect_u);
        printf(" Розрахункова маса атома:   %8.5f а.о.м.\n", u235.atomic_mass_u);
        printf(" Z_min бета-стабільності:   %8.2f (факт Z=92)\n\n", find_z_beta_stable(235));
    }
    
    return 0;
}
