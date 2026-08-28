#include <stdbool.h>
#include <math.h>

typedef struct {
    double p0, v0, a0;  /* Стан склеювання при t = 0 */
    double p1, v1, a1;  /* Цільовий стан при t = T */
    double T;           /* Тривалість маневру */
    double c[6];        /* Коефіцієнти полінома: c[0] + c[1]*t + ... + c[5]*t^5 */
} QuinticSegment;

typedef struct {
    double pos;
    double vel;
    double acc;
    double jerk;
} TrajectoryPoint;

/* Розрахунок аналітичних коефіцієнтів C²-стику */
void quintic_solve(QuinticSegment *seg) {
    double T = seg->T;
    double T2 = T * T;
    double T3 = T2 * T;
    double T4 = T3 * T;
    double T5 = T4 * T;

    seg->c[0] = seg->p0;
    seg->c[1] = seg->v0;
    seg->c[2] = 0.5 * seg->a0;

    double dp = seg->p1 - (seg->p0 + seg->v0 * T + 0.5 * seg->a0 * T2);
    double dv = seg->v1 - (seg->v0 + seg->a0 * T);
    double da = seg->a1 - seg->a0;

    seg->c[3] = (10.0 * dp - 4.0 * dv * T + 0.5 * da * T2) / T3;
    seg->c[4] = (-15.0 * dp + 7.0 * dv * T - da * T2) / T4;
    seg->c[5] = (6.0 * dp - 3.0 * dv * T + 0.5 * da * T2) / T5;
}

/* Обчислення миттєвих уставок для контуру стабілізації */
TrajectoryPoint quintic_eval(const QuinticSegment *seg, double t) {
    if (t < 0.0) t = 0.0;
    if (t > seg->T) t = seg->T;

    double t2 = t * t;
    double t3 = t2 * t;
    double t4 = t3 * t;
    double t5 = t4 * t;

    TrajectoryPoint pt;
    pt.pos = seg->c[0] + seg->c[1]*t + seg->c[2]*t2 + seg->c[3]*t3 + seg->c[4]*t4 + seg->c[5]*t5;
    pt.vel = seg->c[1] + 2.0*seg->c[2]*t + 3.0*seg->c[3]*t2 + 4.0*seg->c[4]*t3 + 5.0*seg->c[5]*t4;
    pt.acc = 2.0*seg->c[2] + 6.0*seg->c[3]*t + 12.0*seg->c[4]*t2 + 20.0*seg->c[5]*t3;
    pt.jerk = 6.0*seg->c[3] + 24.0*seg->c[4]*t + 60.0*seg->c[5]*t2;
    return pt;
}

/* Перевірка лімітів та ітеративна корекція тривалості T */
bool quintic_rescale_time(QuinticSegment *seg, double v_max, double a_max, int max_iter) {
    for (int iter = 0; iter < max_iter; ++iter) {
        quintic_solve(seg);

        double max_v = 0.0;
        double max_a = 0.0;
        const int samples = 20;

        for (int i = 0; i <= samples; ++i) {
            double t = (seg->T * i) / samples;
            TrajectoryPoint pt = quintic_eval(seg, t);
            if (fabs(pt.vel) > max_v) max_v = fabs(pt.vel);
            if (fabs(pt.acc) > max_a) max_a = fabs(pt.acc);
        }

        if (max_v <= v_max && max_a <= a_max) {
            return true; /* Траєкторія кінодинамічно допустима */
        }

        double scale_v = max_v / v_max;
        double scale_a = sqrt(max_a / a_max);
        double scale = (scale_v > scale_a) ? scale_v : scale_a;
        if (scale < 1.05) scale = 1.05;

        seg->T *= scale; /* Розтягуємо час для зниження пікових навантажень */
    }
    return false;
}
