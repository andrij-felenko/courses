#ifndef LINALG_H
#define LINALG_H

/* Мінімальна лінійна алгебра бортового стеку: вектор і кватерніон.
   Усе на float — саме так рахує FPU одинарної точності Cortex-M4F/M7. */

typedef struct { float x, y, z; } Vec3;
typedef struct { float w, x, y, z; } Quat;

Vec3  v3(float x, float y, float z);
Vec3  v3_add(Vec3 a, Vec3 b);
Vec3  v3_sub(Vec3 a, Vec3 b);
Vec3  v3_scale(Vec3 a, float k);
float v3_dot(Vec3 a, Vec3 b);
Vec3  v3_cross(Vec3 a, Vec3 b);
float v3_norm(Vec3 a);
/* Нормалізація з явним запасним значенням: нульового вектора не буває "трохи". */
Vec3  v3_normalized(Vec3 a, Vec3 fallback);
/* Обмеження ДОВЖИНИ вектора зі збереженням напрямку (не покомпонентне!). */
Vec3  v3_clamp_norm(Vec3 a, float max_norm);

Quat quat_identity(void);
Quat quat_mul(Quat a, Quat b);
Quat quat_conj(Quat q);
Quat quat_normalized(Quat q);
/* Поворот вектора зі зв'язаної системи в навігаційну: v_ned = q * v_body * q^-1. */
Vec3 quat_rotate(Quat q, Vec3 v);
/* Кватерніон з ортонормованого тригранника (стовпці матриці повороту body→NED). */
Quat quat_from_basis(Vec3 xb, Vec3 yb, Vec3 zb);
Quat quat_from_axis_angle(Vec3 axis_unit, float angle_rad);

/* Обмежувач швидкості зміни уставки (Slew Rate Limiter).
   Повертає кватерніон, повернутий від from до to не більше ніж на max_angle,
   а в out_rotvec кладе ФАКТИЧНО застосований вектор повороту (вісь * кут)
   у зв'язаній системі from — з нього виходить прямий зв'язок за швидкістю. */
Quat quat_slew(Quat from, Quat to, float max_angle, Vec3 *out_rotvec);

float clampf(float v, float lo, float hi);

#endif /* LINALG_H */
