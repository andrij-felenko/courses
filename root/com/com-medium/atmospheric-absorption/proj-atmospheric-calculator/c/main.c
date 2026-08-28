#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Тип поляризації радіохвилі */
typedef enum {
    POLARIZATION_HORIZONTAL = 0,
    POLARIZATION_VERTICAL   = 1,
    POLARIZATION_CIRCULAR   = 2
} polarization_type_t;

/* Структура параметрів атмосфери та радіолінії */
typedef struct {
    double frequency_ghz;      /* Частота сигналу (1 - 350 ГГц) */
    double distance_km;        /* Фізична довжина траси (км) */
    double elevation_deg;      /* Кут місця / підвищення антени (градуси) */
    double rain_rate_mm_h;     /* Інтенсивність дощу R (мм/год) */
    double humidity_g_m3;      /* Абсолютна вологість повітря (г/м³) */
    polarization_type_t pol;   /* Поляризація сигналу */
} link_params_t;

/* Результати розрахунку згасання */
typedef struct {
    double gamma_oxygen_db_km; /* Питоме згасання в кисні (дБ/км) */
    double gamma_water_db_km;  /* Питоме згасання у водяній парі (дБ/км) */
    double gamma_gas_db_km;    /* Сумарне питоме газове згасання (дБ/км) */
    double gamma_rain_db_km;   /* Питоме дощове згасання (дБ/км) */
    double path_gas_atten_db;  /* Повне газове згасання траси (дБ) */
    double path_rain_atten_db; /* Повне дощове згасання траси (дБ) */
    double total_attenuation_db; /* Загальне згасання в атмосфері (дБ) */
} attenuation_result_t;

/* Обчислення питомого газового згасання (ITU-R P.676) */
void calculate_gas_attenuation(double f_ghz, double rho_g_m3, 
                                double *gamma_o, double *gamma_w) {
    double f2 = f_ghz * f_ghz;
    
    /* Спрощена апроксимація поглинання киснем O2 */
    double term_o1 = 7.27 / (f2 + 0.351);
    double term_o2 = 7.5 / ((f_ghz - 57.0) * (f_ghz - 57.0) + 2.44);
    *gamma_o = (term_o1 + term_o2) * f2 * 1e-3;

    /* Спрощена апроксимація поглинання водяною парою H2O (лінія 22.235 ГГц та 183.31 ГГц) */
    double term_w1 = 0.05 + 0.002 * rho_g_m3;
    double term_w2 = 3.6 / ((f_ghz - 22.235) * (f_ghz - 22.235) + 8.5);
    double term_w3 = 10.6 / ((f_ghz - 183.31) * (f_ghz - 183.31) + 9.0);
    *gamma_w = (term_w1 + term_w2 + term_w3) * f2 * rho_g_m3 * 1e-4;
}

/* Обчислення коефіцієнтів k та alpha для дощового згасання (ITU-R P.838) */
void get_rain_coefficients(double f_ghz, polarization_type_t pol, double elev_deg,
                           double *k_out, double *alpha_out) {
    /* Табличні коефіцієнти регресії ITU-R P.838 для інтерполяції */
    double k_h, k_v, a_h, a_v;

    if (f_ghz <= 10.0) {
        k_h = 0.01217; k_v = 0.01129;
        a_h = 1.2571;  a_v = 1.2156;
    } else if (f_ghz <= 20.0) {
        k_h = 0.0751;  k_v = 0.0691;
        a_h = 1.0993;  a_v = 1.0654;
    } else if (f_ghz <= 30.0) {
        k_h = 0.2403;  k_v = 0.2291;
        a_h = 0.9485;  a_v = 0.9129;
    } else if (f_ghz <= 60.0) {
        k_h = 0.8606;  k_v = 0.8474;
        a_h = 0.7656;  a_v = 0.7589;
    } else {
        k_h = 1.3200;  k_v = 1.3100;
        a_h = 0.6900;  a_v = 0.6850;
    }

    double theta_rad = elev_deg * M_PI / 180.0;
    double cos2_theta = cos(theta_rad) * cos(theta_rad);

    double tau_deg = 0.0;
    if (pol == POLARIZATION_VERTICAL) tau_deg = 90.0;
    else if (pol == POLARIZATION_CIRCULAR) tau_deg = 45.0;
    
    double tau_rad = tau_deg * M_PI / 180.0;
    double cos_2tau = cos(2.0 * tau_rad);

    *k_out = (k_h + k_v + (k_h - k_v) * cos2_theta * cos_2tau) / 2.0;
    *alpha_out = (k_h * a_h + k_v * a_v + (k_h * a_h - k_v * a_v) * cos2_theta * cos_2tau) / (2.0 * (*k_out));
}

/* Обчислення сумарного згасання радіолінії */
attenuation_result_t calculate_link_attenuation(const link_params_t *params) {
    attenuation_result_t res;
    
    /* 1. Газове згасання */
    calculate_gas_attenuation(params->frequency_ghz, params->humidity_g_m3, 
                              &res.gamma_oxygen_db_km, &res.gamma_water_db_km);
    res.gamma_gas_db_km = res.gamma_oxygen_db_km + res.gamma_water_db_km;

    /* 2. Дощове згасання */
    double k, alpha;
    get_rain_coefficients(params->frequency_ghz, params->pol, params->elevation_deg, &k, &alpha);
    res.gamma_rain_db_km = k * pow(params->rain_rate_mm_h, alpha);

    /* 3. Трасовий розрахунок з урахуванням ефекту скорочення дощового стовпа */
    double r_factor = 1.0;
    if (params->distance_km > 1.0) {
        /* Емпіричний коефіцієнт скорочення довжини траси для дощового осередку */
        r_factor = 1.0 / (1.0 + 0.045 * params->distance_km);
    }
    
    double eff_rain_distance = params->distance_km * r_factor;

    res.path_gas_atten_db = res.gamma_gas_db_km * params->distance_km;
    res.path_rain_atten_db = res.gamma_rain_db_km * eff_rain_distance;
    res.total_attenuation_db = res.path_gas_atten_db + res.path_rain_atten_db;

    return res;
}

int main(void) {
    link_params_t link;
    link.frequency_ghz = 28.0;       /* Ka-діапазон */
    link.distance_km = 5.0;          /* 5 км радіорелейний міст */
    link.elevation_deg = 0.0;        /* Горизонтальна траса */
    link.rain_rate_mm_h = 50.0;      /* Злива 50 мм/год */
    link.humidity_g_m3 = 7.5;        /* Стандартна вологість */
    link.pol = POLARIZATION_HORIZONTAL;

    attenuation_result_t res = calculate_link_attenuation(&link);

    printf("=== Розрахунок згасання радіолінії (Мова C) ===\n");
    printf("Частота: %.1f ГГц, Відстань: %.1f км, Дощ: %.1f мм/год (Горизонтальна поляризація)\n", 
           link.frequency_ghz, link.distance_km, link.rain_rate_mm_h);
    printf("Питоме згасання O2:    %.4f дБ/км\n", res.gamma_oxygen_db_km);
    printf("Питоме згасання H2O:   %.4f дБ/км\n", res.gamma_water_db_km);
    printf("Сумарне газове згасання: %.4f дБ/км (Траса: %.2f дБ)\n", 
           res.gamma_gas_db_km, res.path_gas_atten_db);
    printf("Питоме дощове згасання: %.4f дБ/км (Траса: %.2f дБ)\n", 
           res.gamma_rain_db_km, res.path_rain_atten_db);
    printf("Загальні атмосферні втрати: %.2f дБ\n", res.total_attenuation_db);

    return 0;
}
