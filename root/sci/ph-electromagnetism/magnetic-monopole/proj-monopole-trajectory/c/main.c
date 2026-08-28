#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double x, y, z;
} Vec3;

static inline Vec3 vec3_add(Vec3 a, Vec3 b) {
    return (Vec3){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vec3 vec3_sub(Vec3 a, Vec3 b) {
    return (Vec3){a.x - b.x, a.y - b.y, a.z - b.z};
}

static inline Vec3 vec3_scale(Vec3 a, double s) {
    return (Vec3){a.x * s, a.y * s, a.z * s};
}

static inline double vec3_dot(Vec3 a, Vec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline Vec3 vec3_cross(Vec3 a, Vec3 b) {
    return (Vec3){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

static inline double vec3_norm(Vec3 a) {
    return sqrt(vec3_dot(a, a));
}

typedef struct {
    double m;
    double q;
    double g;
    double mu;
} MonopoleSim;

static inline MonopoleSim monopole_init(double m, double q, double g) {
    return (MonopoleSim){m, q, g, (q * g) / (4.0 * M_PI)};
}

static Vec3 monopole_accel(const MonopoleSim* sim, Vec3 r, Vec3 v) {
    double r_len = vec3_norm(r);
    if (r_len < 1e-12) return (Vec3){0.0, 0.0, 0.0};
    Vec3 vr = vec3_cross(v, r);
    return vec3_scale(vr, sim->mu / (sim->m * r_len * r_len * r_len));
}

static Vec3 monopole_poincare(const MonopoleSim* sim, Vec3 r, Vec3 v) {
    double r_len = vec3_norm(r);
    if (r_len < 1e-12) return (Vec3){0.0, 0.0, 0.0};
    Vec3 r_hat = vec3_scale(r, 1.0 / r_len);
    Vec3 L = vec3_scale(vec3_cross(r, v), sim->m);
    return vec3_sub(L, vec3_scale(r_hat, sim->mu));
}

static void monopole_step_rk4(const MonopoleSim* sim, Vec3* r, Vec3* v, double dt) {
    Vec3 k1_r = *v;
    Vec3 k1_v = monopole_accel(sim, *r, *v);

    Vec3 r2 = vec3_add(*r, vec3_scale(k1_r, 0.5 * dt));
    Vec3 v2 = vec3_add(*v, vec3_scale(k1_v, 0.5 * dt));
    Vec3 k2_r = v2;
    Vec3 k2_v = monopole_accel(sim, r2, v2);

    Vec3 r3 = vec3_add(*r, vec3_scale(k2_r, 0.5 * dt));
    Vec3 v3 = vec3_add(*v, vec3_scale(k3_v, 0.5 * dt));
    Vec3 k3_r = v3;
    Vec3 k3_v = monopole_accel(sim, r3, v3);

    Vec3 r4 = vec3_add(*r, vec3_scale(k3_r, dt));
    Vec3 v4 = vec3_add(*v, vec3_scale(k3_v, dt));
    Vec3 k4_r = v4;
    Vec3 k4_v = monopole_accel(sim, r4, v4);

    Vec3 dr = vec3_scale(vec3_add(vec3_add(k1_r, vec3_scale(k2_r, 2.0)),
                                  vec3_add(vec3_scale(k3_r, 2.0), k4_r)), dt / 6.0);
    Vec3 dv = vec3_scale(vec3_add(vec3_add(k1_v, vec3_scale(k2_v, 2.0)),
                                  vec3_scale(k3_v, 2.0), k4_v)), dt / 6.0);

    *r = vec3_add(*r, dr);
    *v = vec3_add(*v, dv);
}

int main(void) {
    MonopoleSim sim = monopole_init(1.0, 1.0, 4.0 * M_PI);
    Vec3 r = {-5.0, 1.0, 0.0};
    Vec3 v = {1.0, 0.0, 0.0};
    double dt = 0.001;

    Vec3 J0 = monopole_poincare(&sim, r, v);
    printf("J0 = (%f, %f, %f)\n", J0.x, J0.y, J0.z);

    for (int i = 0; i < 10000; ++i) {
        monopole_step_rk4(&sim, &r, &v, dt);
    }

    Vec3 J_end = monopole_poincare(&sim, r, v);
    printf("J_end = (%f, %f, %f)\n", J_end.x, J_end.y, J_end.z);
    return 0;
}
