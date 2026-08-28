#include <stdio.h>
#include <math.h>
#include <stdbool.h>

// Параметри електричного кола комутації
typedef struct {
    double v_cc;        // Напруга живлення, В
    double i_0;         // Початковий струм котушки, А
    double l_ind;       // Індуктивність навантаження, Гн
    double r_load;      // Власний активний опір обмотки, Ом
    double r_snubber;   // Демпфувальний опір снабера, Ом
    double c_snubber;   // Ємність снабера, Ф
} CircuitParams;

// Результати моделювання перехідного процесу
typedef struct {
    double v_peak;      // Максимальна зафіксована напруга на ключі, В
    double energy_res;  // Енергія, розсіяна на резисторі у вигляді тепла, Дж
    double t_settle;    // Час згасання струму до 1 % від початкового, с
    bool arc_ignited;   // Прапорець виникнення стійкої дуги (U > 12 В при I > 0.4 А)
} SimResult;

typedef struct {
    double i;   // Миттєвий струм через індуктивність
    double vc;  // Миттєва напруга на ємності
} State;

// Обчислення похідних системи диференціальних рівнянь
static void compute_derivatives(const CircuitParams* p, const State* s, double* di_dt, double* dvc_dt) {
    *di_dt = (p->v_cc - s->vc - s->i * (p->r_snubber + p->r_load)) / p->l_ind;
    *dvc_dt = s->i / p->c_snubber;
}

// Запуск симуляції методом Рунге - Кутти 4-го порядку (RK4)
SimResult simulate_turn_off(const CircuitParams p, double dt, double t_max) {
    SimResult res = { .v_peak = 0.0, .energy_res = 0.0, .t_settle = 0.0, .arc_ignited = false };
    State s = { .i = p.i_0, .vc = 0.0 };
    
    double t = 0.0;
    const double i_threshold = p.i_0 * 0.01;
    bool settled = false;

    while (t < t_max) {
        // Миттєва напруга на розімкненому ключі
        double v_sw = s.vc + s.i * p.r_snubber;
        if (v_sw > res.v_peak) {
            res.v_peak = v_sw;
        }

        // Перевірка порогових умов горіння дуги
        if (v_sw > 12.0 && s.i > 0.4) {
            res.arc_ignited = true;
        }

        // Інтегрування розсіюваної теплової енергії на резисторі
        res.energy_res += (s.i * s.i * p.r_snubber) * dt;

        if (!settled && fabs(s.i) < i_threshold) {
            res.t_settle = t;
            settled = true;
        }

        // Класичний алгоритм RK4
        double k1_i, k1_vc;
        compute_derivatives(&p, &s, &k1_i, &k1_vc);

        State s2 = { s.i + 0.5 * dt * k1_i, s.vc + 0.5 * dt * k1_vc };
        double k2_i, k2_vc;
        compute_derivatives(&p, &s2, &k2_i, &k2_vc);

        State s3 = { s.i + 0.5 * dt * k2_i, s.vc + 0.5 * dt * k2_vc };
        double k3_i, k3_vc;
        compute_derivatives(&p, &s3, &k3_i, &k3_vc);

        State s4 = { s.i + dt * k3_i, s.vc + dt * k3_vc };
        double k4_i, k4_vc;
        compute_derivatives(&p, &s4, &k4_i, &k4_vc);

        s.i += (dt / 6.0) * (k1_i + 2.0 * k2_i + 2.0 * k3_i + k4_i);
        s.vc += (dt / 6.0) * (k1_vc + 2.0 * k2_vc + 2.0 * k3_vc + k4_vc);

        t += dt;
    }

    return res;
}
