#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура 8 broadcast-параметрів Клобучара з супутникового кадру */
typedef struct {
    double alpha[4]; /* α0..α3 у секундах, с/напівколо, с/напівколо², с/напівколо³ */
    double beta[4];  /* β0..β3 у секундах, с/напівколо, с/напівколо², с/напівколо³ */
} klobuchar_params_t;

/* Вхідні геометричні дані спостереження */
typedef struct {
    double lat_deg;   /* Широта приймача (градуси, -90..+90) */
    double lon_deg;   /* Довгота приймача (градуси, -180..+180) */
    double elev_deg;  /* Елевація супутника (градуси, 0..90) */
    double azim_deg;  /* Азимут супутника (градуси, 0..360) */
    double gps_time_s;/* Секунди тижня GPS (0..604800) */
    double freq_hz;   /* Частота сигналу (наприклад, 1575.42e6 для L1) */
} gnss_obs_t;

/**
 * Обчислює іоносферну затримку у метрах за моделлю Клобучара.
 */
double klobuchar_compute_delay_m(const klobuchar_params_t* p, const gnss_obs_t* obs) {
    const double speed_of_light = 299792458.0; /* м/с */
    const double f_l1 = 1575.42e6;              /* Базова частота GPS L1 */

    /* 1. Переведення в кутові одиниці напівкіл (semi-circles) */
    double lat_semi = obs->lat_deg / 180.0;
    double lon_semi = obs->lon_deg / 180.0;
    double elev_semi = obs->elev_deg / 180.0;
    double azim_rad = obs->azim_deg * (M_PI / 180.0);

    /* 2. Центральний кут Землі psi */
    double psi = 0.0137 / (elev_semi + 0.11) - 0.022;

    /* 3. Широта пробійної точки іоносфери (IPP) */
    double lat_i = lat_semi + psi * cos(azim_rad);
    if (lat_i > 0.416)  lat_i = 0.416;
    if (lat_i < -0.416) lat_i = -0.416;

    /* 4. Довгота пробійної точки іоносфери (IPP) */
    double lon_i = lon_semi + (psi * sin(azim_rad)) / cos(lat_i * M_PI);

    /* 5. Геомагнітна широта IPP */
    double lat_m = lat_i + 0.064 * cos((lon_i - 1.617) * M_PI);

    /* 6. Місцевий сонячний час у точці IPP (секунди доби) */
    double t_local = 43200.0 * lon_i + obs->gps_time_s;
    t_local = fmod(t_local, 86400.0);
    if (t_local < 0.0) t_local += 86400.0;

    /* 7. Похилий картографічний фактор F(e) */
    double f_slanted = 1.0 + 16.0 * pow(0.53 - elev_semi, 3);

    /* 8. Обчислення амплітуди A та періоду P за поліномами геомагнітної широти */
    double amp = p->alpha[0] + p->alpha[1] * lat_m + p->alpha[2] * pow(lat_m, 2) + p->alpha[3] * pow(lat_m, 3);
    if (amp < 0.0) amp = 0.0;

    double period = p->beta[0] + p->beta[1] * lat_m + p->beta[2] * pow(lat_m, 2) + p->beta[3] * pow(lat_m, 3);
    if (period < 72000.0) period = 72000.0;

    /* 9. Фаза косинусоїди та затримка у секундах */
    double x_phase = 2.0 * M_PI * (t_local - 50400.0) / period;
    double delay_seconds = 0.0;

    if (fabs(x_phase) < 1.57) {
        /* Денна косинусна фаза (апроксимація рядом Тейлора 4-го порядку) */
        double cos_approx = 1.0 - (x_phase * x_phase) / 2.0 + (x_phase * x_phase * x_phase * x_phase) / 24.0;
        delay_seconds = f_slanted * (5.0e-9 + amp * cos_approx);
    } else {
        /* Нічний постійний поріг 5 наносекунд */
        delay_seconds = f_slanted * 5.0e-9;
    }

    /* 10. Масштабування за частотою (1/f²) та переведення в метри */
    double freq_scale = (f_l1 * f_l1) / (obs->freq_hz * obs->freq_hz);
    double delay_meters = delay_seconds * speed_of_light * freq_scale;

    return delay_meters;
}

int main(void) {
    /* Типові коефіцієнти Клобучара з навігаційного кадру GPS */
    klobuchar_params_t params = {
        .alpha = {0.1490e-07, 0.1490e-07, -0.5960e-07, -0.1192e-06},
        .beta  = {0.9830e+05, 0.8192e+05, -0.1966e+06, -0.4588e+06}
    };

    gnss_obs_t obs = {
        .lat_deg    = 50.45,       /* Київ, Україна */
        .lon_deg    = 30.52,
        .elev_deg   = 35.0,        /* Елевація 35 градусів */
        .azim_deg   = 140.0,
        .gps_time_s = 50400.0,     /* 14:00 місцевого сонячного часу (пік затримки) */
        .freq_hz    = 1575.42e6    /* Частота L1 */
    };

    double delay_m = klobuchar_compute_delay_m(&params, &obs);
    printf("Київ (L1, elev=35 deg, 14:00): Іоносферна затримка = %.3f м\n", delay_m);

    /* Зміна частоти на L2 (1227.60 МГц) */
    obs.freq_hz = 1227.60e6;
    double delay_l2 = klobuchar_compute_delay_m(&params, &obs);
    printf("Київ (L2, elev=35 deg, 14:00): Іоносферна затримка = %.3f м\n", delay_l2);

    return 0;
}
