#include "controllers.h"

#include <math.h>

#include "mission.h"

/* Коефіцієнти контурів. Числа тут — робочі значення для середнього квадрокоптера
   класу 450 мм; на іншій рамі їх переналаштовують, але структура каскаду —
   позиція → швидкість → кут, висота → вертикальна швидкість → тяга — не міняється. */
#define FM_ALT_P        1.00f   /* м/с на метр помилки висоти                   */
#define FM_VZ_MAX       2.50f   /* межа вертикальної швидкості, м/с             */
#define FM_VZ_P         0.25f   /* частка тяги на м/с помилки                   */
#define FM_VZ_I         0.08f   /* те саме за секунду                           */
#define FM_POS_P        0.90f   /* м/с на метр помилки положення                */
#define FM_VEL_MAX      5.00f   /* межа горизонтальної швидкості, м/с           */
#define FM_VEL_P        4.00f   /* градусів нахилу на м/с помилки               */
#define FM_VEL_I        0.80f   /* те саме за секунду                           */
#define FM_TILT_MAX    35.00f   /* межа кута нахилу, градуси                    */
#define FM_STICK_DEAD   0.10f   /* мертва зона стіків крену й тангажу           */
#define FM_THR_DEAD     0.10f   /* півширина мертвої зони ручки газу            */

static float clampf(float v, float lo, float hi)
{
    if (isnan(v)) {
        return lo;
    }
    return (v < lo) ? lo : ((v > hi) ? hi : v);
}

void fm_ctl_init(fm_controllers_t *c, const fm_state_t *s)
{
    if (!c) {
        return;
    }
    c->alt_engaged    = false;
    c->alt_target_m   = s ? s->altitude_rel_m : 0.0f;
    c->vz_integrator  = s ? s->hover_throttle : 0.5f;
    c->pos_engaged    = false;
    c->pos_latched    = false;
    c->target_lat_1e7 = s ? s->lat_1e7 : 0;
    c->target_lon_1e7 = s ? s->lon_1e7 : 0;
    c->vel_int_north  = 0.0f;
    c->vel_int_east   = 0.0f;
    c->tilt_north_deg = 0.0f;
    c->tilt_east_deg  = 0.0f;
    c->output         = s ? s->motor_output : 0.0f;
    fm_slew_reset(&c->throttle_slew, c->output);
}

void fm_ctl_enter_mode(fm_controllers_t *c, fm_mode_t mode,
                       const fm_state_t *s, const fm_params_t *p)
{
    if (!c || !s || !p) {
        return;
    }

    c->alt_engaged = fm_mode_auto_throttle(mode);
    c->pos_engaged = fm_mode_needs_position(mode);

    /* 1. Фіксація уставок: ціль дорівнює тому, що є ЗАРАЗ, у ту саму
          мілісекунду перемикання. Інакше регулятор побачить помилку, якої
          насправді немає, і відпрацює її повним ходом. */
    c->alt_target_m   = s->altitude_rel_m;
    c->target_lat_1e7 = s->lat_1e7;
    c->target_lon_1e7 = s->lon_1e7;
    c->pos_latched    = c->pos_engaged;

    /* 2. Передустановка інтегратора: вертикальний канал стартує з тієї тяги,
          яку мотори вже дають, а не з нуля. Саме цей рядок відділяє плавний
          перехід від просідання на метр-другий. */
    if (c->alt_engaged) {
        const float hover = (s->hover_throttle > 0.05f) ? s->hover_throttle : 0.5f;
        c->vz_integrator = clampf((s->motor_output > 0.05f) ? s->motor_output : hover,
                                  0.0f, 1.0f);
    } else {
        c->vz_integrator = s->stick_throttle;
    }

    /* 3. Інтегратори горизонталі стартують з поточної команди нахилу — апарат
          уже летить із якимось креном, і обнуляти його ривком не можна. */
    c->vel_int_north = clampf(c->tilt_north_deg, -FM_TILT_MAX, FM_TILT_MAX);
    c->vel_int_east  = clampf(c->tilt_east_deg, -FM_TILT_MAX, FM_TILT_MAX);

    if (mode == FM_MODE_RTL && s->home_set) {
        /* Повернення: спершу набір безпечної висоти, ціль по горизонталі —
           точка старту. Висоту не знижуємо ніколи, лише піднімаємо. */
        c->target_lat_1e7 = s->home_lat_1e7;
        c->target_lon_1e7 = s->home_lon_1e7;
        c->alt_target_m   = (s->altitude_rel_m > p->rtl_alt_m) ? s->altitude_rel_m
                                                               : p->rtl_alt_m;
        c->pos_latched    = true;
    }

    if (mode == FM_MODE_AUTO && s->mission && s->mission->count > 0) {
        /* Перша точка плану; далі точки подає навігатор місії через
           fm_ctl_set_position_target(). */
        c->target_lat_1e7 = s->mission->items[0].lat_1e7;
        c->target_lon_1e7 = s->mission->items[0].lon_1e7;
        c->alt_target_m   = s->mission->items[0].alt_rel_m;
        c->pos_latched    = true;
    }

    /* 4. Обмежувач наростання починає рахувати від фактичного виходу. */
    fm_slew_reset(&c->throttle_slew, s->motor_output);
    c->output = s->motor_output;
}

