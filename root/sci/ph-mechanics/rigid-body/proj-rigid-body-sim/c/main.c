/* C Implementation: 3D Rigid Body RK4 Physics Integrator */
#include <stdio.h>
#include <math.h>

typedef struct {
    double x, y, z;
} Vec3;

typedef struct {
    double w, x, y, z;
} Quat;

typedef struct {
    Vec3 pos;       /* Позиція центру мас у світі (m) */
    Vec3 vel;       /* Поступальна швидкість у світі (m/s) */
    Quat quat;      /* Орієнтація у вигляді одиничного кватерніона */
    Vec3 omega;     /* Кутова швидкість у власних осях тіла (rad/s) */
} RigidBodyState;

typedef struct {
    double mass;    /* Маса тіла (kg) */
    Vec3 I_diag;    /* Головні моменти інерції (I_xx, I_yy, I_zz) (kg·m²) */
} RigidBodyProps;

typedef struct {
    Vec3 force_world;   /* Зовнішня сила у світовій системі (N) */
    Vec3 torque_body;   /* Зовнішній момент у власній системі (N·m) */
} ExternalInputs;

typedef struct {
    Vec3 d_pos;
    Vec3 d_vel;
    Quat d_quat;
    Vec3 d_omega;
} StateDeriv;

/* Операції над векторами */
static inline Vec3 vec3_add(Vec3 a, Vec3 b) {
    return (Vec3){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vec3 vec3_scale(Vec3 v, double s) {
    return (Vec3){v.x * s, v.y * s, v.z * s};
}

static inline Vec3 vec3_cross(Vec3 a, Vec3 b) {
    return (Vec3){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

/* Нормування кватерніона для запобігання чисельному дрейфу */
static inline Quat quat_normalize(Quat q) {
    double len = sqrt(q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z);
    if (len < 1e-12) return (Quat){1.0, 0.0, 0.0, 0.0};
    return (Quat){q.w / len, q.x / len, q.y / len, q.z / len};
}

/* Добуток кватерніона на кватерніон кутової швидкості (0, w_x, w_y, w_z) */
static inline Quat quat_deriv(Quat q, Vec3 w) {
    return (Quat){
        0.5 * (-q.x * w.x - q.y * w.y - q.z * w.z),
        0.5 * ( q.w * w.x + q.y * w.z - q.z * w.y),
        0.5 * ( q.w * w.y + q.z * w.x - q.x * w.z),
        0.5 * ( q.w * w.z + q.x * w.y - q.y * w.x)
    };
}

/* Обчислення похідних стану dS/dt */
StateDeriv compute_derivatives(const RigidBodyState *s, const RigidBodyProps *props, const ExternalInputs *in) {
    StateDeriv d;
    d.d_pos = s->vel;
    d.d_vel = vec3_scale(in->force_world, 1.0 / props->mass);
    d.d_quat = quat_deriv(s->quat, s->omega);

    /* Рівняння руху Ейлера: I · dω/dt = M - ω × (I · ω) */
    Vec3 Iw = {
        props->I_diag.x * s->omega.x,
        props->I_diag.y * s->omega.y,
        props->I_diag.z * s->omega.z
    };
    Vec3 gyro_torque = vec3_cross(s->omega, Iw);
    Vec3 net_torque = {
        in->torque_body.x - gyro_torque.x,
        in->torque_body.y - gyro_torque.y,
        in->torque_body.z - gyro_torque.z
    };

    d.d_omega = (Vec3){
        net_torque.x / props->I_diag.x,
        net_torque.y / props->I_diag.y,
        net_torque.z / props->I_diag.z
    };
    return d;
}

/* Інтегрування одного кроку за допомогою RK4 */
void rigid_body_step_rk4(RigidBodyState *state, const RigidBodyProps *props, const ExternalInputs *in, double dt) {
    StateDeriv k1 = compute_derivatives(state, props, in);

    RigidBodyState s_k2 = *state;
    s_k2.pos = vec3_add(state->pos, vec3_scale(k1.d_pos, dt * 0.5));
    s_k2.vel = vec3_add(state->vel, vec3_scale(k1.d_vel, dt * 0.5));
    s_k2.quat.w += k1.d_quat.w * dt * 0.5;
    s_k2.quat.x += k1.d_quat.x * dt * 0.5;
    s_k2.quat.y += k1.d_quat.y * dt * 0.5;
    s_k2.quat.z += k1.d_quat.z * dt * 0.5;
    s_k2.quat = quat_normalize(s_k2.quat);
    s_k2.omega = vec3_add(state->omega, vec3_scale(k1.d_omega, dt * 0.5));
    StateDeriv k2 = compute_derivatives(&s_k2, props, in);

    RigidBodyState s_k3 = *state;
    s_k3.pos = vec3_add(state->pos, vec3_scale(k2.d_pos, dt * 0.5));
    s_k3.vel = vec3_add(state->vel, vec3_scale(k2.d_vel, dt * 0.5));
    s_k3.quat.w += k2.d_quat.w * dt * 0.5;
    s_k3.quat.x += k2.d_quat.x * dt * 0.5;
    s_k3.quat.y += k2.d_quat.y * dt * 0.5;
    s_k3.quat.z += k2.d_quat.z * dt * 0.5;
    s_k3.quat = quat_normalize(s_k3.quat);
    s_k3.omega = vec3_add(state->omega, vec3_scale(k2.d_omega, dt * 0.5));
    StateDeriv k3 = compute_derivatives(&s_k3, props, in);

    RigidBodyState s_k4 = *state;
    s_k4.pos = vec3_add(state->pos, vec3_scale(k3.d_pos, dt));
    s_k4.vel = vec3_add(state->vel, vec3_scale(k3.d_vel, dt));
    s_k4.quat.w += k3.d_quat.w * dt;
    s_k4.quat.x += k3.d_quat.x * dt;
    s_k4.quat.y += k3.d_quat.y * dt;
    s_k4.quat.z += k3.d_quat.z * dt;
    s_k4.quat = quat_normalize(s_k4.quat);
    s_k4.omega = vec3_add(state->omega, vec3_scale(k3.d_omega, dt));
    StateDeriv k4 = compute_derivatives(&s_k4, props, in);

    /* Оновлення стану: S_{t+dt} = S_t + (dt/6) * (k1 + 2*k2 + 2*k3 + k4) */
    state->pos.x += (dt / 6.0) * (k1.d_pos.x + 2.0 * k2.d_pos.x + 2.0 * k3.d_pos.x + k4.d_pos.x);
    state->pos.y += (dt / 6.0) * (k1.d_pos.y + 2.0 * k2.d_pos.y + 2.0 * k3.d_pos.y + k4.d_pos.y);
    state->pos.z += (dt / 6.0) * (k1.d_pos.z + 2.0 * k2.d_pos.z + 2.0 * k3.d_pos.z + k4.d_pos.z);

    state->vel.x += (dt / 6.0) * (k1.d_vel.x + 2.0 * k2.d_vel.x + 2.0 * k3.d_vel.x + k4.d_vel.x);
    state->vel.y += (dt / 6.0) * (k1.d_vel.y + 2.0 * k2.d_vel.y + 2.0 * k3.d_vel.y + k4.d_vel.y);
    state->vel.z += (dt / 6.0) * (k1.d_vel.z + 2.0 * k2.d_vel.z + 2.0 * k3.d_vel.z + k4.d_vel.z);

    state->quat.w += (dt / 6.0) * (k1.d_quat.w + 2.0 * k2.d_quat.w + 2.0 * k3.d_quat.w + k4.d_quat.w);
    state->quat.x += (dt / 6.0) * (k1.d_quat.x + 2.0 * k2.d_quat.x + 2.0 * k3.d_quat.x + k4.d_quat.x);
    state->quat.y += (dt / 6.0) * (k1.d_quat.y + 2.0 * k2.d_quat.y + 2.0 * k3.d_quat.y + k4.d_quat.y);
    state->quat.z += (dt / 6.0) * (k1.d_quat.z + 2.0 * k2.d_quat.z + 2.0 * k3.d_quat.z + k4.d_quat.z);
    state->quat = quat_normalize(state->quat);

    state->omega.x += (dt / 6.0) * (k1.d_omega.x + 2.0 * k2.d_omega.x + 2.0 * k3.d_omega.x + k4.d_omega.x);
    state->omega.y += (dt / 6.0) * (k1.d_omega.y + 2.0 * k2.d_omega.y + 2.0 * k3.d_omega.y + k4.d_omega.y);
    state->omega.z += (dt / 6.0) * (k1.d_omega.z + 2.0 * k2.d_omega.z + 2.0 * k3.d_omega.z + k4.d_omega.z);
}

int main(void) {
    RigidBodyState state = {
        .pos = {0.0, 0.0, 10.0},
        .vel = {0.0, 0.0, 0.0},
        .quat = {1.0, 0.0, 0.0, 0.0},
        .omega = {1.0, 20.0, 0.1} /* Обертання навколо проміжної осі y (нестійке) */
    };

    RigidBodyProps props = {
        .mass = 2.0,
        .I_diag = {1.0, 2.0, 3.0} /* I_xx < I_yy < I_zz */
    };

    ExternalInputs in = {
        .force_world = {0.0, 0.0, -9.81 * 2.0}, /* Сила тяжіння */
        .torque_body = {0.0, 0.0, 0.0}          /* Вільне обертання */
    };

    double dt = 0.001;
    printf("Крок\t Час (s)\t Z-Позиція\t Omega_X\t Omega_Y\t Omega_Z\n");
    for (int step = 0; step <= 2000; step++) {
        if (step % 200 == 0) {
            printf("%d\t %.3f\t %.3f\t\t %.3f\t %.3f\t %.3f\n",
                   step, step * dt, state.pos.z, state.omega.x, state.omega.y, state.omega.z);
        }
        rigid_body_step_rk4(&state, &props, &in, dt);
    }
    return 0;
}
