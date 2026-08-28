#include <cmath>

// Бортовий обчислювач планування: жодної купи, самі float — як у кабінному приладі.
struct Glider {
    float m, S, b, CD0, e;        // маса, площа, розмах, паразит. опір, к-т Освальда
    float rho = 1.225f, g = 9.81f;
};

static const float PI_F = 3.14159265f;

static inline float weight(const Glider& a) { return a.m * a.g; }
static inline float aspect(const Glider& a) { return a.b * a.b / a.S; }
static inline float k_ind(const Glider& a)  { return 1.0f / (PI_F * a.e * aspect(a)); }

// швидкість для заданого CL (пологе планування, L ≈ W)
static inline float speed(const Glider& a, float CL) {
    return sqrtf(2.0f * weight(a) / (a.rho * a.S * CL));
}
// вертикальне зниження на швидкості V
static inline float sink(const Glider& a, float V) {
    float CL = 2.0f * weight(a) / (a.rho * V * V * a.S);
    float CD = a.CD0 + k_ind(a) * CL * CL;
    return V * CD / CL;                              // = V / (L/D)
}

float ld_max(const Glider& a) {
    return 1.0f / (2.0f * sqrtf(a.CD0 * k_ind(a)));
}
float v_best_glide(const Glider& a) {
    float CL_best = sqrtf(a.CD0 / k_ind(a));
    return speed(a, CL_best);
}
// швидкість-щоб-летіти проти вітру: дотична з точки (вітер, 0) до поляри
float speed_to_fly(const Glider& a, float headwind) {
    float best_V = v_best_glide(a), best_gr = -1.0f;
    for (float V = 15.0f; V < 60.0f; V += 0.05f) {
        float gr = (V - headwind) / sink(a, V);
        if (gr > best_gr) { best_gr = gr; best_V = V; }
    }
    return best_V;
}
