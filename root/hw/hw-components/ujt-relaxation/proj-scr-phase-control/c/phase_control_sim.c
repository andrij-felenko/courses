/*
 * phase_control_sim.c - Моделювання фазоімпульсного UJT-регулятора напруги
 *
 * Обчислює часові затримки, кути відмикання симістора, діючу напругу (RMS)
 * та потужність на активному навантаженні для мережі 230 В / 50 Гц.
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double v_grid_rms;     /* Діюча напруга мережі, В (230.0) */
    double f_grid;         /* Частота мережі, Гц (50.0) */
    double v_zener;        /* Напруга стабілітрона, В (20.0) */
    double eta;            /* Внутрішній коефіцієнт поділу UJT (0.65) */
    double v_diode;        /* Пряме падіння на діоді емітера, В (0.65) */
    double v_valley;       /* Напруга западини UJT, В (1.5) */
    double r_min_ohms;     /* Постійний обмежувальний резистор, Ом (5100.0) */
    double r_pot_ohms;     /* Повний опір змінного резистора, Ом (100000.0) */
    double cap_farads;      /* Ємність часозадавального конденсатора, Ф (100e-9) */
    double r_load_ohms;    /* Опір активного навантаження, Ом (50.0) */
} ujt_circuit_config_t;

typedef struct {
    double pot_ratio;       /* Положення потенціометра (0.0 ... 1.0) */
    double r_total;         /* Повний опір заряду, Ом */
    double t_fire_ms;       /* Час затримки відмикання, мс */
    double alpha_deg;       /* Фазовий кут відмикання, градуси */
    double v_load_rms;      /* Діюча напруга на навантаженні, В */
    double p_load_watts;    /* Середня потужність навантаження, Вт */
    double p_percent;       /* Відсоток від максимальної потужності, % */
    bool is_triggered;      /* Чи досягає конденсатор напруги порогу */
} phase_calc_result_t;

/* Обчислення порогу напруги піку V_P */
static inline double calc_v_peak(const ujt_circuit_config_t *cfg) {
    return cfg->eta * cfg->v_zener + cfg->v_diode;
}

/* Обчислення параметрів для заданого положення потенціометра */
bool calculate_firing_point(const ujt_circuit_config_t *cfg, double pot_ratio, phase_calc_result_t *res) {
    if (!cfg || !res || pot_ratio < 0.0 || pot_ratio > 1.0) {
        return false;
    }

    double t_half_ms = 1000.0 / (2.0 * cfg->f_grid); /* 10.0 мс для 50 Гц */
    double v_peak = calc_v_peak(cfg);

    res->pot_ratio = pot_ratio;
    res->r_total = cfg->r_min_ohms + pot_ratio * cfg->r_pot_ohms;

    /* Перевірка чи напруга стабілітрона перевищує поріг піку */
    if (v_peak >= cfg->v_zener) {
        res->is_triggered = false;
        res->t_fire_ms = t_half_ms;
        res->alpha_deg = 180.0;
        res->v_load_rms = 0.0;
        res->p_load_watts = 0.0;
        res->p_percent = 0.0;
        return true;
    }

    /* Точний час заряду від V_V до V_P */
    double v_num = cfg->v_zener - cfg->v_valley;
    double v_den = cfg->v_zener - v_peak;
    double t_charge_sec = res->r_total * cfg->cap_farads * log(v_num / v_den);
    double t_charge_ms = t_charge_sec * 1000.0;

    if (t_charge_ms >= t_half_ms) {
        /* Конденсатор не встигає зарядитися за напівперіод */
        res->is_triggered = false;
        res->t_fire_ms = t_half_ms;
        res->alpha_deg = 180.0;
        res->v_load_rms = 0.0;
        res->p_load_watts = 0.0;
        res->p_percent = 0.0;
    } else {
        res->is_triggered = true;
        res->t_fire_ms = t_charge_ms;
        res->alpha_deg = (t_charge_ms / t_half_ms) * 180.0;

        /* Кут у радіанах для інтегрування синусоїди */
        double alpha_rad = res->alpha_deg * (M_PI / 180.0);

        /* V_load(RMS) = V_grid * sqrt( (1/pi) * [ (pi - alpha) + (sin(2*alpha)/2) ] ) */
        double integ = (M_PI - alpha_rad) + (sin(2.0 * alpha_rad) / 2.0);
        res->v_load_rms = cfg->v_grid_rms * sqrt(integ / M_PI);

        res->p_load_watts = (res->v_load_rms * res->v_load_rms) / cfg->r_load_ohms;
        double p_max = (cfg->v_grid_rms * cfg->v_grid_rms) / cfg->r_load_ohms;
        res->p_percent = (res->p_load_watts / p_max) * 100.0;
    }

    return true;
}

int main(void) {
    ujt_circuit_config_t config = {
        .v_grid_rms = 230.0,
        .f_grid = 50.0,
        .v_zener = 20.0,
        .eta = 0.65,
        .v_diode = 0.65,
        .v_valley = 1.50,
        .r_min_ohms = 5100.0,
        .r_pot_ohms = 100000.0,
        .cap_farads = 100.0e-9,
        .r_load_ohms = 50.0
    };

    printf("=== СИМУЛЯЦІЯ ФАЗОІМПУЛЬСНОГО КЕРУВАННЯ СИМІСТОРОМ НА UJT ===\n");
    printf("Мережа: %.1f В / %.0f Гц | Стабілітрон: %.1f В | UJT: eta=%.2f, C=%.0f нФ\n\n",
           config.v_grid_rms, config.f_grid, config.v_zener, config.eta, config.cap_farads * 1e9);
    printf(" Пот.%% |  Опір R, кОм | Час t, мс | Кут alpha | V_RMS, В | Потужність, Вт |  Потужн. %%\n");
    printf("-------+--------------+-----------+-----------+----------+----------------+------------\n");

    for (int step = 0; step <= 10; ++step) {
        double pot_ratio = (double)step / 10.0;
        phase_calc_result_t res;
        if (calculate_firing_point(&config, pot_ratio, &res)) {
            printf(" %4.0f%% | %12.2f | %9.3f | %8.1f* | %8.2f | %14.2f | %10.1f%%\n",
                   pot_ratio * 100.0,
                   res.r_total / 1000.0,
                   res.t_fire_ms,
                   res.alpha_deg,
                   res.v_load_rms,
                   res.p_load_watts,
                   res.p_percent);
        }
    }

    return 0;
}