void fm_ctl_set_position_target(fm_controllers_t *c, fm_mode_t mode,
                                int32_t lat_1e7, int32_t lon_1e7, float alt_rel_m)
{
    if (!c) {
        return;
    }
    if (mode != FM_MODE_GUIDED && mode != FM_MODE_AUTO) {
        return;   /* поза автономними режимами зовнішня точка нічого не означає */
    }
    c->target_lat_1e7 = lat_1e7;
    c->target_lon_1e7 = lon_1e7;
    if (!isnan(alt_rel_m) && alt_rel_m > 0.0f) {
        c->alt_target_m = alt_rel_m;
    }
    c->pos_latched = true;
}

/* Вертикальна швидкість, якої просить пілот ручкою газу в режимах з
   автоматичною тягою: центральна мертва зона — утримання висоти. */
static float stick_climb_rate(const fm_state_t *s)
{
    const float centered = s->stick_throttle - 0.5f;

    if (fabsf(centered) <= FM_THR_DEAD) {
        return 0.0f;
    }
    const float span = 0.5f - FM_THR_DEAD;
    const float rate = (centered - ((centered > 0.0f) ? FM_THR_DEAD : -FM_THR_DEAD)) / span;

    return clampf(rate, -1.0f, 1.0f) * FM_VZ_MAX;
}

/* Внутрішній контур: вертикальна швидкість -> частка тяги, з інтегратором і
   захистом від його розкручування на упорі. */
static float vertical_loop(fm_controllers_t *c, float vz_setpoint,
                           const fm_state_t *s, float dt_s)
{
    const float err = vz_setpoint - s->vertical_velocity;
    const float unclamped = c->vz_integrator + FM_VZ_P * err;

    if (unclamped > 0.0f && unclamped < 1.0f) {
        /* Інтегруємо лише поки вихід не вперся в межу — інакше інтегратор
           накопичить те, чого мотори однаково не віддадуть. */
        c->vz_integrator = clampf(c->vz_integrator + FM_VZ_I * err * dt_s, 0.0f, 1.0f);
    }
    return clampf(c->vz_integrator + FM_VZ_P * err, 0.0f, 1.0f);
}

