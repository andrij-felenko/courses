#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define STATE_DIM 9
#define MEAS_DIM 3

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

static inline Vec3 vec3_clamp_norm(Vec3 a, double max_val) {
    double n = vec3_norm(a);
    if (n > max_val && n > 1e-6) {
        return vec3_scale(a, max_val / n);
    }
    return a;
}

/* 1D Фільтр Калмана (PV-A) для однієї координатної осі */
typedef struct {
    double p, v, a;      /* стан: координата, швидкість, прискорення */
    double P[3][3];      /* коваріація помилки */
    double q_acc;        /* інтенсивність шуму маневру цілі */
    double r_meas;       /* дисперсія шуму давача */
} AxisKalman;

static void axis_kalman_init(AxisKalman* kf, double init_p, double q_acc, double r_meas) {
    kf->p = init_p;
    kf->v = 0.0;
    kf->a = 0.0;
    kf->q_acc = q_acc;
    kf->r_meas = r_meas;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            kf->P[i][j] = (i == j) ? 10.0 : 0.0;
        }
    }
}

static void axis_kalman_predict(AxisKalman* kf, double dt) {
    double dt2 = 0.5 * dt * dt;
    /* Екстраполяція стану */
    kf->p += kf->v * dt + kf->a * dt2;
    kf->v += kf->a * dt;

    /* Матриця переходу F: [1, dt, dt2; 0, 1, dt; 0, 0, 1] */
    double P00 = kf->P[0][0] + dt * (kf->P[1][0] + kf->P[0][1]) + dt2 * (kf->P[2][0] + kf->P[0][2])
                 + dt * dt * kf->P[1][1] + dt * dt2 * (kf->P[2][1] + kf->P[1][2]) + dt2 * dt2 * kf->P[2][2];
    double P01 = kf->P[0][1] + dt * kf->P[1][1] + dt2 * kf->P[2][1] + dt * kf->P[0][2] + dt * dt * kf->P[1][2] + dt * dt2 * kf->P[2][2];
    double P02 = kf->P[0][2] + dt * kf->P[1][2] + dt2 * kf->P[2][2];
    double P11 = kf->P[1][1] + dt * (kf->P[2][1] + kf->P[1][2]) + dt * dt * kf->P[2][2];
    double P12 = kf->P[1][2] + dt * kf->P[2][2];
    double P22 = kf->P[2][2] + kf->q_acc * dt;

    kf->P[0][0] = P00; kf->P[0][1] = P01; kf->P[0][2] = P02;
    kf->P[1][0] = P01; kf->P[1][1] = P11; kf->P[1][2] = P12;
    kf->P[2][0] = P02; kf->P[2][1] = P12; kf->P[2][2] = P22;
}

static void axis_kalman_update(AxisKalman* kf, double z_meas) {
    double inn = z_meas - kf->p;
    double s = kf->P[0][0] + kf->r_meas;
    if (fabs(s) < 1e-9) return;

    double k0 = kf->P[0][0] / s;
    double k1 = kf->P[1][0] / s;
    double k2 = kf->P[2][0] / s;

    kf->p += k0 * inn;
    kf->v += k1 * inn;
    kf->a += k2 * inn;

    double p00 = kf->P[0][0], p01 = kf->P[0][1], p02 = kf->P[0][2];
    kf->P[0][0] -= k0 * p00; kf->P[0][1] -= k0 * p01; kf->P[0][2] -= k0 * p02;
    kf->P[1][0] -= k1 * p00; kf->P[1][1] -= k1 * p01; kf->P[1][2] -= k1 * p02;
    kf->P[2][0] -= k2 * p00; kf->P[2][1] -= k2 * p01; kf->P[2][2] -= k2 * p02;
}

/* 3D Стан цілі */
typedef struct {
    AxisKalman kf_x, kf_y, kf_z;
} TargetEstimator;

void target_estimator_init(TargetEstimator* est, Vec3 init_pos, double q_acc, double r_meas) {
    axis_kalman_init(&est->kf_x, init_pos.x, q_acc, r_meas);
    axis_kalman_init(&est->kf_y, init_pos.y, q_acc, r_meas);
    axis_kalman_init(&est->kf_z, init_pos.z, q_acc, r_meas);
}

void target_estimator_step(TargetEstimator* est, double dt, Vec3 raw_meas, bool valid_meas) {
    axis_kalman_predict(&est->kf_x, dt);
    axis_kalman_predict(&est->kf_y, dt);
    axis_kalman_predict(&est->kf_z, dt);

    if (valid_meas) {
        axis_kalman_update(&est->kf_x, raw_meas.x);
        axis_kalman_update(&est->kf_y, raw_meas.y);
        axis_kalman_update(&est->kf_z, raw_meas.z);
    }
}

/* Конфігурація наведення */
typedef struct {
    double N;            /* Навігаційний коефіцієнт (3.0 .. 5.0) */
    double a_max;        /* Граничне командне прискорення [м/с^2] */
    bool use_apn;        /* Чи використовувати APN компенсацію маневру */
} GuidanceConfig;

/* Генератор прискорення APN */
Vec3 compute_guidance_acceleration(
    GuidanceConfig cfg,
    Vec3 drone_pos,
    Vec3 drone_vel,
    const TargetEstimator* est
) {
    Vec3 target_pos = {est->kf_x.p, est->kf_y.p, est->kf_z.p};
    Vec3 target_vel = {est->kf_x.v, est->kf_y.v, est->kf_z.v};
    Vec3 target_acc = {est->kf_x.a, est->kf_y.a, est->kf_z.a};

    Vec3 R_vec = vec3_sub(target_pos, drone_pos);
    double R_norm = vec3_norm(R_vec);
    if (R_norm < 0.1) {
        return (Vec3){0.0, 0.0, 0.0};
    }

    Vec3 e_los = vec3_scale(R_vec, 1.0 / R_norm);
    Vec3 V_r = vec3_sub(target_vel, drone_vel);

    /* Швидкість зближення: V_c = - (R · V_r) / R */
    double V_c = -vec3_dot(e_los, V_r);
    if (V_c < 0.1) {
        V_c = 0.1; /* Захист від втрати швидкості зближення */
    }

    /* Кутова швидкість лінії візування: Ω = (R × V_r) / ||R||² */
    Vec3 cross_rv = vec3_cross(R_vec, V_r);
    Vec3 Omega = vec3_scale(cross_rv, 1.0 / (R_norm * R_norm));

    /* Базова складова PN: N * V_c * (Ω × e_los) */
    Vec3 omega_cross_los = vec3_cross(Omega, e_los);
    Vec3 a_pn = vec3_scale(omega_cross_los, cfg.N * V_c);

    /* Складова APN для маневруючої цілі: (N / 2) * a_target_normal */
    Vec3 a_total = a_pn;
    if (cfg.use_apn) {
        Vec3 a_t_parallel = vec3_scale(e_los, vec3_dot(target_acc, e_los));
        Vec3 a_t_perp = vec3_sub(target_acc, a_t_parallel);
        Vec3 a_apn = vec3_scale(a_t_perp, cfg.N * 0.5);
        a_total = vec3_add(a_total, a_apn);
    }

    return vec3_clamp_norm(a_total, cfg.a_max);
}
