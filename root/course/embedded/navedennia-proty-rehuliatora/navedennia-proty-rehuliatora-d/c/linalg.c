#include "linalg.h"

#include <math.h>

Vec3 v3(float x, float y, float z) { Vec3 r = { x, y, z }; return r; }

Vec3 v3_add(Vec3 a, Vec3 b) { return v3(a.x + b.x, a.y + b.y, a.z + b.z); }
Vec3 v3_sub(Vec3 a, Vec3 b) { return v3(a.x - b.x, a.y - b.y, a.z - b.z); }
Vec3 v3_scale(Vec3 a, float k) { return v3(a.x * k, a.y * k, a.z * k); }

float v3_dot(Vec3 a, Vec3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }

Vec3 v3_cross(Vec3 a, Vec3 b)
{
    return v3(a.y * b.z - a.z * b.y,
              a.z * b.x - a.x * b.z,
              a.x * b.y - a.y * b.x);
}

float v3_norm(Vec3 a) { return sqrtf(v3_dot(a, a)); }

Vec3 v3_normalized(Vec3 a, Vec3 fallback)
{
    const float n = v3_norm(a);
    if (n < 1e-6f) {
        return fallback;
    }
    return v3_scale(a, 1.0f / n);
}

Vec3 v3_clamp_norm(Vec3 a, float max_norm)
{
    const float n = v3_norm(a);
    if (n <= max_norm || n < 1e-6f) {
        return a;
    }
    return v3_scale(a, max_norm / n);
}

float clampf(float v, float lo, float hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

Quat quat_identity(void) { Quat q = { 1.0f, 0.0f, 0.0f, 0.0f }; return q; }

Quat quat_mul(Quat a, Quat b)
{
    Quat r;
    r.w = a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z;
    r.x = a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y;
    r.y = a.w * b.y - a.x * b.z + a.y * b.w + a.z * b.x;
    r.z = a.w * b.z + a.x * b.y - a.y * b.x + a.z * b.w;
    return r;
}

Quat quat_conj(Quat q)
{
    Quat r = { q.w, -q.x, -q.y, -q.z };
    return r;
}

Quat quat_normalized(Quat q)
{
    const float n = sqrtf(q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z);
    if (n < 1e-6f) {
        return quat_identity();
    }
    const float k = 1.0f / n;
    Quat r = { q.w * k, q.x * k, q.y * k, q.z * k };
    return r;
}

Vec3 quat_rotate(Quat q, Vec3 v)
{
    /* Формула Родріга у кватерніонній формі: без побудови матриці 3x3. */
    const Vec3 u = v3(q.x, q.y, q.z);
    const Vec3 t = v3_scale(v3_cross(u, v), 2.0f);
    return v3_add(v3_add(v, v3_scale(t, q.w)), v3_cross(u, t));
}

Quat quat_from_basis(Vec3 xb, Vec3 yb, Vec3 zb)
{
    /* Стовпці матриці повороту body->NED. Метод Шеппарда: обираємо гілку з
       найбільшим знаменником, інакше на кутах близько 180 гр. втрачаємо точність. */
    const float r00 = xb.x, r01 = yb.x, r02 = zb.x;
    const float r10 = xb.y, r11 = yb.y, r12 = zb.y;
    const float r20 = xb.z, r21 = yb.z, r22 = zb.z;

    const float trace = r00 + r11 + r22;
    Quat q;

    if (trace > 0.0f) {
        const float s = sqrtf(trace + 1.0f) * 2.0f;
        q.w = 0.25f * s;
        q.x = (r21 - r12) / s;
        q.y = (r02 - r20) / s;
        q.z = (r10 - r01) / s;
    } else if (r00 > r11 && r00 > r22) {
        const float s = sqrtf(1.0f + r00 - r11 - r22) * 2.0f;
        q.w = (r21 - r12) / s;
        q.x = 0.25f * s;
        q.y = (r01 + r10) / s;
        q.z = (r02 + r20) / s;
    } else if (r11 > r22) {
        const float s = sqrtf(1.0f + r11 - r00 - r22) * 2.0f;
        q.w = (r02 - r20) / s;
        q.x = (r01 + r10) / s;
        q.y = 0.25f * s;
        q.z = (r12 + r21) / s;
    } else {
        const float s = sqrtf(1.0f + r22 - r00 - r11) * 2.0f;
        q.w = (r10 - r01) / s;
        q.x = (r02 + r20) / s;
        q.y = (r12 + r21) / s;
        q.z = 0.25f * s;
    }
    return quat_normalized(q);
}

Quat quat_from_axis_angle(Vec3 axis_unit, float angle_rad)
{
    const float half = angle_rad * 0.5f;
    const float s = sinf(half);
    Quat q = { cosf(half), axis_unit.x * s, axis_unit.y * s, axis_unit.z * s };
    return q;
}

Quat quat_slew(Quat from, Quat to, float max_angle, Vec3 *out_rotvec)
{
    Quat d = quat_mul(quat_conj(from), to);   /* дельта у зв'язаній системі from */

    /* Найкоротший шлях на 4-сфері: q і -q — той самий поворот. */
    if (d.w < 0.0f) {
        d.w = -d.w; d.x = -d.x; d.y = -d.y; d.z = -d.z;
    }

    const float vnorm = sqrtf(d.x * d.x + d.y * d.y + d.z * d.z);
    if (vnorm < 1e-7f) {                      /* уставка не зрушила */
        *out_rotvec = v3(0.0f, 0.0f, 0.0f);
        return quat_normalized(to);
    }

    const Vec3 axis = v3_scale(v3(d.x, d.y, d.z), 1.0f / vnorm);
    const float angle = 2.0f * atan2f(vnorm, clampf(d.w, -1.0f, 1.0f));

    if (angle <= max_angle) {                 /* стрибок у межах — пропускаємо як є */
        *out_rotvec = v3_scale(axis, angle);
        return quat_normalized(to);
    }

    /* Сходинку ріжемо: за такт повертаємо уставку рівно на max_angle. */
    *out_rotvec = v3_scale(axis, max_angle);
    return quat_normalized(quat_mul(from, quat_from_axis_angle(axis, max_angle)));
}
