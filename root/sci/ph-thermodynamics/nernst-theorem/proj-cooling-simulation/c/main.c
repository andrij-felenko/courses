#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фундаментальні фізичні константи у системі SI */
#define R_GAS 8.314462618
#define MU_B 9.274010078e-24
#define K_B 1.380649e-23
#define PI 3.14159265358979323846

/* Структура для зберігання фізичних параметрів парамагнітної солі */
typedef struct {
    double g_factor;     /* Фактор Ланде магнітного йона */
    double debye_temp;   /* Температура Дебая кристалічної ґратки (К) */
    double b_min;        /* Внутрішнє диполь-дипольне поле солі (Тл) */
    double b_max;        /* Максимальне зовнішнє магнітне поле (Тл) */
} ParamagneticSalt;

/* Обчислення магнітної ентропії спінів у молі речовини (Дж/(моль*К)) */
double calc_spin_entropy(const ParamagneticSalt *salt, double T, double B) {
    if (T <= 0.0) return 0.0;
    double y = (salt->g_factor * MU_B * B) / (2.0 * K_B * T);
    /* Запобігання переповненню типу double при у прямуючому до нескінченності */
    if (y > 50.0) return 0.0; 
    return R_GAS * (log(2.0 * cosh(y)) - y * tanh(y));
}

/* Обчислення ентропії фононів дебаївської ґратки */
double calc_lattice_entropy(const ParamagneticSalt *salt, double T) {
    if (T <= 0.0) return 0.0;
    double ratio = T / salt->debye_temp;
    return (4.0 / 5.0) * pow(PI, 4.0) * R_GAS * pow(ratio, 3.0);
}

/* Повна ентропія системи: магнітна + ґратчаста */
double total_entropy(const ParamagneticSalt *salt, double T, double B) {
    return calc_spin_entropy(salt, T, B) + calc_lattice_entropy(salt, T);
}

/* Чисельне розв'язання рівняння S(T, B_target) = target_S методом бісекції */
double find_adiabatic_temperature(const ParamagneticSalt *salt, double target_S, double B_target, double T_min, double T_max) {
    double low = T_min, high = T_max;
    for (int iter = 0; iter < 60; iter++) {
        double mid = 0.5 * (low + high);
        double s_mid = total_entropy(salt, mid, B_target);
        if (s_mid < target_S) {
            low = mid;
        } else {
            high = mid;
        }
    }
    return 0.5 * (low + high);
}

int main(void) {
    /* Модельні параметри парамагнітної солі CMN (Церій-магнієвий нітрат) */
    ParamagneticSalt cmn = {
        .g_factor = 2.0,
        .debye_temp = 60.0,  
        .b_min = 0.001,      /* Внутрішнє дипольне поле 1 мТл */
        .b_max = 1.5         /* Зовнішнє магнітне поле 1.5 Тл */
    };

    double current_T = 4.2; /* Початкова температура рідкого гелію (К) */
    int num_cycles = 6;

    printf("=== Симуляція адіабатичного розмагнічування (C) ===\n");
    printf("Крок | Початкове T (К) | Поле B (Тл) | Ентропія S (Дж/моль*К) | Кінцеве T (К)\n");
    printf("-------------------------------------------------------------------------\n");

    for (int step = 1; step <= num_cycles; step++) {
        /* 1. Ізотермічне магнітування при current_T від b_min до b_max */
        double S_initial = total_entropy(&cmn, current_T, cmn.b_min);
        double S_magnetized = total_entropy(&cmn, current_T, cmn.b_max);

        /* 2. Адіабатичне розмагнічування при S_magnetized від b_max до b_min */
        double T_final = find_adiabatic_temperature(&cmn, S_magnetized, cmn.b_min, 1e-7, current_T);

        printf(" %2d  | %14.6f | %11.3f | %22.6f | %13.6f\n", 
               step, current_T, cmn.b_max, S_magnetized, T_final);

        current_T = T_final;
    }

    printf("-------------------------------------------------------------------------\n");
    printf("Результат: За %d циклів температура впала до %.8f К.\n", num_cycles, current_T);
    return 0;
}
