#include <iostream>
#include <vector>
#include <span>
#include <numeric>

struct CossPoint {
    double v;    // напруга сток-витік, В
    double coss; // вихідна ємність, Фарад
};

struct CossResult {
    double q_oss{0.0};   // повний заряд, Кулони
    double e_oss{0.0};   // накопичена енергія, Джоулі
    double c_o_tr{0.0};  // часова еквівалентна ємність, Фаради
    double c_o_er{0.0};  // енергетична еквівалентна ємність, Фаради
};

constexpr CossResult integrate_coss(std::span<const CossPoint> pts) noexcept {
    if (pts.size() < 2) return {};

    double q_total = 0.0;
    double e_total = 0.0;

    for (size_t i = 0; i < pts.size() - 1; ++i) {
        const double v1 = pts[i].v;
        const double v2 = pts[i+1].v;
        const double c1 = pts[i].coss;
        const double c2 = pts[i+1].coss;
        const double dv = v2 - v1;

        if (dv <= 0.0) continue;

        q_total += 0.5 * (c1 + c2) * dv;
        e_total += 0.5 * (v1 * c1 + v2 * c2) * dv;
    }

    const double v_max = pts.back().v;
    if (v_max <= 0.0) return {};

    return CossResult{
        .q_oss = q_total,
        .e_oss = e_total,
        .c_o_tr = q_total / v_max,
        .c_o_er = (2.0 * e_total) / (v_max * v_max)
    };
}
