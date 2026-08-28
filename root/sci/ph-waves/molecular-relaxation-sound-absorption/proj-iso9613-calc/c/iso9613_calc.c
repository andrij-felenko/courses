/* iso9613_calc.c — Реалізація стандарту ISO 9613-1 мовою C */
#include <stdio.h>
#include <math.h>

typedef struct {
    double temp_c;      /* Температура повітря у °C (-20..+50) */
    double rh_percent;  /* Відносна вологість у % (0..100) */
    double pressure_kpa;/* Атмосферний тиск у кПа (наприклад, 101.325) */
} iso9613_env_t;

/* Обчислення коефіцієнта поглинання у дБ/км для заданої частоти f (Гц) */
double iso9613_attenuation_db_per_km(double f_hz, const iso9613_env_t *env) {
    if (f_hz <= 0.0 || env == NULL) {
        return 0.0;
    }

    double T_k = env->temp_c + 273.15;
    double T0 = 293.15;      /* 20 °C у Кельвінах */
    double T01 = 273.16;     /* Потрійна точка води */
    
    double pr = env->pressure_kpa / 101.325; /* Відносний тиск */
    double Tr = T_k / T0;                    /* Відносна температура */

    /* Тиск насиченої пари вологи (ISO 9613-1 рівняння B.1) */
    double exponent = -6.8346 * pow(T01 / T_k, 1.261) + 4.6151;
    double p_sat_pr = pow(10.0, exponent);

    /* Молярна концентрація водяної пари h (%) */
    double h = env->rh_percent * (p_sat_pr / pr);
    if (h < 1e-6) {
        h = 1e-6; /* Захист від нуля для сухого повітря */
    }

    /* Частота релаксації кисню f_r,O2 (Гц) */
    double fr_O2 = pr * (24.0 + 4.04e4 * h * (0.02 + h) / (0.391 + h));

    /* Частота релаксації азоту f_r,N2 (Гц) */
    double fr_N2 = pr * pow(Tr, -0.5) * 
                   (9.0 + 280.0 * h * exp(-4.170 * (pow(Tr, -1.0 / 3.0) - 1.0)));

    /* Класичний внесок та в'язкісна теплопровідність */
    double alpha_class = 1.84e-11 * (1.0 / pr) * sqrt(Tr);

    /* Коливальні амплітуди молекул кисню та азоту */
    double A_O2 = 0.01275 * exp(-2239.1 / T_k);
    double A_N2 = 0.10680 * exp(-3352.0 / T_k);

    /* Релаксаційні внески */
    double alpha_O2 = pow(Tr, -2.5) * (A_O2 * fr_O2 / (fr_O2 * fr_O2 + f_hz * f_hz));
    double alpha_N2 = pow(Tr, -2.5) * (A_N2 * fr_N2 / (fr_N2 * fr_N2 + f_hz * f_hz));

    /* Загальний коефіцієнт поглинання у дБ/км */
    double alpha_db_km = 8.686 * f_hz * f_hz * (alpha_class + alpha_O2 + alpha_N2);

    return alpha_db_km;
}

int main(void) {
    iso9613_env_t env = { .temp_c = 20.0, .rh_percent = 50.0, .pressure_kpa = 101.325 };
    double freqs[] = { 125.0, 500.0, 1000.0, 4000.0, 8000.0, 40000.0 };
    size_t count = sizeof(freqs) / sizeof(freqs[0]);

    printf("Частота (Гц) | Поглинання (дБ/км) | Поглинання (дБ/м)\n");
    printf("--------------------------------------------------\n");
    for (size_t i = 0; i < count; ++i) {
        double db_km = iso9613_attenuation_db_per_km(freqs[i], &env);
        printf("%11.1f | %17.3f | %16.5f\n", freqs[i], db_km, db_km / 1000.0);
    }
    return 0;
}
