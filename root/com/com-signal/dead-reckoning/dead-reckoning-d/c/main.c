#include <math.h>

#define G_MSS 9.80665f

typedef struct { float x, y, z; } Vector3;
typedef struct { float w, x, y, z; } Quaternion;

typedef struct {
    Vector3 pos;      /* Позиція в NED [м] */
    Vector3 vel;      /* Швидкість в NED [м/с] */
    Quaternion q;     /* Орієнтація Body -> Nav */
    Vector3 prev_acc; /* Прискорення попереднього кроку */
} InsEngine;

void ins_step(InsEngine *ins, Vector3 acc_b, Vector3 gyro_b, float dt) {
    /* 1. Оновлення кватерніона орієнтації через приріст кута */
    Vector3 d_th = {gyro_b.x * dt, gyro_b.y * dt, gyro_b.z * dt};
    float th_len = sqrtf(d_th.x * d_th.x + d_th.y * d_th.y + d_th.z * d_th.z);

    Quaternion dq;
    if (th_len > 1e-7f) {
        float half = 0.5f * th_len;
        float s = sinf(half) / th_len;
        dq = (Quaternion){cosf(half), d_th.x * s, d_th.y * s, d_th.z * s};
    } else {
        dq = (Quaternion){1.0f, 0.5f * d_th.x, 0.5f * d_th.y, 0.5f * d_th.z};
    }

    /* Кватерніонне множення ins->q = ins->q * dq */
    Quaternion q_new = {
        ins->q.w * dq.w - ins->q.x * dq.x - ins->q.y * dq.y - ins->q.z * dq.z,
        ins->q.w * dq.x + ins->q.x * dq.w + ins->q.y * dq.z - ins->q.z * dq.y,
        ins->q.w * dq.y - ins->q.x * dq.z + ins->q.y * dq.w + ins->q.z * dq.x,
        ins->q.w * dq.z + ins->q.x * dq.y - ins->q.y * dq.x + ins->q.z * dq.w
    };

    /* Нормалізація кватерніона */
    float q_norm = sqrtf(q_new.w * q_new.w + q_new.x * q_new.x + q_new.y * q_new.y + q_new.z * q_new.z);
    ins->q = (Quaternion){q_new.w / q_norm, q_new.x / q_norm, q_new.y / q_norm, q_new.z / q_norm};

    /* 2. Побудова матриці повороту R_b2n та поворот прискорення */
    float qw = ins->q.w, qx = ins->q.x, qy = ins->q.y, qz = ins->q.z;
    float r00 = 1.0f - 2.0f * (qy * qy + qz * qz);
    float r01 = 2.0f * (qx * qy - qw * qz);
    float r02 = 2.0f * (qx * qz + qw * qy);
    float r10 = 2.0f * (qx * qy + qw * qz);
    float r11 = 1.0f - 2.0f * (qx * qx + qz * qz);
    float r12 = 2.0f * (qy * qz - qw * qx);
    float r20 = 2.0f * (qx * qz - qw * qy);
    float r21 = 2.0f * (qy * qz + qw * qx);
    float r22 = 1.0f - 2.0f * (qx * qx + qy * qy);

    Vector3 f_nav = {
        r00 * acc_b.x + r01 * acc_b.y + r02 * acc_b.z,
        r10 * acc_b.x + r11 * acc_b.y + r12 * acc_b.z,
        r20 * acc_b.x + r21 * acc_b.y + r22 * acc_b.z
    };

    /* 3. Компенсація сили тяжіння: a_nav = f_nav + [0, 0, +g] */
    Vector3 cur_acc = {f_nav.x, f_nav.y, f_nav.z + G_MSS};

    /* 4. Трапецеїдальне інтегрування швидкості та позиції */
    Vector3 next_vel = {
        ins->vel.x + 0.5f * (ins->prev_acc.x + cur_acc.x) * dt,
        ins->vel.y + 0.5f * (ins->prev_acc.y + cur_acc.y) * dt,
        ins->vel.z + 0.5f * (ins->prev_acc.z + cur_acc.z) * dt
    };

    ins->pos.x += 0.5f * (ins->vel.x + next_vel.x) * dt;
    ins->pos.y += 0.5f * (ins->vel.y + next_vel.y) * dt;
    ins->pos.z += 0.5f * (ins->vel.z + next_vel.z) * dt;

    ins->vel = next_vel;
    ins->prev_acc = cur_acc;
}
