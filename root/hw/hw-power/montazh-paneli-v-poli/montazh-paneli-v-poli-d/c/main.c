#include <math.h>

typedef struct {
    double p_stc_w;         /* Номінальна потужність панелі за STC (Вт) */
    double gamma_pmp;       /* Температурний коефіцієнт потужності (%/°C, наприклад -0.38) */
    double noct_c;          /* Нормальна робоча температура комірки (°C, типово 45.0) */
    double soiling_factor;  /* Частка втрат від забруднення (наприклад 0.05 = 5%) */
} SolarFieldPanel;

/* Розрахунок реальної потужності сонячної панелі у польових умовах */
double calculate_field_power(const SolarFieldPanel *panel, double g_tilt_w_m2, double t_ambient_c) {
    if (g_tilt_w_m2 <= 0.0) {
        return 0.0;
    }

    /* 1. Розрахунок робочої температури кремнієвого фотоелемента */
    double t_cell = t_ambient_c + g_tilt_w_m2 * ((panel->noct_c - 20.0) / 800.0);

    /* 2. Температурна деградація потужності */
    double temp_correction = 1.0 + (panel->gamma_pmp / 100.0) * (t_cell - 25.0);
    if (temp_correction < 0.1) {
        temp_correction = 0.1; /* Захист від від'ємних значень при екстремальному нагріві */
    }

    /* 3. Корекція на оптичні втрати від пилу та бруду */
    double soiling_correction = 1.0 - panel->soiling_factor;
    if (soiling_correction < 0.0) {
        soiling_correction = 0.0;
    }

    /* 4. Фінальна електрична потужність */
    double p_out = panel->p_stc_w * (g_tilt_w_m2 / 1000.0) * temp_correction * soiling_correction;
    return p_out > 0.0 ? p_out : 0.0;
}
