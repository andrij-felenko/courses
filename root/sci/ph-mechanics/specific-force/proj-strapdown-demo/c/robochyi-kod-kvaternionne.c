#include <math.h>

typedef struct { float x, y, z; }    Vec3;
typedef struct { float w, x, y, z; } Quat;

// Добуток кватерніонів a ⊗ b (складання двох поворотів).
static Quat quat_mul(Quat a, Quat b) {
    return (Quat){
        a.w*b.w - a.x*b.x - a.y*b.y - a.z*b.z,
        a.w*b.x + a.x*b.w + a.y*b.z - a.z*b.y,
        a.w*b.y - a.x*b.z + a.y*b.w + a.z*b.x,
        a.w*b.z + a.x*b.y - a.y*b.x + a.z*b.w
    };
}

// Повернути до одиничної довжини — інакше обертання «попливе» масштабом.
static Quat quat_unit(Quat q) {
    float inv = 1.0f / sqrtf(q.w*q.w + q.x*q.x + q.y*q.y + q.z*q.z);
    return (Quat){ q.w*inv, q.x*inv, q.y*inv, q.z*inv };
}

// Повернути вектор тіла у світ:  v_світ = q ⊗ (0,v) ⊗ q*.
static Vec3 quat_rotate(Quat q, Vec3 v) {
    Quat p  = { 0.0f, v.x, v.y, v.z };
    Quat qc = { q.w, -q.x, -q.y, -q.z };
    Quat r  = quat_mul(quat_mul(q, p), qc);
    return (Vec3){ r.x, r.y, r.z };
}

// Точний приріст орієнтації з вектора повороту θ = ω·dt за крок.
static Quat quat_delta(Vec3 rotvec) {
    float a = sqrtf(rotvec.x*rotvec.x + rotvec.y*rotvec.y + rotvec.z*rotvec.z);
    if (a < 1e-9f)                      // мала межа: θ/2 просто у векторну частину
        return (Quat){ 1.0f, 0.5f*rotvec.x, 0.5f*rotvec.y, 0.5f*rotvec.z };
    float s = sinf(a * 0.5f) / a;
    return (Quat){ cosf(a * 0.5f), rotvec.x*s, rotvec.y*s, rotvec.z*s };
}
