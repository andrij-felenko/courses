#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double v_ocv;            /* Напруга холостого ходу пакета, В */
    double l_loop;           /* Паразитна індуктивність контуру, Гн */
    double r_cells;          /* Внутрішній опір комірок, Ом */
    double r_bus_base;       /* Базовий опір шин та дротів за 20 °C, Ом */
    double r_dson_base;      /* Опір каналу всіх паралельних MOSFET за 25 °C, Ом */
    double r_shunt;          /* Опір струмовимірювального шунта, Ом */
    double r_fault;          /* Опір перемички КЗ, Ом */
    double i2t_fuse_rating;  /* Номінальний I²t розплавлення запобіжника, А²·с */
    double i2t_pcb_rating;   /* Граничний I²t доріжки друкованої плати, А²·с */
    double scp_delay_sec;    /* Затримка апаратного компаратора BMS, с */
    double mosfet_toff_sec;  /* Час спаду струму затвора при вимкненні, с */
    double c_th_die;         /* Теплоємність кристала кремнію MOSFET, Дж/°C */
    double t_j_max;          /* Максимально допустима температура кристала, °C */
} PackSimConfig;

typedef struct {
    double time_sec;
    double current;
    double i2t_accumulated;
    double t_junction;
    double v_ds_peak;
    bool fuse_blown;
    bool pcb_damaged;
    bool mosfet_destroyed;
    bool bms_tripped;
} SimResult;

SimResult run_short_circuit_simulation(const PackSimConfig *cfg, double dt, double t_max) {
    SimResult res = {
        .time_sec = 0.0,
        .current = 0.0,
        .i2t_accumulated = 0.0,
        .t_junction = 25.0,
        .v_ds_peak = cfg->v_ocv,
        .fuse_blown = false,
        .pcb_damaged = false,
        .mosfet_destroyed = false,
        .bms_tripped = false
    };

    double current = 0.0;
    double t = 0.0;
    bool bms_opening = false;
    double bms_open_progress = 0.0;

    while (t < t_max) {
        /* Температурний дрейф опору міді/нікелю та каналу MOSFET */
        double r_dson = cfg->r_dson_base * (1.0 + 0.005 * (res.t_junction - 25.0));
        double r_bus = cfg->r_bus_base * (1.0 + 0.00393 * (res.t_junction - 25.0));
        double r_active_dson = r_dson;

        /* Моделювання переходу в режим відсічки затвора */
        if (bms_opening) {
            bms_open_progress += dt / cfg->mosfet_toff_sec;
            if (bms_open_progress >= 1.0) {
                bms_open_progress = 1.0;
            }
            /* Зростання опору каналу при закритті ключа */
            r_active_dson = r_dson / (1.0 - 0.999 * bms_open_progress);
        }

        double r_total = cfg->r_cells + r_bus + r_active_dson + cfg->r_shunt + cfg->r_fault;

        /* Диференціальне рівняння di/dt = (V_ocv - i * R_total) / L */
        double di_dt = (cfg->v_ocv - current * r_total) / cfg->l_loop;
        current += di_dt * dt;
        if (current < 0.0) {
            current = 0.0;
        }

        /* Накопичення інтегралу Джоуля */
        res.i2t_accumulated += (current * current) * dt;

        /* Тепловий баланс кристала MOSFET */
        double p_loss_die = (current * current) * r_active_dson;
        res.t_junction += (p_loss_die / cfg->c_th_die) * dt;

        /* Перевірка критеріїв руйнування */
        if (res.t_junction >= cfg->t_j_max && !res.mosfet_destroyed) {
            res.mosfet_destroyed = true;
        }

        if (res.i2t_accumulated >= cfg->i2t_pcb_rating && !res.pcb_damaged) {
            res.pcb_damaged = true;
        }

        if (res.i2t_accumulated >= cfg->i2t_fuse_rating && !res.fuse_blown) {
            res.fuse_blown = true;
            break;
        }

        /* Спрацьовування апаратного захисту BMS */
        if (t >= cfg->scp_delay_sec && !res.bms_tripped && !bms_opening) {
            bms_opening = true;
            res.bms_tripped = true;
        }

        /* Фіксація індуктивного сплеску напруги під час вимкнення */
        if (bms_opening && di_dt < 0.0) {
            double v_spike = cfg->v_ocv + cfg->l_loop * fabs(di_dt);
            if (v_spike > res.v_ds_peak) {
                res.v_ds_peak = v_spike;
            }
        }

        if (bms_opening && bms_open_progress >= 1.0 && current < 1.0) {
            break;
        }

        t += dt;
    }

    res.time_sec = t;
    res.current = current;
    return res;
}

int main(void) {
    PackSimConfig cfg = {
        .v_ocv = 67.2,                  /* 16S Li-ion (4.2 В на комірку) */
        .l_loop = 600e-9,               /* 600 нГн індуктивність */
        .r_cells = 0.030,               /* 30 мОм пакет */
        .r_bus_base = 0.010,            /* 10 мОм шини */
        .r_dson_base = 0.002,           /* 2 мОм ключі BMS */
        .r_shunt = 0.001,               /* 1 мОм шунт */
        .r_fault = 0.001,               /* 1 мОм коротке замикання */
        .i2t_fuse_rating = 1200.0,      /* 1200 А²·с DC запобіжник */
        .i2t_pcb_rating = 2200.0,       /* 2200 А²·с доріжки плати */
        .scp_delay_sec = 25e-6,         /* 25 мкс реакція BMS SCP */
        .mosfet_toff_sec = 5e-6,        /* 5 мкс час закриття затвора */
        .c_th_die = 0.35,               /* 0.35 Дж/°C теплоємність кристалів */
        .t_j_max = 175.0                /* 175 °C межа кремнію */
    };

    SimResult r = run_short_circuit_simulation(&cfg, 0.1e-6, 500e-6);

    printf("=== РЕЗУЛЬТАТИ СИМУЛЯЦІЇ КЗ БАТАРЕЇ 16S (67.2 В) ===\n");
    printf("Час процесу:          %.2f мкс\n", r.time_sec * 1e6);
    printf("Накопичений I²t:      %.1f А²·с\n", r.i2t_accumulated);
    printf("Температура MOSFET:   %.1f °C\n", r.t_junction);
    printf("Піковий викид V_ds:   %.1f В\n", r.v_ds_peak);
    printf("BMS відсічка:         %s\n", r.bms_tripped ? "СПРАЦЮВАЛА" : "НІ");
    printf("Стан MOSFET:          %s\n", r.mosfet_destroyed ? "ПРОБИТО (ТЕПЛОВИЙ ВИБУХ)" : "ВЦІЛІЛИ");
    printf("Стан запобіжника:     %s\n", r.fuse_blown ? "ПЕРЕГОРІВ" : "ЦІЛИЙ");
    printf("Стан плати (PCB):     %s\n", r.pcb_damaged ? "ЗГОРІЛА" : "ВЦІЛІЛА");

    return 0;
}
