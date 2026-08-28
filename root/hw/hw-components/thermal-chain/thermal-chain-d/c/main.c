#include <stdio.h>
#include <math.h>

/* Структура 3-ланкової фізичної теплової моделі Кауера */
typedef struct {
    double r[3];  /* Теплові опори шарів [°C/Вт]: кристал, припій, фланець */
    double c[3];  /* Теплоємності шарів [Дж/°C] */
    double t[3];  /* Поточні температури вузлів [°C] */
} CauerModel3;

/* Крок чисельного інтегрування теплового стану методом Ейлера */
void cauer_step(CauerModel3 *m, double p_in, double t_amb, double dt) {
    /* Розрахунок теплових потоків між сусідніми вузлами */
    double q01 = (m->t[0] - m->t[1]) / m->r[0];
    double q12 = (m->t[1] - m->t[2]) / m->r[1];
    double q2a = (m->t[2] - t_amb) / m->r[2];

    /* Зміна температур вузлів: dT = (Q_in - Q_out) / C * dt */
    m->t[0] += ((p_in - q01) / m->c[0]) * dt;
    m->t[1] += ((q01 - q12) / m->c[1]) * dt;
    m->t[2] += ((q12 - q2a) / m->c[2]) * dt;
}

int main(void) {
    /* Параметри MOSFET у корпусі TO-247 (Кауер) */
    CauerModel3 mosfet = {
        .r = { 0.095, 0.345, 0.560 },             /* θJC_total = 1.0 °C/Вт */
        .c = { 1.85e-3, 2.10e-2, 2.15e-1 },       /* Дж/°C */
        .t = { 25.0, 25.0, 25.0 }                 /* Початкова температура 25 °C */
    };

    double t_ambient = 25.0;                      /* Температура повітря 25 °C */
    double dt = 1e-5;                             /* Крок за часом 10 мкс */
    double sim_time = 0.05;                       /* Загальний час моделювання 50 мс */
    double p_pulse = 200.0;                       /* Імпульс потужності 200 Вт */
    double t_pulse_end = 0.01;                    /* Тривалість імпульсу 10 мс */

    int steps = (int)(sim_time / dt);
    printf("Час [мс]\tПотужність [Вт]\tT_кристал [°C]\tT_фланець [°C]\n");

    for (int i = 0; i <= steps; i++) {
        double current_time = i * dt;
        double p_now = (current_time <= t_pulse_end) ? p_pulse : 0.0;

        cauer_step(&mosfet, p_now, t_ambient, dt);

        if (i % 200 == 0) {  /* Друк кожні 2 мс */
            printf("%.1f\t\t%.1f\t\t%.2f\t\t%.2f\n",
                   current_time * 1000.0, p_now, mosfet.t[0], mosfet.t[2]);
        }
    }

    return 0;
}
