#include "quaternion.h"

quat_t quat_identity(void) {
    quat_t q = { 1.0f, 0.0f, 0.0f, 0.0f };
    return q;
}

bool quat_is_finite(quat_t q) {
    return isfinite(q.w) && isfinite(q.x) && isfinite(q.y) && isfinite(q.z);
}

float quat_norm(quat_t q) {
    return sqrtf(q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z);
}

quat_t quat_conj(quat_t q) {
    quat_t r = { q.w, -q.x, -q.y, -q.z };
    return r;
}

quat_t quat_mul(quat_t p, quat_t q) {
    quat_t r;
    r.w = p.w * q.w - p.x * q.x - p.y * q.y - p.z * q.z;
    r.x = p.w * q.x + p.x * q.w + p.y * q.z - p.z * q.y;
    r.y = p.w * q.y - p.x * q.z + p.y * q.w + p.z * q.x;
    r.z = p.w * q.z + p.x * q.y - p.y * q.x + p.z * q.w;
    return r;
}

quat_t quat_normalize(quat_t q) {
    float n = quat_norm(q);
    if (!isfinite(n) || n < 1e-9f) return quat_identity();   /* стан загублено — стартуємо з одиничного */
    float k = 1.0f / n;
    quat_t r = { q.w * k, q.x * k, q.y * k, q.z * k };
    return r;
}

quat_t quat_normalize_fast(quat_t q) {
    float sq = q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z;
    if (!isfinite(sq)) return quat_identity();
    /* Ряд Тейлора точний лише поблизу одиниці; далі від неї чесніше заплатити за sqrtf. */
    if (fabsf(sq - 1.0f) > 2.0e-2f) return quat_normalize(q);
    float k = 1.5f - 0.5f * sq;
    quat_t r = { q.w * k, q.x * k, q.y * k, q.z * k };
    return r;
}

quat_t quat_from_axis_angle(vec3_t axis, float angle_rad) {
    vec3_t u;
    if (!vec3_normalize(axis, &u) || !isfinite(angle_rad)) return quat_identity();
    float half = 0.5f * angle_rad;
    float s = sinf(half);
    quat_t r = { cosf(half), u.x * s, u.y * s, u.z * s };
    return r;
}

quat_t quat_from_rotation_vector(vec3_t phi) {
    if (!vec3_is_finite(phi)) return quat_identity();
    float theta = vec3_norm(phi);
    if (theta < 1.0e-7f) {
        /* Малий поворот: sin(θ/2)/θ → 1/2, тригонометрія не потрібна. */
        quat_t r = { 1.0f, 0.5f * phi.x, 0.5f * phi.y, 0.5f * phi.z };
        return quat_normalize_fast(r);
    }
    float half = 0.5f * theta;
    float k = sinf(half) / theta;
    quat_t r = { cosf(half), phi.x * k, phi.y * k, phi.z * k };
    return r;
}

vec3_t quat_rotate(quat_t q, vec3_t v) {
    /* v' = v + 2·q_vec × (q_vec × v + w·v) — 15 множень, без тригонометрії. */
    vec3_t qv = vec3_make(q.x, q.y, q.z);
    vec3_t t = vec3_add(vec3_cross(qv, v), vec3_scale(v, q.w));
    return vec3_add(v, vec3_scale(vec3_cross(qv, t), 2.0f));
}

vec3_t quat_rotate_inv(quat_t q, vec3_t v) {
    return quat_rotate(quat_conj(q), v);
}

quat_t quat_integrate_gyro(quat_t q, vec3_t omega, float dt) {
    if (!quat_is_finite(q) || !vec3_is_finite(omega) || !isfinite(dt)) return quat_identity();
    float h = 0.5f * dt;
    quat_t next;
    next.w = q.w + h * (-q.x * omega.x - q.y * omega.y - q.z * omega.z);
    next.x = q.x + h * ( q.w * omega.x + q.y * omega.z - q.z * omega.y);
    next.y = q.y + h * ( q.w * omega.y - q.x * omega.z + q.z * omega.x);
    next.z = q.z + h * ( q.w * omega.z + q.x * omega.y - q.y * omega.x);
    return quat_normalize_fast(next);
}

