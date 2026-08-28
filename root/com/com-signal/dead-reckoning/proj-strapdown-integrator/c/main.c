#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define GRAVITY_MSS 9.80665f

typedef struct {
    float x, y, z;
} Vec3;

typedef struct {
    float w, x, y, z;
} Quat;

typedef struct {
    float m[3][3];
} Mat3;

typedef struct {
    Vec3 pos;       /* Позиція [м] (North, East, Down) */
    Vec3 vel;       /* Швидкість [м/с] (North, East, Down) */
    Quat q;         /* Орієнтація (кватерніон повороту з body в nav) */
    Vec3 prev_acc;  /* Прискорення попереднього кроку для трапецеїдального інтеграла */
    Vec3 gyro_bias; /* Калібрувальне зміщення нуля гіроскопа [рад/с] */
    Vec3 accel_bias;/* Калібрувальне зміщення нуля акселерометра [м/с²] */
} InsState;

static inline Vec3 vec3_add(Vec3 a, Vec3 b) {
    return (Vec3){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vec3 vec3_sub(Vec3 a, Vec3 b) {
    return (Vec3){a.x - b.x, a.y - b.y, a.z - b.z};
}

static inline Vec3 vec3_scale(Vec3 v, float s) {
    return (Vec3){v.x * s, v.y * s, v.z * s};
}

static inline float vec3_norm(Vec3 v) {
    return sqrtf(v.x * v.x + v.y * v.y + v.z * v.z);
}

static inline Quat quat_norm(Quat q) {
    float n = sqrtf(q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z);
    if (n < 1e-8f) return (Quat){1.0f, 0.0f, 0.0f, 0.0f};
    float inv = 1.0f / n;
    return (Quat){q.w * inv, q.x * inv, q.y * inv, q.z * inv};
}

static inline Quat quat_mult(Quat a, Quat b) {
    return (Quat){
        a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z,
        a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y,
        a.w * b.y - a.x * b.z + a.y * b.w + a.z * b.x,
        a.w * b.z + a.x * b.y - a.y * b.x + a.z * b.w
    };
}

static inline Mat3 quat_to_dcm(Quat q) {
    Mat3 r;
    float qw = q.w, qx = q.x, qy = q.y, qz = q.z;
    float qx2 = qx * qx, qy2 = qy * qy, qz2 = qz * qz;

    r.m[0][0] = 1.0f - 2.0f * (qy2 + qz2);
    r.m[0][1] = 2.0f * (qx * qy - qw * qz);
    r.m[0][2] = 2.0f * (qx * qz + qw * qy);

    r.m[1][0] = 2.0f * (qx * qy + qw * qz);
    r.m[1][1] = 1.0f - 2.0f * (qx2 + qz2);
    r.m[1][2] = 2.0f * (qy * qz - qw * qx);

    r.m[2][0] = 2.0f * (qx * qz - qw * qy);
    r.m[2][1] = 2.0f * (qy * qz + qw * qx);
    r.m[2][2] = 1.0f - 2.0f * (qx2 + qy2);
    return r;
}

static inline Vec3 mat3_mult_vec3(Mat3 m, Vec3 v) {
    return (Vec3){
        m.m[0][0] * v.x + m.m[0][1] * v.y + m.m[0][2] * v.z,
        m.m[1][0] * v.x + m.m[1][1] * v.y + m.m[1][2] * v.z,
        m.m[2][0] * v.x + m.m[2][1] * v.y + m.m[2][2] * v.z
    };
}

void ins_init(InsState *ins, Vec3 init_pos, Vec3 init_vel, Quat init_q) {
    ins->pos = init_pos;
    ins->vel = init_vel;
    ins->q = quat_norm(init_q);
    ins->prev_acc = (Vec3){0.0f, 0.0f, 0.0f};
    ins->gyro_bias = (Vec3){0.0f, 0.0f, 0.0f};
    ins->accel_bias = (Vec3){0.0f, 0.0f, 0.0f};
}

void ins_update(InsState *ins, Vec3 raw_acc, Vec3 raw_gyro, float dt) {
    /* 1. Компенсація зміщень нуля (Bias) */
    Vec3 unb_gyro = vec3_sub(raw_gyro, ins->gyro_bias);
    Vec3 unb_acc  = vec3_sub(raw_acc, ins->accel_bias);

    /* 2. Інтегрування орієнтації через приріст кватерніона */
    Vec3 d_theta = vec3_scale(unb_gyro, dt);
    float angle = vec3_norm(d_theta);

    Quat dq;
    if (angle > 1e-8f) {
        float half_angle = 0.5f * angle;
        float factor = sinf(half_angle) / angle;
        dq = (Quat){cosf(half_angle), d_theta.x * factor, d_theta.y * factor, d_theta.z * factor};
    } else {
        dq = (Quat){1.0f, 0.5f * d_theta.x, 0.5f * d_theta.y, 0.5f * d_theta.z};
    }
    ins->q = quat_norm(quat_mult(ins->q, dq));

    /* 3. Поворот виміряної питомої сили у навігаційну систему NED */
    Mat3 dcm = quat_to_dcm(ins->q);
    Vec3 f_nav = mat3_mult_vec3(dcm, unb_acc);

    /* 4. Компенсація сили тяжіння: a_nav = f_nav + [0, 0, g] */
    Vec3 g_nav = {0.0f, 0.0f, GRAVITY_MSS};
    Vec3 cur_acc = vec3_add(f_nav, g_nav);

    /* 5. Трапецеїдальне інтегрування швидкості та позиції */
    Vec3 avg_acc = vec3_scale(vec3_add(ins->prev_acc, cur_acc), 0.5f);
    Vec3 next_vel = vec3_add(ins->vel, vec3_scale(avg_acc, dt));
    Vec3 avg_vel = vec3_scale(vec3_add(ins->vel, next_vel), 0.5f);

    ins->pos = vec3_add(ins->pos, vec3_scale(avg_vel, dt));
    ins->vel = next_vel;
    ins->prev_acc = cur_acc;
}

bool ins_check_and_apply_zupt(InsState *ins, Vec3 raw_acc, Vec3 raw_gyro, float gyro_thresh, float acc_thresh) {
    float g_diff = fabsf(vec3_norm(raw_acc) - GRAVITY_MSS);
    float w_norm = vec3_norm(raw_gyro);

    if (g_diff < acc_thresh && w_norm < gyro_thresh) {
        /* Детектор спокою: апарат стоїть на місці */
        ins->vel = (Vec3){0.0f, 0.0f, 0.0f};
        ins->prev_acc = (Vec3){0.0f, 0.0f, 0.0f};
        return true;
    }
    return false;
}

int main(void) {
    InsState ins;
    ins_init(&ins, (Vec3){0.0f, 0.0f, 0.0f}, (Vec3){0.0f, 0.0f, 0.0f}, (Quat){1.0f, 0.0f, 0.0f, 0.0f});

    float dt = 0.01f; /* 100 Гц */
    printf("=== Тест дискретної БІНС (100 Гц) ===\n");

    /* Симуляція: розгін уздовж осі X (North) з прискоренням 2.0 м/с² протягом 2 секунд */
    for (int i = 0; i < 200; ++i) {
        Vec3 acc = {2.0f, 0.0f, -GRAVITY_MSS}; /* Питома сила акселерометра */
        Vec3 gyro = {0.0f, 0.0f, 0.0f};
        ins_update(&ins, acc, gyro, dt);
    }

    printf("Після 2 с розгону: Pos=(%.3f, %.3f, %.3f) м, Vel=(%.3f, %.3f, %.3f) м/с\n",
           ins.pos.x, ins.pos.y, ins.pos.z, ins.vel.x, ins.vel.y, ins.vel.z);

    /* Рівномірний рух протягом 3 секунд */
    for (int i = 0; i < 300; ++i) {
        Vec3 acc = {0.0f, 0.0f, -GRAVITY_MSS};
        Vec3 gyro = {0.0f, 0.0f, 0.0f};
        ins_update(&ins, acc, gyro, dt);
    }

    printf("Після 3 с круїзу: Pos=(%.3f, %.3f, %.3f) м, Vel=(%.3f, %.3f, %.3f) м/с\n",
           ins.pos.x, ins.pos.y, ins.pos.z, ins.vel.x, ins.vel.y, ins.vel.z);

    return 0;
}
