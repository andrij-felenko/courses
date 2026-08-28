#include <stdio.h>
#include <math.h>

typedef struct {
    double x, y, z;
} Vector3;

static inline Vector3 vec_add(Vector3 a, Vector3 b) {
    return (Vector3){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vector3 vec_sub(Vector3 a, Vector3 b) {
    return (Vector3){a.x - b.x, a.y - b.y, a.z - b.z};
}

static inline Vector3 vec_scale(Vector3 a, double s) {
    return (Vector3){a.x * s, a.y * s, a.z * s};
}

static inline Vector3 vec_cross(Vector3 a, Vector3 b) {
    return (Vector3){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

static inline double vec_norm_sq(Vector3 a) {
    return a.x * a.x + a.y * a.y + a.z * a.z;
}

typedef struct {
    Vector3 pos;
    Vector3 vel;
    double charge;
    double mass;
} Particle;

void boris_step(Particle *p, Vector3 E, Vector3 B, double dt) {
    double q_over_m = p->charge / p->mass;
    Vector3 half_E = vec_scale(E, q_over_m * dt * 0.5);

    // 1. Половина E-прискорення
    Vector3 v_minus = vec_add(p->vel, half_E);

    // 2. Векторне обертання у полем B
    Vector3 t = vec_scale(B, q_over_m * dt * 0.5);
    double t_sq = vec_norm_sq(t);
    Vector3 s = vec_scale(t, 2.0 / (1.0 + t_sq));

    Vector3 v_prime = vec_add(v_minus, vec_cross(v_minus, t));
    Vector3 v_plus = vec_add(v_minus, vec_cross(v_prime, s));

    // 3. Друга половина E-прискорення
    p->vel = vec_add(v_plus, half_E);

    // 4. Оновлення координат
    p->pos = vec_add(p->pos, vec_scale(p->vel, dt));
}

int main(void) {
    Particle electron = {
        .pos = {0.0, 0.0, 0.0},
        .vel = {1e6, 0.0, 2e5},
        .charge = -1.60217663e-19,
        .mass = 9.1093837e-31
    };

    Vector3 E = {0.0, 0.0, 0.0};
    Vector3 B = {0.0, 0.0, 0.01};
    double dt = 1e-11;

    printf("Step\tX_mm\t\tY_mm\t\tZ_mm\n");
    for (int step = 0; step <= 1000; step++) {
        if (step % 100 == 0) {
            printf("%d\t%.4f\t%.4f\t%.4f\n",
                   step, electron.pos.x * 1e3, electron.pos.y * 1e3, electron.pos.z * 1e3);
        }
        boris_step(&electron, E, B, dt);
    }
    return 0;
}
