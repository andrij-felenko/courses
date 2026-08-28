/* c */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фундаментальні фізичні константи (SI) */
#define HBAR 1.054571817e-34       /* Зведена стала Планка, Дж·с */
#define MASS_E 9.1093837015e-31    /* Маса спокою електрона, кг */
#define SPEED_OF_LIGHT 299792458.0 /* Швидкість світла, м/с */
#define BOLTZMANN_K 1.380649e-23   /* Стала Больцмана, Дж/К */
#define EV_TO_JOULE 1.602176634e-19/* 1 еВ у Джоулях */
#define M_PI 3.14159265358979323846

/* Структура для збереження результатів моделювання */
typedef struct {
    double n_e;              /* Концентрація електронів (1/м³) */
    double p_F;              /* Імпульс Фермі (кг·м/с) */
    double v_F;              /* Швидкість Фермі (м/с) */
    double E_F_eV;           /* Енергія Фермі (еВ) */
    double T_F;              /* Температура Фермі (К) */
    double total_energy_J;   /* Сумарна кінетична енергія при T=0 K (Дж) */
    double pressure_Pa;      /* Тиск квантового виродження (Па) */
    double pressure_atm;     /* Тиск квантового виродження (атмосфер) */
    int is_relativistic;     /* Прапор релятивістського режиму */
} FermiGasProfile;

/* Обчислення густини станів g(E) = (V / 2π²) * (2m_e/ℏ²)^(3/2) * sqrt(E) */
double density_of_states(double E_joules, double volume_m3) {
    if (E_joules <= 0.0) return 0.0;
    double factor = (volume_m3 / (2.0 * M_PI * M_PI)) * pow(2.0 * MASS_E / (HBAR * HBAR), 1.5);
    return factor * sqrt(E_joules);
}

/* Обчислення ймовірності заповнення за розподілом Фермі — Дірака */
double fermi_dirac_distribution(double E_joules, double mu_joules, double temp_K) {
    if (temp_K <= 0.0) {
        return (E_joules <= mu_joules) ? 1.0 : 0.0;
    }
    double arg = (E_joules - mu_joules) / (BOLTZMANN_K * temp_K);
    if (arg > 700.0) return 0.0;   /* Запобігання числовому переповненню exp */
    if (arg < -700.0) return 1.0;
    return 1.0 / (exp(arg) + 1.0);
}

/* Основна функція обчислення профілю фермі-газу */
FermiGasProfile analyze_fermi_gas(double total_electrons, double volume_m3) {
    FermiGasProfile prof;
    prof.n_e = total_electrons / volume_m3;

    /* Імпульс Фермі p_F = ℏ * (3 * π² * n_e)^(1/3) */
    double k_F = cbrt(3.0 * M_PI * M_PI * prof.n_e);
    prof.p_F = HBAR * k_F;
    prof.v_F = prof.p_F / MASS_E;

    /* Перевірка релятивістського критерію: p_F >= 0.1 * m_e * c */
    double rest_energy_J = MASS_E * SPEED_OF_LIGHT * SPEED_OF_LIGHT;
    double E_F_nonrel_J = (prof.p_F * prof.p_F) / (2.0 * MASS_E);

    if (E_F_nonrel_J > 0.1 * rest_energy_J) {
        prof.is_relativistic = 1;
        /* Релятивістська енергія: E_F = sqrt(p_F² c² + m² c⁴) - m c² */
        double total_E = sqrt(prof.p_F * prof.p_F * SPEED_OF_LIGHT * SPEED_OF_LIGHT + rest_energy_J * rest_energy_J);
        double E_F_rel_J = total_E - rest_energy_J;
        prof.E_F_eV = E_F_rel_J / EV_TO_JOULE;
        prof.total_energy_J = 0.75 * total_electrons * E_F_rel_J;
        prof.pressure_Pa = 0.25 * prof.n_e * E_F_rel_J;
    } else {
        prof.is_relativistic = 0;
        prof.E_F_eV = E_F_nonrel_J / EV_TO_JOULE;
        prof.total_energy_J = 0.60 * total_electrons * E_F_nonrel_J;
        prof.pressure_Pa = 0.40 * prof.n_e * E_F_nonrel_J;
    }

    prof.T_F = (prof.E_F_eV * EV_TO_JOULE) / BOLTZMANN_K;
    prof.pressure_atm = prof.pressure_Pa / 101325.0;

    return prof;
}

/* Демонстрація розрахунку для різних фізичних систем */
void print_profile(const char* title, FermiGasProfile prof) {
    printf("==================================================\n");
    printf(" СИСТЕМА: %s\n", title);
    printf("==================================================\n");
    printf(" Режим:                      %s\n", prof.is_relativistic ? "РЕЛЯТИВІСТСЬКИЙ" : "Нерелятивістський");
    printf(" Концентрація e⁻ (n_e):      %.3e m⁻³\n", prof.n_e);
    printf(" Імпульс Фермі (p_F):        %.3e kg·m/s\n", prof.p_F);
    printf(" Швидкість Фермі (v_F):      %.3e m/s (%.2f%% від c)\n", prof.v_F, (prof.v_F / SPEED_OF_LIGHT) * 100.0);
    printf(" Енергія Фермі (E_F):        %.3f eV\n", prof.E_F_eV);
    printf(" Температура Фермі (T_F):    %.1f K\n", prof.T_F);
    printf(" Повна енергія (T=0 K):      %.3e J\n", prof.total_energy_J);
    printf(" Тиск виродження (P_deg):    %.3e Pa (%.2e atm)\n\n", prof.pressure_Pa, prof.pressure_atm);
}

int main(void) {
    /* 1. Провідні електрони в Міді (Cu): n_e ≈ 8.47e28 m⁻³ */
    double vol_sample = 1.0e-6; /* 1 см³ */
    FermiGasProfile cu = analyze_fermi_gas(8.47e28 * vol_sample, vol_sample);
    print_profile("Мідний провідник (Cu, 1 cm³)", cu);

    /* 2. Провідні електрони в Натрії (Na): n_e ≈ 2.65e28 m⁻³ */
    FermiGasProfile na = analyze_fermi_gas(2.65e28 * vol_sample, vol_sample);
    print_profile("Металевий Натрій (Na, 1 cm³)", na);

    /* 3. Надра Білого Карлика: n_e ≈ 1.0e36 m⁻³ */
    FermiGasProfile wd = analyze_fermi_gas(1.0e36 * vol_sample, vol_sample);
    print_profile("Ядро Білого Карлика (1 cm³)", wd);

    return 0;
}
