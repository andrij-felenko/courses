#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double v;
    double i_l;
} State;

static double diode_current(double v) {
    const double v_p = 0.07;
    const double i_p = 0.005;
    const double v_v = 0.35;
    const double i_v = 0.0005;
    const double alpha = 10.0;

    if (v < 0.0) {
        return -i_p * (fabs(v) / v_p);
    }
    double i_tunnel = i_p * (v / v_p) * exp(1.0 - v / v_p);
    double i_diff = (v > v_v) ? i_v * exp(alpha * (v - v_v)) : 0.0;
    return i_tunnel + i_diff;
}

static State derivatives(State s, double v_cc, double r_l, double l_ind, double c_cap) {
    State d;
    d.v = (s.i_l - diode_current(s.v)) / c_cap;
    d.i_l = (v_cc - s.v - r_l * s.i_l) / l_ind;
    return d;
}

int main(void) {
    const double v_cc = 0.18;      /* Напруга живлення у зоні NDR (В) */
    const double r_l = 2.0;         /* Опір навантаження та втрат (Ом) */
    const double l_ind = 1.0e-6;    /* Індуктивність контуру (Гн) */
    const double c_cap = 100.0e-12; /* Ємність контуру (Ф) */
    const double dt = 1.0e-11;      /* Крок чисельного інтегрування (с) */
    const int steps = 20000;

    State s = { .v = 0.01, .i_l = 0.001 };

    printf("Time(ns)\tVoltage(mV)\tCurrent(mA)\n");
    for (int step = 0; step < steps; ++step) {
        if (step % 2000 == 0) {
            printf("%.3f\t\t%.2f\t\t%.2f\n", step * dt * 1.0e9, s.v * 1000.0, s.i_l * 1000.0);
        }

        State k1 = derivatives(s, v_cc, r_l, l_ind, c_cap);
        
        State s2 = { s.v + 0.5 * dt * k1.v, s.i_l + 0.5 * dt * k1.i_l };
        State k2 = derivatives(s2, v_cc, r_l, l_ind, c_cap);

        State s3 = { s.v + 0.5 * dt * k2.v, s.i_l + 0.5 * dt * k2.i_l };
        State k3 = derivatives(s3, v_cc, r_l, l_ind, c_cap);

        State s4 = { s.v + dt * k3.v, s.i_l + dt * k3.i_l };
        State k4 = derivatives(s4, v_cc, r_l, l_ind, c_cap);

        s.v   += (dt / 6.0) * (k1.v + 2.0 * k2.v + 2.0 * k3.v + k4.v);
        s.i_l += (dt / 6.0) * (k1.i_l + 2.0 * k2.i_l + 2.0 * k3.i_l + k4.i_l);
    }

    return 0;
}
