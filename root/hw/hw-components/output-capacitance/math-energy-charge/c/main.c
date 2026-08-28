#include <stdio.h>
#include <math.h>

typedef struct {
    double v;    // напруга сток-витік, В
    double coss; // вихідна ємність, Фарад
} CossPoint;

typedef struct {
    double q_oss;   // повний заряд, Кулони
    double e_oss;   // накопичена енергія, Джоулі
    double c_o_tr;  // часова еквівалентна ємність, Фаради
    double c_o_er;  // енергетична еквівалентна ємність, Фаради
} CossResult;

CossResult integrate_coss(const CossPoint* pts, size_t count) {
    CossResult res = {0.0, 0.0, 0.0, 0.0};
    if (count < 2) return res;

    for (size_t i = 0; i < count - 1; ++i) {
        double v1 = pts[i].v;
        double v2 = pts[i+1].v;
        double c1 = pts[i].coss;
        double c2 = pts[i+1].coss;
        double dv = v2 - v1;

        if (dv <= 0.0) continue;

        // Метод трапецій для заряду: dq = 0.5 * (C1 + C2) * dv
        double dq = 0.5 * (c1 + c2) * dv;
        res.q_oss += dq;

        // Метод трапецій для енергії: dE = 0.5 * (v1*C1 + v2*C2) * dv
        double de = 0.5 * (v1 * c1 + v2 * c2) * dv;
        res.e_oss += de;
    }

    double v_max = pts[count - 1].v;
    if (v_max > 0.0) {
        res.c_o_tr = res.q_oss / v_max;
        res.c_o_er = (2.0 * res.e_oss) / (v_max * v_max);
    }
    return res;
}
