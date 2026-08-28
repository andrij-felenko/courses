/* simulation_cascade.c — чисельне моделювання каскаду захисту Spark Gap + TVS */
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double v_spark;        /* напруга запалювання іскри, В */
    double v_arc;          /* напруга горіння дуги, В */
    double r_arc;          /* опір дугового каналу, Ом */
    double t_delay;        /* затримка формування дуги, с */
    bool is_ignited;       /* стан провідності */
    double ignition_timer; /* накопичений час перебування під надкритичною напругою */
} SparkGap;

typedef struct {
    double v_br;           /* напруга відкривання діода, В */
    double r_dyn;          /* динамічний опір, Ом */
    double c_tvs;          /* паразитна ємність діода, Ф */
} TvsDiode;

typedef struct {
    double r_s;            /* послідовний опір розв'язки, Ом */
    double l_trace;        /* індуктивність друкованої доріжки, Гн */
} Decoupling;

/* Генерація випробувального ESD струму IEC 61000-4-2 (8 кВ) */
static double esd_current_source(double t_sec) {
    if (t_sec < 0.0 || t_sec > 200e-9) return 0.0;
    double t_ns = t_sec * 1e9;
    /* Двохкомпонентний аналітичний імпульс ESD */
    double i1 = 30.0 * exp(-t_ns / 30.0) / (1.0 + exp(-(t_ns - 1.0) / 0.5));
    double i2 = 15.0 * exp(-t_ns / 60.0) / (1.0 + exp(-(t_ns - 1.0) / 1.5));
    return i1 + i2;
}

int main(void) {
    SparkGap gap = {
        .v_spark = 1200.0,
        .v_arc = 18.0,
        .r_arc = 0.4,
        .t_delay = 4.0e-9,
        .is_ignited = false,
        .ignition_timer = 0.0
    };

    TvsDiode tvs = {
        .v_br = 6.8,
        .r_dyn = 0.5,
        .c_tvs = 15.0e-12
    };

    Decoupling dec = {
        .r_s = 2.2,
        .l_trace = 25.0e-9 /* 25 нГн (~25 мм доріжки на платі) */
    };

    const double dt = 1.0e-11;     /* крок інтегрування 10 пс */
    const double t_max = 80.0e-9;  /* 80 нс тривалість аналізу */

    double i_trace = 0.0;
    double v_tvs = 0.0;
    double energy_gap = 0.0;
    double energy_tvs = 0.0;
    double energy_res = 0.0;
    double max_v_tvs = 0.0;

    printf("Час [нс] | Струм ESD [A] | Напруга Gap [В] | Струм Gap [A] | Напруга TVS [В] | Стан іскровика\n");
    printf("--------------------------------------------------------------------------------------------\n");

    for (double t = 0.0; t <= t_max; t += dt) {
        double i_esd = esd_current_source(t);

        /* Стан іскрового розрядника */
        double v_gap = 0.0;
        double i_gap = 0.0;

        if (gap.is_ignited) {
            /* Дуга горить: напруга фіксована на рівні дуги + омічне падіння */
            i_gap = i_esd - i_trace;
            if (i_gap < 0.0) i_gap = 0.0;
            v_gap = gap.v_arc + i_gap * gap.r_arc;
        } else {
            /* До пробою: струм іскровика нульовий */
            i_gap = 0.0;
            /* Напруга на вході визначається реакцією координуючого кола */
            double di_dt = (i_esd - i_trace) / dt;
            v_gap = v_tvs + dec.r_s * i_trace + dec.l_trace * di_dt;

            if (v_gap >= gap.v_spark) {
                gap.ignition_timer += dt;
                if (gap.ignition_timer >= gap.t_delay) {
                    gap.is_ignited = true;
                }
            } else {
                gap.ignition_timer = 0.0;
            }
        }

        /* Динаміка координуючого контуру та TVS */
        double di_trace_dt = (v_gap - v_tvs - dec.r_s * i_trace) / dec.l_trace;
        i_trace += di_trace_dt * dt;
        if (i_trace < 0.0) i_trace = 0.0;

        /* Розрахунок TVS-діода */
        double i_tvs = 0.0;
        if (v_tvs > tvs.v_br) {
            i_tvs = (v_tvs - tvs.v_br) / tvs.r_dyn;
        }
        double dv_tvs_dt = (i_trace - i_tvs) / tvs.c_tvs;
        v_tvs += dv_tvs_dt * dt;

        if (v_tvs > max_v_tvs) max_v_tvs = v_tvs;

        /* Інтегрування розсіяної енергії */
        energy_gap += (v_gap * i_gap) * dt;
        energy_tvs += (v_tvs * i_tvs) * dt;
        energy_res += (i_trace * i_trace * dec.r_s) * dt;

        /* Друк ключових точок */
        int step = (int)(t / dt);
        if (step % 200 == 0) {
            printf("%7.2f  | %13.2f | %15.1f | %13.2f | %15.2f | %s\n",
                   t * 1e9, i_esd, v_gap, i_gap, v_tvs,
                   gap.is_ignited ? "ДУГА (ON)" : "ІЗОЛЯЦІЯ");
        }
    }

    printf("--------------------------------------------------------------------------------------------\n");
    printf("Підсумки розподілу енергії:\n");
    printf("  Енергія в іскровому розряднику: %6.2f мДж (%5.1f%%)\n",
           energy_gap * 1000.0, (energy_gap / (energy_gap + energy_tvs + energy_res)) * 100.0);
    printf("  Енергія в розв'язувальному резисторі: %6.2f мДж\n", energy_res * 1000.0);
    printf("  Енергія в TVS-діоді:            %6.2f мДж (%5.1f%%)\n",
           energy_tvs * 1000.0, (energy_tvs / (energy_gap + energy_tvs + energy_res)) * 100.0);
    printf("  Пікова напруга на мікросхемі:   %6.2f В\n", max_v_tvs);

    return 0;
}
