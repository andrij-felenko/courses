#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Фізичні константи */
#define Q_ELEM 1.602e-19       /* Елементарний заряд, Кл */
#define KB 1.381e-23           /* Стала Больцмана, Дж/К */
#define T_ENV 300.0            /* Температура середовища, К */

/* Параметри структури CBRAM */
typedef struct {
    double cell_gap;           /* Товщина електроліту, м (наприклад, 10 нм) */
    double act_energy;         /* Енергія активації E_a, джоулі (0.8 еВ) */
    double hop_distance;       /* Довжина стрибка іона a, м (0.4 нм) */
    double nu_0;               /* Частота спроб, Гц (1e13) */
    double r_hrs;              /* Опір матриці в стан HRS, Ом (10 МОм) */
    double r_lrs;              /* Опір сформованого містка LRS, Ом (1 кОм) */
    double i_comp;             /* Комплайєнс струму I_CC, А (100 мкА) */
    double c_th;               /* Тепловий коефіцієнт нагріву, Вт/К */
} CbramParams;

/* Стан осередку */
typedef struct {
    double fil_height;         /* Висота містка h, м */
    double temp;               /* Поточна температура звуження, К */
    bool is_connected;         /* Прапорець замикання містка */
} CbramState;

/* Ініціалізація параметрів за замовчуванням */
static CbramParams default_params(void) {
    CbramParams p;
    p.cell_gap = 10.0e-9;
    p.act_energy = 0.8 * Q_ELEM;
    p.hop_distance = 0.4e-9;
    p.nu_0 = 1.0e13;
    p.r_hrs = 1.0e7;
    p.r_lrs = 1000.0;
    p.i_comp = 100.0e-6;
    p.c_th = 5.0e-5;
    return p;
}

/* Обчислення поточного опору елемента */
static double compute_resistance(const CbramParams *p, double h) {
    if (h >= p->cell_gap * 0.99) {
        return p->r_lrs;
    }
    /* Пропорційне змішування опору зазору та містка */
    double fraction = h / p->cell_gap;
    double r_curr = p->r_hrs * (1.0 - fraction) + p->r_lrs * fraction;
    return (r_curr < p->r_lrs) ? p->r_lrs : r_curr;
}

/* Один крок симуляції часом dt */
static void step_simulation(const CbramParams *p, CbramState *st, double v_app, double dt, double *out_i) {
    double r_cell = compute_resistance(p, st->fil_height);
    double i_cell = v_app / r_cell;

    /* Обмеження комплайєнсом при SET */
    if (v_app > 0 && fabs(i_cell) > p->i_comp) {
        i_cell = (i_cell > 0) ? p->i_comp : -p->i_comp;
    }

    /* Джоулів нагрів */
    double p_joule = i_cell * i_cell * r_cell;
    st->temp = T_ENV + p_joule / p->c_th;

    /* Польовий дрейф іонів */
    double gap_rem = p->cell_gap - st->fil_height + 0.1e-9;
    double e_field = v_app / gap_rem;

    if (v_app > 0 && !st->is_connected) {
        /* Режим SET: ріст містка */
        double arg = (Q_ELEM * e_field * p->hop_distance) / (2.0 * KB * st->temp);
        if (arg > 30.0) arg = 30.0; /* Захист від переповнення */
        double v_drift = p->nu_0 * p->hop_distance * exp(-p->act_energy / (KB * st->temp)) * sinh(arg);

        st->fil_height += v_drift * dt;
        if (st->fil_height >= p->cell_gap * 0.99) {
            st->fil_height = p->cell_gap;
            st->is_connected = true;
        }
    } else if (v_app < 0 && st->is_connected) {
        /* Режим RESET: термічне та електрохімічне розчинення */
        double v_dissolve = p->nu_0 * p->hop_distance * exp(-p->act_energy / (KB * st->temp)) * 2.0;
        st->fil_height -= v_dissolve * dt;
        if (st->fil_height < p->cell_gap * 0.95) {
            st->is_connected = false;
        }
        if (st->fil_height < 0) {
            st->fil_height = 0;
        }
    }

    *out_i = i_cell;
}

int main(void) {
    CbramParams params = default_params();
    CbramState state = { 0.0, T_ENV, false };

    int num_steps = 200;
    double dt = 1.0e-5; /* 10 мкс */
    
    printf("--- CBRAM Simulation Output (C) ---\n");
    printf("Step\tVoltage(V)\tCurrent(uA)\tHeight(nm)\tState\n");

    /* Цикл напруги: 0V -> 1.5V (SET) -> 0V -> -1.0V (RESET) -> 0V */
    for (int i = 0; i <= num_steps; i++) {
        double t = (double)i / num_steps;
        double v_app = 0.0;

        if (t <= 0.25) {
            v_app = (t / 0.25) * 1.5;         /* Наростання SET */
        } else if (t <= 0.50) {
            v_app = 1.5 - ((t - 0.25) / 0.25) * 1.5; /* Спад SET */
        } else if (t <= 0.75) {
            v_app = -((t - 0.50) / 0.25) * 1.0; /* Наростання RESET */
        } else {
            v_app = -1.0 + ((t - 0.75) / 0.25) * 1.0; /* Повернення в 0В */
        }

        double i_out = 0.0;
        step_simulation(&params, &state, v_app, dt, &i_out);

        if (i % 20 == 0) {
            printf("%d\t%.3f\t\t%.2f\t\t%.2f\t\t%s\n",
                   i, v_app, i_out * 1e6, state.fil_height * 1e9,
                   state.is_connected ? "LRS" : "HRS");
        }
    }

    return 0;
}
