#include "guidance.h"

#include <math.h>

/* --- Межі й коефіцієнти зовнішнього контуру ------------------------------- */
#define GRAVITY_MSS     9.80665f
#define A_MAX_THRUST    (2.0f * GRAVITY_MSS)  /* тягоозброєність 2:1 */

#define KP_POS          1.0f     /* похибка позиції -> уставка швидкості */
#define V_MAX           5.0f     /* м/с */
#define KP_VEL          2.2f
#define KI_VEL          0.7f
#define I_MAX           3.0f     /* стеля інтегратора, м/с^2 */
#define A_MAX_XY        6.0f
#define A_MAX_Z         5.0f

#define MAX_TILT_RAD    0.610865f   /* 35 градусів */
#define OMEGA_MAX       3.14159f    /* 180 град/с — межа обертання уставки */
#define THRUST_MIN      0.05f

void guidance_init(Guidance *g)
{
    g->vel_integral = v3(0.0f, 0.0f, 0.0f);
    g->q_prev = quat_identity();
    g->primed = false;
}

/* Обмежувач кута нахилу: вісь тяги не відхиляється від вертикалі далі tilt_max.
   Саме тут ми відмовляємося виконувати наказ наведення заради підйомної сили. */
static Vec3 apply_tilt_limit(Vec3 zb)
{
    const float cos_max = cosf(MAX_TILT_RAD);
    if (zb.z >= cos_max) {
        return zb;
    }

    const float xy = sqrtf(zb.x * zb.x + zb.y * zb.y);
    if (xy < 1e-4f) {
        /* Вироджений випадок: потрібна сила спрямована ВНИЗ (наприклад, наведення
           просить прискорення до землі, більшого за g). Мультиротор так не вміє —
           тримаємо горизонт і віддаємо мінімальну тягу. */
        return v3(0.0f, 0.0f, 1.0f);
    }

    const float k = sinf(MAX_TILT_RAD) / xy;
    return v3(zb.x * k, zb.y * k, cos_max);
}

/* Ортонормований тригранник із бажаної осі тяги та курсу — і кватерніон із нього. */
static Quat basis_to_quat(Vec3 zb, float yaw_rad)
{
    Vec3 x_c = v3(cosf(yaw_rad), sinf(yaw_rad), 0.0f);   /* напрямок носа в NED */
    Vec3 yb = v3_cross(zb, x_c);
    float yn = v3_norm(yb);

    if (yn < 1e-4f) {
        /* Ніс збігся з віссю тяги (можливо лише за межами tilt-ліміту) —
           беремо перпендикулярний опорний напрямок, щоб базис не розвалився. */
        x_c = v3(-sinf(yaw_rad), cosf(yaw_rad), 0.0f);
        yb = v3_cross(zb, x_c);
        yn = v3_norm(yb);
        if (yn < 1e-4f) {
            return quat_identity();
        }
    }

    yb = v3_scale(yb, 1.0f / yn);
    const Vec3 xb = v3_cross(yb, zb);
    return quat_from_basis(xb, yb, zb);
}

Setpoint guidance_step(Guidance *g,
                       const NavState *nav,
                       Vec3 target_pos_ned,
                       float yaw_sp_rad,
                       float dt,
                       bool actuators_saturated,
                       uint64_t now_us)
{
    Setpoint sp;

    /* 1. Позиція -> швидкість. Обмежуємо ДОВЖИНУ вектора, а не осі окремо:
          інакше по діагоналі апарат летів би в 1.41 раза швидше за дозволене. */
    const Vec3 e_pos = v3_sub(target_pos_ned, nav->pos_ned);
    const Vec3 vel_sp = v3_clamp_norm(v3_scale(e_pos, KP_POS), V_MAX);

    /* 2. Швидкість -> прискорення, PI з анти-вінд-апом. */
    const Vec3 e_vel = v3_sub(vel_sp, nav->vel_ned);

    if (!actuators_saturated) {
        g->vel_integral = v3_add(g->vel_integral, v3_scale(e_vel, KI_VEL * dt));
        g->vel_integral = v3_clamp_norm(g->vel_integral, I_MAX);
    }
    /* Інакше — інтегратор ЗАМОРОЖЕНО. Мотори вже на стелі, накопичувати похибку
       нема куди: після стихання вітру апарат перелетів би ціль на десятки метрів. */

    Vec3 a_des = v3_add(v3_scale(e_vel, KP_VEL), g->vel_integral);

    Vec3 a_xy = v3_clamp_norm(v3(a_des.x, a_des.y, 0.0f), A_MAX_XY);
    a_des = v3(a_xy.x, a_xy.y, clampf(a_des.z, -A_MAX_Z, A_MAX_Z));

    /* 3. Питома сила: f = a_des - g. У NED вісь Z вниз, тож у висінні
          f = (0, 0, -9.81) — сила спрямована вгору. */
    const Vec3 f_des = v3(a_des.x, a_des.y, a_des.z - GRAVITY_MSS);

    /* 4. Бажана вісь Z корпуса (вниз крізь дно): z_body = -f / ||f||. */
    Vec3 zb = v3_normalized(v3_scale(f_des, -1.0f), v3(0.0f, 0.0f, 1.0f));
    zb = apply_tilt_limit(zb);

    /* 5. Тригранник -> цільовий кватерніон. */
    const Quat q_raw = basis_to_quat(zb, yaw_sp_rad);

    /* 6. Обмежувач швидкості зміни уставки. Перемикання вейпойнта під 90 градусів
          дає сходинку в цілі; без різання вона б'є в D-ланку регулятора орієнтації. */
    Vec3 rotvec = v3(0.0f, 0.0f, 0.0f);
    if (!g->primed) {
        g->q_prev = q_raw;
        g->primed = true;
        sp.q_target = q_raw;
    } else {
        sp.q_target = quat_slew(g->q_prev, q_raw, OMEGA_MAX * dt, &rotvec);
        g->q_prev = sp.q_target;
    }

    /* Фактичний поворот уставки за такт — це і є прямий зв'язок за швидкістю:
       регулятор дізнається, куди уставка вже їде, не чекаючи появи похибки. */
    sp.rate_ff = (dt > 1e-6f) ? v3_scale(rotvec, 1.0f / dt) : v3(0.0f, 0.0f, 0.0f);

    /* 7. Колективна тяга. Ділення на zb.z — це і є компенсація 1/cos(theta):
          при нахилі 30 гр. вертикальна складова падає до 0.866, і рівно на стільки
          ж піднімається уставка газу, інакше апарат просідає на маневрі.
          Поки обмежувач нахилу не втрутився, це тотожно ||f_des||. */
    float f_up = -f_des.z;
    if (f_up < 0.5f) {
        f_up = 0.5f;               /* від'ємної тяги гвинт фіксованого кроку не дає */
    }
    const float thrust_mag = f_up / zb.z;      /* zb.z >= cos(35 гр.) > 0 гарантовано */
    sp.thrust = clampf(thrust_mag / A_MAX_THRUST, THRUST_MIN, 1.0f);

    sp.stamp_us = now_us;
    return sp;
}
