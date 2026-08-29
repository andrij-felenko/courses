#include "guards.h"

#include <math.h>
#include <stdio.h>

#include "fm_time.h"
#include "mission.h"
#include "report.h"

fm_deny_t fm_guard_imu(const fm_state_t *s)
{
    if (!s || !s->gyro_healthy) {
        return FM_DENY_IMU;
    }
    return FM_ALLOW;
}

fm_deny_t fm_guard_attitude(const fm_state_t *s)
{
    const fm_deny_t imu = fm_guard_imu(s);

    if (imu != FM_ALLOW) {
        return imu;
    }
    if (!s->accel_healthy || !s->attitude_valid) {
        return FM_DENY_ATTITUDE;
    }
    return FM_ALLOW;
}

fm_deny_t fm_guard_altitude(const fm_state_t *s, const fm_params_t *p)
{
    const fm_deny_t att = fm_guard_attitude(s);

    if (att != FM_ALLOW) {
        return att;
    }
    (void)p;
    /* Вертикальний контур живиться баро АБО далекоміром: втрата одного джерела
       ще не позбавляє автомат висоти, втрата обох — позбавляє. */
    if (!s->baro_healthy && !s->rangefinder_healthy) {
        return FM_DENY_ALT_ESTIMATE;
    }
    if (!s->ekf_vert_pos_valid) {
        return FM_DENY_ALT_ESTIMATE;
    }
    if (isnan(s->altitude_rel_m) || isnan(s->vertical_velocity)) {
        return FM_DENY_ALT_ESTIMATE;
    }
    return FM_ALLOW;
}

fm_deny_t fm_guard_position(const fm_state_t *s, const fm_params_t *p)
{
    const fm_deny_t alt = fm_guard_altitude(s, p);

    if (alt != FM_ALLOW) {
        return alt;
    }
    if (!p) {
        return FM_DENY_INVALID_MODE;
    }

    /* 1. Формальний супутниковий фікс. */
    if (s->gnss_fix_type < p->gnss_min_fix_type || s->gnss_sats < p->gnss_min_sats) {
        return FM_DENY_NO_GNSS_FIX;
    }

    /* 2. Геометрія сузірʼя: шість супутників, зібраних в одному секторі неба,
          дають координату з похибкою в десятки метрів. */
    if (isnan(s->gnss_hdop) || isnan(s->gnss_vdop) ||
        s->gnss_hdop > p->gnss_max_hdop || s->gnss_vdop > p->gnss_max_vdop) {
        return FM_DENY_BAD_DOP;
    }

    /* 3. Сходження оцінок фільтра. Інновація понад одиницю означає, що
          інерціальний прогноз і супутниковий вимір суперечать одне одному;
          такий перехід блокується безумовно й окремою причиною. */
    if (isnan(s->ekf_innov_pos_norm) || isnan(s->ekf_innov_vel_norm)) {
        return FM_DENY_EKF_GLITCH;
    }
    if (s->ekf_innov_pos_norm >= p->ekf_glitch_innov ||
        s->ekf_innov_vel_norm >= p->ekf_glitch_innov) {
        return FM_DENY_EKF_GLITCH;
    }
    if (!s->ekf_horiz_pos_valid ||
        s->ekf_innov_pos_norm > p->ekf_max_innov_pos ||
        s->ekf_innov_vel_norm > p->ekf_max_innov_vel) {
        return FM_DENY_EKF_INNOVATION;
    }

    /* 4. Курс. Без нього вектор зміщення в системі Північ-Схід не перекладеться
          в систему координат апарата, і дрон компенсуватиме знос не туди. */
    if (!s->compass_healthy || isnan(s->compass_yaw_error_deg) ||
        fabsf(s->compass_yaw_error_deg) > p->compass_max_yaw_err_deg) {
        return FM_DENY_COMPASS;
    }

    return FM_ALLOW;
}

fm_deny_t fm_guard_guided(const fm_state_t *s, const fm_params_t *p)
{
    const fm_deny_t pos = fm_guard_position(s, p);

    if (pos != FM_ALLOW) {
        return pos;
    }
    /* Живе джерело цілевказівок: мовчазний супровідний компʼютер перетворює
       Guided на політ у нікуди за останньою відомою точкою. */
    if (fm_age_ms(s->now_ms, s->guided_setpoint_ms) > p->guided_timeout_ms) {
        return FM_DENY_GUIDED_LINK;
    }
    return FM_ALLOW;
}

fm_deny_t fm_guard_auto(const fm_state_t *s, const fm_params_t *p)
{
    const fm_deny_t pos = fm_guard_position(s, p);

    if (pos != FM_ALLOW) {
        return pos;
    }
    if (!s->home_set) {
        return FM_DENY_NO_HOME;
    }
    if (!s->mission || s->mission->count == 0) {
        return FM_DENY_NO_MISSION;
    }

    const fm_mission_status_t st = fm_mission_validate(s->mission,
                                                       s->home_lat_1e7, s->home_lon_1e7,
                                                       p->fence_radius_m, p->mission_max_alt_m);
    if (st == FM_MISSION_EMPTY) {
        return FM_DENY_NO_MISSION;
    }
    if (st != FM_MISSION_OK) {
        return FM_DENY_BAD_MISSION;
    }
    return FM_ALLOW;
}

