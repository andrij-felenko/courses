#include <math.h>

typedef struct { float x, y, z; } vec3;
typedef struct { float w, x, y, z; } quat;

/* спряжений кватерніон = обернений поворот (для одиничного q) */
static quat quat_conj(quat q) { quat r = { q.w, -q.x, -q.y, -q.z }; return r; }

/* застосувати поворот q до вектора v: v' = q ⊗ (0,v) ⊗ q* */
static vec3 quat_rotate(quat q, vec3 v) {
    float tx = 2.0f * (q.y*v.z - q.z*v.y);
    float ty = 2.0f * (q.z*v.x - q.x*v.z);
    float tz = 2.0f * (q.x*v.y - q.y*v.x);
    vec3 r = { v.x + q.w*tx + (q.y*tz - q.z*ty),
               v.y + q.w*ty + (q.z*tx - q.x*tz),
               v.z + q.w*tz + (q.x*ty - q.y*tx) };
    return r;
}
