#include <stdio.h>
#include <stdbool.h>
#include <math.h>

// Параметри силової схеми та комутатора
typedef struct {
    double vs;          // Напруга джерела живлення, В
    double i_load;      // Струм навантаження, А
    double cc;          // Ємність комутуючого конденсатора, Ф
    double lc;          // Індуктивність котушки, Гн
    double r_loss;      // Активний опір контуру втрат, Ом
    double tq_25c;      // Паспортний час вимикання при 25 C, с
    double temp_j;      // Робоча температура кристала, C
    double dt;          // Крок чисельного інтегрування, с
    double t_max;       // Тривалість моделювання, с
} CommutationParams;

// Результати моделювання перехідного процесу
typedef struct {
    double tc_measured;     // Виміряний час зворотного зміщення, с
    double tq_actual;       // Час відновлення з урахуванням температури, с
    double peak_current;    // Піковий резонансний струм, А
    double peak_voltage;    // Пікова напруга на конденсаторі, В
    double max_dvdt;        // Максимальна швидкість відновлення напруги, В/мкс
    bool commutation_ok;    // Прапорець успішного вимикання
} SimulationResult;

// Стан головного тиристора
typedef enum {
    THYRISTOR_ON,
    THYRISTOR_REVERSE_BIASED,
    THYRISTOR_OFF_RECOVERED,
    THYRISTOR_FAILED
} ThyristorState;

// Розрахунок часу відновлення з урахуванням температури переходу
static double calculate_actual_tq(double tq_base, double temp_c) {
    const double alpha_temp = 0.008; // 0.8% на кожен градус понад 25 C
    if (temp_c <= 25.0) {
        return tq_base;
    }
    return tq_base * (1.0 + alpha_temp * (temp_c - 25.0));
}

SimulationResult simulate_mcmurray(const CommutationParams *p) {
    SimulationResult res = {0};
    res.tq_actual = calculate_actual_tq(p->tq_25c, p->temp_j);

    double t = 0.0;
    double vc = p->vs;      // Початковий заряд конденсатора
    double ic = 0.0;       // Початковий струм котушки
    ThyristorState t1_state = THYRISTOR_ON;

    double t_reverse_start = 0.0;
    double t_reverse_end = 0.0;
    double prev_vak = 0.0;

    while (t < p->t_max) {
        double vak = 0.0;

        // Симплектичний інтегратор Ейлера-Крамера
        double di_c = (vc - p->r_loss * ic) / p->lc;
        ic += di_c * p->dt;
        vc -= (ic / p->cc) * p->dt;

        if (ic > res.peak_current) {
            res.peak_current = ic;
        }
        if (fabs(vc) > res.peak_voltage) {
            res.peak_voltage = fabs(vc);
        }

        // Автомат станів симистора/тиристора та зустрічного діода
        if (t1_state == THYRISTOR_ON) {
            if (ic < p->i_load) {
                vak = 1.5; // Прямий спад відкритого тиристора
            } else {
                // Струм тиристора досяг нуля, надлишок іде в діод D1
                t1_state = THYRISTOR_REVERSE_BIASED;
                t_reverse_start = t;
                vak = -1.0; // Зворотне зміщення через спад на D1
            }
        } else if (t1_state == THYRISTOR_REVERSE_BIASED) {
            if (ic >= p->i_load) {
                vak = -1.0;
            } else {
                // Діод D1 закрився, починається наростання прямої напруги
                t_reverse_end = t;
                double tc = t_reverse_end - t_reverse_start;
                res.tc_measured = tc;

                if (tc >= res.tq_actual) {
                    t1_state = THYRISTOR_OFF_RECOVERED;
                } else {
                    t1_state = THYRISTOR_FAILED; // Зрив комутації!
                }
                vak = 0.0;
            }
        } else if (t1_state == THYRISTOR_OFF_RECOVERED) {
            // Тиристор надійно вимкнено, конденсатор дозаряджається струмом навантаження
            vak = p->vs - vc;
            double current_dvdt = (vak - prev_vak) / (p->dt * 1e6); // В/мкс
            if (current_dvdt > res.max_dvdt) {
                res.max_dvdt = current_dvdt;
            }
        } else if (t1_state == THYRISTOR_FAILED) {
            res.commutation_ok = false;
            break;
        }

        prev_vak = vak;
        t += p->dt;
    }

    res.commutation_ok = (t1_state == THYRISTOR_OFF_RECOVERED) && (res.tc_measured >= res.tq_actual);
    return res;
}

int main(void) {
    CommutationParams params = {
        .vs = 600.0,
        .i_load = 150.0,
        .cc = 7.5e-6,
        .lc = 50.0e-6,
        .r_loss = 0.04,
        .tq_25c = 20.0e-6,
        .temp_j = 85.0,     // Робоча температура 85 C
        .dt = 1e-8,
        .t_max = 200.0e-6
    };

    SimulationResult res = simulate_mcmurray(&params);

    printf("=== Результати чисельного моделювання комутатора ===\n");
    printf("Робоча температура кристала: %.1f C\n", params.temp_j);
    printf("Скоригований час вимикання tq: %.2f мкс\n", res.tq_actual * 1e6);
    printf("Виміряний час зворотного зміщення tc: %.2f мкс\n", res.tc_measured * 1e6);
    printf("Коефіцієнт запасу надійності ks: %.2f\n", res.tc_measured / res.tq_actual);
    printf("Піковий струм коливального контуру Ip: %.1f А\n", res.peak_current);
    printf("Максимальна швидкість наростання dv/dt: %.1f В/мкс\n", res.max_dvdt);
    printf("Підсумок комутації: %s\n", res.commutation_ok ? "УСПІШНО (НАДІЙНО)" : "ЗРИВ КОМУТАЦІЇ!");

    return res.commutation_ok ? 0 : 1;
}