mat3_t quat_to_dcm(quat_t q) {
    quat_t n = quat_normalize(q);
    float x = n.x, y = n.y, z = n.z, w = n.w;
    mat3_t r;
    r.m[0][0] = 1.0f - 2.0f * (y * y + z * z);
    r.m[0][1] =        2.0f * (x * y - w * z);
    r.m[0][2] =        2.0f * (x * z + w * y);
    r.m[1][0] =        2.0f * (x * y + w * z);
    r.m[1][1] = 1.0f - 2.0f * (x * x + z * z);
    r.m[1][2] =        2.0f * (y * z - w * x);
    r.m[2][0] =        2.0f * (x * z - w * y);
    r.m[2][1] =        2.0f * (y * z + w * x);
    r.m[2][2] = 1.0f - 2.0f * (x * x + y * y);
    return r;
}

euler_t quat_to_euler(quat_t q) {
    quat_t n = quat_normalize(q);
    euler_t e;
    e.roll = atan2f(2.0f * (n.w * n.x + n.y * n.z),
                    1.0f - 2.0f * (n.x * n.x + n.y * n.y));
    float sinp = 2.0f * (n.w * n.y - n.z * n.x);
    if (sinp >  1.0f) sinp =  1.0f;   /* затиск рятує asinf від NaN на похибці округлення */
    if (sinp < -1.0f) sinp = -1.0f;
    e.pitch = asinf(sinp);
    e.yaw = atan2f(2.0f * (n.w * n.z + n.x * n.y),
                   1.0f - 2.0f * (n.y * n.y + n.z * n.z));
    return e;
}

quat_t quat_from_euler(euler_t e) {
    float cr = cosf(0.5f * e.roll),  sr = sinf(0.5f * e.roll);
    float cp = cosf(0.5f * e.pitch), sp = sinf(0.5f * e.pitch);
    float cy = cosf(0.5f * e.yaw),   sy = sinf(0.5f * e.yaw);
    quat_t q;
    q.w = cy * cp * cr + sy * sp * sr;
    q.x = cy * cp * sr - sy * sp * cr;
    q.y = cy * sp * cr + sy * cp * sr;
    q.z = sy * cp * cr - cy * sp * sr;
    return q;
}

quat_t quat_nlerp(quat_t a, quat_t b, float t) {
    float d = a.w * b.w + a.x * b.x + a.y * b.y + a.z * b.z;
    if (d < 0.0f) { b.w = -b.w; b.x = -b.x; b.y = -b.y; b.z = -b.z; }  /* найкоротший шлях */
    float u = 1.0f - t;
    quat_t r = { u * a.w + t * b.w, u * a.x + t * b.x, u * a.y + t * b.y, u * a.z + t * b.z };
    return quat_normalize(r);
}

quat_t quat_slerp(quat_t a, quat_t b, float t) {
    a = quat_normalize(a);
    b = quat_normalize(b);
    float d = a.w * b.w + a.x * b.x + a.y * b.y + a.z * b.z;
    if (d < 0.0f) {
        b.w = -b.w; b.x = -b.x; b.y = -b.y; b.z = -b.z;
        d = -d;
    }
    if (d > 0.9995f) return quat_nlerp(a, b, t);   /* дуга майже пряма: sin(Ω) → 0 */
    if (d < -1.0f) d = -1.0f;
    float omega = acosf(d);
    float s = sinf(omega);
    float k0 = sinf((1.0f - t) * omega) / s;
    float k1 = sinf(t * omega) / s;
    quat_t r = { k0 * a.w + k1 * b.w, k0 * a.x + k1 * b.x,
                 k0 * a.y + k1 * b.y, k0 * a.z + k1 * b.z };
    return quat_normalize(r);
}

bool euler_rates_from_gyro(euler_t angles, vec3_t omega, euler_t *rates) {
    if (!rates) return false;
    float ct = cosf(angles.pitch);
    if (fabsf(ct) < 1.0e-3f) return false;   /* тангаж біля ±90°: шарнірний замок */
    float sr = sinf(angles.roll), cr = cosf(angles.roll);
    float common = omega.y * sr + omega.z * cr;
    rates->roll  = omega.x + common * (sinf(angles.pitch) / ct);
    rates->pitch = omega.y * cr - omega.z * sr;
    rates->yaw   = common / ct;
    return true;
}
