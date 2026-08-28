#include <math.h>

typedef struct { float w, x, y, z; } quat;
typedef struct { float x, y, z; } vec3;

/* множення кватерніонів: r = a ⊗ b (складання поворотів) */
static quat quat_mul(quat a, quat b) {
    quat r;
    r.w = a.w*b.w - a.x*b.x - a.y*b.y - a.z*b.z;
    r.x = a.w*b.x + a.x*b.w + a.y*b.z - a.z*b.y;
    r.y = a.w*b.y - a.x*b.z + a.y*b.w + a.z*b.x;
    r.z = a.w*b.z + a.x*b.y - a.y*b.x + a.z*b.w;
    return r;
}

/* нормування: повертає q на сферу одиничних кватерніонів (|q| = 1) */
static quat quat_normalize(quat q) {
    float n = sqrtf(q.w*q.w + q.x*q.x + q.y*q.y + q.z*q.z);
    if (n < 1e-9f) { quat id = {1,0,0,0}; return id; }  /* захист від ділення на 0 */
    float inv = 1.0f / n;
    q.w *= inv; q.x *= inv; q.y *= inv; q.z *= inv;
    return q;
}
