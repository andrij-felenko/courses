#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Параметри джерела живлення та профілю навантаження */
typedef struct {
    double v_bat_ocv;      /* Напруга холостого ходу батареї, В */
    double r_src;          /* Внутрішній опір джерела живлення, Ом */
    double i_peak;         /* Піковий струм імпульсу передачі, А */
    double t_pulse;        /* Тривалість імпульсу навантаження, с */
    double t_rise;         /* Тривалість наростання фронту струму, с */
    double v_bor_limit;    /* Поріг спрацьовування Brownout Reset, В */
    double v_safety_margin;/* Запас надійності за напругою, В */
} PdnScenario;

/* Параметри буферного конденсатора */
typedef struct {
    double c_nominal;      /* Номінальна ємність, Фарад */
    double r_esr;          /* Еквівалентний послідовний опір (ESR), Ом */
    double dc_bias_factor; /* Коефіцієнт втрати ємності під напругою (0.0..1.0) */
} BufferCapacitor;

/* Результати моделювання перехідного процесу */
typedef struct {
    double v_min;          /* Найглибша точка просідання напруги, В */
    double t_v_min;        /* Час досягнення мінімальної напруги, с */
    bool   is_bor_triggered; /* Чи відбулося аварійне скидання ядра */
} SimResult;

/* Обчислення ефективної ємності під постійною напругою (DC Bias derating) */
static double calc_effective_capacitance(const BufferCapacitor *cap, double v_now) {
    /* Спрощена лінійна модель деградації: при V > 0 ємність падає пропорційно напрузі */
    double derating = 1.0 - (cap->dc_bias_factor * (v_now / 3.3));
    if (derating < 0.20) derating = 0.20; /* насичення на рівні 20% номіналу */
    return cap->c_nominal * derating;
}

/* Генерація профілю струму навантаження з лінійним фронтом наростання */
static double get_load_current(const PdnScenario *sc, double t) {
    if (t < 0.0 || t > sc->t_pulse) {
        return 0.000005; /* Струм сну: 5 мкА */
    }
    if (t < sc->t_rise && sc->t_rise > 0.0) {
        return 0.000005 + (sc->i_peak - 0.000005) * (t / sc->t_rise);
    }
    return sc->i_peak;
}

/* Симуляція перехідного процесу розряду PDN у часовій області */
SimResult simulate_pdn_droop(const PdnScenario *sc, const BufferCapacitor *cap) {
    SimResult res = { sc->v_bat_ocv, 0.0, false };
    const double dt = 0.000001; /* Крок інтегрування: 1 мкс */
    const double t_end = sc->t_pulse * 1.5;

    double v_c = sc->v_bat_ocv; /* Початкова напруга на пластинах конденсатора */
    double v_bus = sc->v_bat_ocv;

    for (double t = 0.0; t <= t_end; t += dt) {
        double i_load = get_load_current(sc, t);

        /* Струм від джерела та конденсатора на поточному кроці */
        /* V_bus = V_c - I_cap * R_esr = V_bat - I_src * R_src */
        /* I_load = I_cap + I_src  =>  I_src = (V_bat - V_c + I_load * R_esr) / (R_src + R_esr) */
        double i_src = (sc->v_bat_ocv - v_c + i_load * cap->r_esr) / (sc->r_src + cap->r_esr);
        if (i_src < 0.0) i_src = 0.0; /* Джерело не приймає зворотний струм */

        double i_cap = i_load - i_src;

        /* Оновлення напруги на шині та ємності */
        v_bus = v_c - (i_cap * cap->r_esr);
        double c_eff = calc_effective_capacitance(cap, v_c);
        v_c -= (i_cap / c_eff) * dt;

        if (v_bus < res.v_min) {
            res.v_min = v_bus;
            res.t_v_min = t;
        }

        if (v_bus < sc->v_bor_limit) {
            res.is_bor_triggered = true;
        }
    }

    return res;
}

/* Автоматичний підбір мінімальної необхідної ємності конденсатора */
double find_minimum_buffer_capacitance(const PdnScenario *sc, double r_esr, double dc_bias) {
    double c_low = 1e-6;      /* 1 мкФ */
    double c_high = 20000e-6; /* 20 000 мкФ */
    double target_min_v = sc->v_bor_limit + sc->v_safety_margin;

    BufferCapacitor test_cap = { c_high, r_esr, dc_bias };
    SimResult check_max = simulate_pdn_droop(sc, &test_cap);
    if (check_max.v_min < target_min_v) {
        return -1.0; /* Навіть 20 000 мкФ недостатньо через завеликий ESR! */
    }

    /* Двійковий пошук мінімального номіналу */
    for (int iter = 0; iter < 40; ++iter) {
        double c_mid = (c_low + c_high) * 0.5;
        test_cap.c_nominal = c_mid;
        SimResult r = simulate_pdn_droop(sc, &test_cap);

        if (r.v_min >= target_min_v && !r.is_bor_triggered) {
            c_high = c_mid; /* Успіх, пробуємо меншу ємність */
        } else {
            c_low = c_mid;  /* Просідання завелике, збільшуємо ємність */
        }
    }

    return c_high;
}

int main(void) {
    PdnScenario sc = {
        .v_bat_ocv = 3.00,       /* Батарея CR2032 3.0 В */
        .r_src = 30.0,           /* Внутрішній опір комірки: 30 Ом */
        .i_peak = 0.280,         /* Пік передавача Wi-Fi/BLE: 280 мА */
        .t_pulse = 0.020,        /* Тривалість пакета: 20 мс */
        .t_rise = 0.0001,        /* Фронт наростання: 100 мкс */
        .v_bor_limit = 2.20,     /* Поріг скидання BOR: 2.20 В */
        .v_safety_margin = 0.20  /* Запас надійності: 0.20 В (мін. 2.40 В) */
    };

    double r_esr = 0.040;        /* ESR танталового конденсатора: 40 мОм */
    double dc_bias = 0.15;       /* Тантал майже не втрачає ємність під DC Bias */

    double c_min = find_minimum_buffer_capacitance(&sc, r_esr, dc_bias);

    if (c_min > 0) {
        printf("Мінімальна необхідна ємність буфера: %.1f мкФ (%.3f мФ)\n",
               c_min * 1e6, c_min * 1e3);

        BufferCapacitor best_cap = { c_min, r_esr, dc_bias };
        SimResult sim = simulate_pdn_droop(&sc, &best_cap);
        printf("Найглибша точка напруги: %.3f В (досягнута на %.2f мс)\n",
               sim.v_min, sim.t_v_min * 1000.0);
        printf("Статус скидання Brownout: %s\n",
               sim.is_bor_triggered ? "СПРАЦЮВАЛО (Збій!)" : "БЕЗПЕЧНО (Норма)");
    } else {
        printf("Помилка: Неможливо компенсувати просідання з поточним ESR джерела/буфера!\n");
    }

    return 0;
}