fm_deny_t fm_guard_rtl(const fm_state_t *s, const fm_params_t *p)
{
    const fm_deny_t alt = fm_guard_altitude(s, p);

    if (alt != FM_ALLOW) {
        return alt;
    }
    /* Повертатися нема куди — це не «спробуємо якось»: без точки старту автомат
       перенаправляє запит у Land, і рішення це ухвалює викликач. */
    if (!s->home_set) {
        return FM_DENY_NO_HOME;
    }
    if (!s->ekf_horiz_pos_valid) {
        return FM_DENY_EKF_INNOVATION;
    }
    return FM_ALLOW;
}

fm_deny_t fm_guard_check(fm_mode_t target, const fm_state_t *s, const fm_params_t *p)
{
    if (!s || !p) {
        return FM_DENY_INVALID_MODE;
    }

    switch (target) {
    case FM_MODE_MANUAL:
        return fm_guard_imu(s);

    case FM_MODE_STABILIZE:
        return fm_guard_attitude(s);

    case FM_MODE_ALT_HOLD:
        return fm_guard_altitude(s, p);

    case FM_MODE_POS_HOLD:
        return fm_guard_position(s, p);

    case FM_MODE_GUIDED:
        return fm_guard_guided(s, p);

    case FM_MODE_AUTO:
        return fm_guard_auto(s, p);

    case FM_MODE_RTL:
        return fm_guard_rtl(s, p);

    case FM_MODE_LAND:
        /* Посадка вимагає вертикальної оцінки; без неї лишається аварійний
           спуск на самих кутах і фіксованій тязі. */
        return fm_guard_altitude(s, p);

    case FM_MODE_EMERGENCY_LAND:
        return fm_guard_attitude(s);

    case FM_MODE_TERMINATE:
        /* Відсічка мусить спрацювати за будь-якого стану сенсорів. */
        return FM_ALLOW;

    case FM_MODE_COUNT:
    default:
        /* Вичерпність переходів: невідомий код режиму дістає відмову, а не
           мовчазне «нічого не сталося». */
        return FM_DENY_INVALID_MODE;
    }
}

static const char *deny_phrase(fm_deny_t deny)
{
    switch (deny) {
    case FM_ALLOW:                   return "accepted";
    case FM_DENY_INVALID_MODE:       return "unknown mode id";
    case FM_DENY_IMU:                return "requires healthy gyro";
    case FM_DENY_ATTITUDE:           return "requires attitude estimate";
    case FM_DENY_ALT_ESTIMATE:       return "requires altitude estimate";
    case FM_DENY_NO_GNSS_FIX:        return "requires 3D Fix & HDOP < 1.5";
    case FM_DENY_BAD_DOP:            return "requires 3D Fix & HDOP < 1.5";
    case FM_DENY_EKF_INNOVATION:     return "requires EKF innovations in gate";
    case FM_DENY_EKF_GLITCH:         return "blocked by EKF variance glitch";
    case FM_DENY_COMPASS:            return "requires healthy compass heading";
    case FM_DENY_GUARD_UNSTABLE:     return "guard not stable yet";
    case FM_DENY_NO_MISSION:         return "requires loaded mission";
    case FM_DENY_BAD_MISSION:        return "mission failed validation";
    case FM_DENY_NO_HOME:            return "requires Home position";
    case FM_DENY_GUIDED_LINK:        return "requires live setpoint stream";
    case FM_DENY_THROTTLE_MISMATCH:  return "match throttle stick first";
    case FM_DENY_FAILSAFE_LOCK:      return "blocked by active failsafe";
    case FM_DENY_IN_AIR:             return "not allowed while airborne";
    default:                         return "denied";
    }
}

void fm_deny_text(fm_mode_t target, fm_deny_t deny, char *buf, size_t n)
{
    if (!buf || n == 0) {
        return;
    }
    /* snprintf сам обріже рядок під довжину поля STATUSTEXT і завершить нулем;
       повернене значення тут не потрібне — обрізання є штатним випадком. */
    (void)snprintf(buf, n, "Mode change failed: %s %s",
                   fm_mode_name(target), deny_phrase(deny));
}

uint8_t fm_deny_mav_result(fm_deny_t deny)
{
    switch (deny) {
    case FM_ALLOW:
        return MAV_RESULT_ACCEPTED;

    case FM_DENY_INVALID_MODE:
        return MAV_RESULT_UNSUPPORTED;

    /* Перешкода минуща: зведи стік, дочекайся витримки, поверни потік точок —
       і той самий запит пройде. Станція має право повторити. */
    case FM_DENY_THROTTLE_MISMATCH:
    case FM_DENY_GUARD_UNSTABLE:
    case FM_DENY_GUIDED_LINK:
    case FM_DENY_EKF_INNOVATION:
    case FM_DENY_BAD_DOP:
        return MAV_RESULT_TEMPORARILY_REJECTED;

    default:
        return MAV_RESULT_DENIED;
    }
}