/* Каскад горизонталі: помилка положення -> уставка швидкості -> кут нахилу. */
static void horizontal_loop(fm_controllers_t *c, const fm_state_t *s, float dt_s)
{
    float vel_sp_north = 0.0f;
    float vel_sp_east  = 0.0f;

    const bool sticks_moved = fabsf(s->stick_pitch) > FM_STICK_DEAD ||
                              fabsf(s->stick_roll)  > FM_STICK_DEAD;

    if (sticks_moved) {
        /* Пілот веде апарат: стіки задають вектор швидкості, ціль по координатах
           поки не має сенсу й буде зафіксована в мить, коли стіки стануть. */
        vel_sp_north   = clampf(s->stick_pitch, -1.0f, 1.0f) * FM_VEL_MAX;
        vel_sp_east    = clampf(s->stick_roll, -1.0f, 1.0f) * FM_VEL_MAX;
        c->pos_latched = false;
    } else {
        if (!c->pos_latched) {
            c->target_lat_1e7 = s->lat_1e7;
            c->target_lon_1e7 = s->lon_1e7;
            c->pos_latched    = true;
        }

        float err_north = 0.0f;
        float err_east  = 0.0f;

        fm_geo_offset_m(s->lat_1e7, s->lon_1e7, c->target_lat_1e7, c->target_lon_1e7,
                        &err_north, &err_east);
        vel_sp_north = clampf(err_north * FM_POS_P, -FM_VEL_MAX, FM_VEL_MAX);
        vel_sp_east  = clampf(err_east * FM_POS_P, -FM_VEL_MAX, FM_VEL_MAX);
    }

    const float err_vn = vel_sp_north - s->vel_north_ms;
    const float err_ve = vel_sp_east - s->vel_east_ms;

    const float raw_north = c->vel_int_north + FM_VEL_P * err_vn;
    const float raw_east  = c->vel_int_east + FM_VEL_P * err_ve;

    if (fabsf(raw_north) < FM_TILT_MAX) {
        c->vel_int_north = clampf(c->vel_int_north + FM_VEL_I * err_vn * dt_s,
                                  -FM_TILT_MAX, FM_TILT_MAX);
    }
    if (fabsf(raw_east) < FM_TILT_MAX) {
        c->vel_int_east = clampf(c->vel_int_east + FM_VEL_I * err_ve * dt_s,
                                 -FM_TILT_MAX, FM_TILT_MAX);
    }

    c->tilt_north_deg = clampf(c->vel_int_north + FM_VEL_P * err_vn, -FM_TILT_MAX, FM_TILT_MAX);
    c->tilt_east_deg  = clampf(c->vel_int_east + FM_VEL_P * err_ve, -FM_TILT_MAX, FM_TILT_MAX);
}

float fm_ctl_step(fm_controllers_t *c, fm_mode_t mode, const fm_state_t *s,
                  const fm_params_t *p, const fm_land_detector_t *land, float dt_s)
{
    if (!c || !s || !p) {
        return 0.0f;
    }
    if (dt_s <= 0.0f) {
        dt_s = 0.01f;   /* такт 100 Гц як запобіжник від нульового кроку */
    }

    float command = 0.0f;

    if (mode == FM_MODE_TERMINATE) {
        /* Відсічка: жодного інтегрування, жодного плавного зведення. */
        c->alt_engaged = false;
        c->pos_engaged = false;
        c->vz_integrator = 0.0f;
        c->tilt_north_deg = 0.0f;
        c->tilt_east_deg  = 0.0f;
        fm_slew_reset(&c->throttle_slew, 0.0f);
        c->output = 0.0f;
        return c->output;
    }

    if (fm_mode_manual_throttle(mode)) {
        c->alt_engaged = false;
        c->pos_engaged = false;
        c->tilt_north_deg = 0.0f;
        c->tilt_east_deg  = 0.0f;
        command = clampf(s->stick_throttle, 0.0f, 1.0f);
    } else if (land && fm_land_is_landed(land)) {
        /* Посадку підтверджено: мотори на холостому ходу до роззброєння. */
        command = p->land_idle_throttle;
        c->vz_integrator = command;
    } else {
        float vz_setpoint;

        if (mode == FM_MODE_LAND || mode == FM_MODE_EMERGENCY_LAND) {
            vz_setpoint = land ? fm_land_target_vz(land, p) : -p->land_speed;
        } else {
            const float stick_vz = stick_climb_rate(s);

            if (fabsf(stick_vz) > 0.0f) {
                /* Поки пілот тримає ручку поза мертвою зоною, цільова висота
                   їде за поточною — щоб на відпусканні зафіксуватися тут. */
                c->alt_target_m = s->altitude_rel_m;
                vz_setpoint     = stick_vz;
            } else {
                vz_setpoint = clampf((c->alt_target_m - s->altitude_rel_m) * FM_ALT_P,
                                     -FM_VZ_MAX, FM_VZ_MAX);
            }
        }

        command = vertical_loop(c, vz_setpoint, s, dt_s);

        if (fm_mode_needs_position(mode)) {
            c->pos_engaged = true;
            horizontal_loop(c, s, dt_s);
        } else {
            c->pos_engaged    = false;
            c->tilt_north_deg = 0.0f;
            c->tilt_east_deg  = 0.0f;
        }
    }

    /* Обмежувач наростання стоїть ПІСЛЯ всіх контурів: він прибирає східчасті
       стрибки навіть тоді, коли перехід уже пройшов усі охоронці. */
    c->output = fm_slew_step(&c->throttle_slew, clampf(command, 0.0f, 1.0f),
                             dt_s, p->throttle_slew_per_s);
    return c->output;
}
