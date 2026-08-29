/* ==========================================================================
 *  mag_cal_telemetry.c — пакування кадрів MAVLink
 *
 *  Використовується стандартна згенерована бібліотека C (mavlink v2,
 *  діалект common). Каталог заголовків підключається до збірки як
 *  -Imodules/mavlink/generated.
 * ========================================================================== */

#include <common/mavlink.h>

#include "mag_cal_telemetry.h"

/* Не частіше 5 Гц: MAG_CAL_PROGRESS — це 27 байтів корисних даних плюс
 * кадр, і на радіоканалі 57 600 бод він конкурує з потоком положення. */
#define MAG_CAL_PROGRESS_PERIOD_MS 200u

void mag_cal_telemetry_init(mag_cal_telemetry_t *tm, uint8_t system_id,
                            uint8_t component_id, uint8_t compass_id) {
    tm->system_id        = system_id;
    tm->component_id     = component_id;
    tm->compass_id       = compass_id;
    tm->attempt          = 0;
    tm->last_progress_ms = 0;
}

void mag_cal_telemetry_next_attempt(mag_cal_telemetry_t *tm) {
    if (tm->attempt < 255u) {
        tm->attempt++;
    }
}

static uint8_t mag_cal_status_to_mavlink(mag_cal_tm_status_t status) {
    switch (status) {
        case MAG_CAL_TM_WAITING:     return MAG_CAL_WAITING_TO_START;
        case MAG_CAL_TM_COLLECTING:  return MAG_CAL_RUNNING_STEP_ONE;
        case MAG_CAL_TM_SOLVING:     return MAG_CAL_RUNNING_STEP_TWO;
        case MAG_CAL_TM_SUCCESS:     return MAG_CAL_SUCCESS;
        case MAG_CAL_TM_FAILED:      return MAG_CAL_FAILED;
        case MAG_CAL_TM_BAD_RADIUS:  return MAG_CAL_BAD_RADIUS;
        case MAG_CAL_TM_NOT_STARTED:
        default:                     return MAG_CAL_NOT_STARTED;
    }
}

static bool mag_cal_send(const mavlink_message_t *msg) {
    uint8_t frame[MAVLINK_MAX_PACKET_LEN];
    const uint16_t len = mavlink_msg_to_send_buffer(frame, msg);
    return mag_cal_link_write(frame, len);
}

bool mag_cal_telemetry_progress(mag_cal_telemetry_t *tm,
                                const mag_cal_collector_t *col,
                                mag_cal_tm_status_t status,
                                uint32_t now_ms) {
    /* Різниця беззнакових чисел коректно переживає переповнення лічильника
     * мілісекунд, тому порівнюємо саме її, а не самі мітки часу. */
    if ((uint32_t)(now_ms - tm->last_progress_ms) < MAG_CAL_PROGRESS_PERIOD_MS) {
        return false;
    }

    uint8_t completion_mask[MAG_CAL_MASK_BYTES];
    mag_cal_collector_completion_mask(col, completion_mask);

    /* Відсоток рахуємо по вибраній квоті, а не по «хоч одна точка»: інакше
     * шкала стрибнула б до ста, коли роботи ще на пів процедури. */
    const float filled_quota = (float)col->total_points
                             / (float)(MAG_CAL_TOTAL_BINS * MAG_CAL_SAMPLES_PER_BIN);
    uint8_t completion_pct = (uint8_t)(filled_quota * 100.0f + 0.5f);
    if (completion_pct > 100u) completion_pct = 100u;

    const vec3_t hint = mag_cal_collector_hint_direction(col);

    mavlink_message_t msg;
    mavlink_msg_mag_cal_progress_pack(tm->system_id, tm->component_id, &msg,
                                      tm->compass_id,
                                      (uint8_t)(1u << (tm->compass_id & 7u)),
                                      mag_cal_status_to_mavlink(status),
                                      tm->attempt,
                                      completion_pct,
                                      completion_mask,
                                      hint.x, hint.y, hint.z);

    tm->last_progress_ms = now_ms;
    return mag_cal_send(&msg);
}

void mag_cal_telemetry_report(mag_cal_telemetry_t *tm,
                              const mag_cal_result_t *cal,
                              bool success, bool autosaved) {
    /* Масштаб сфери відносно очікуваного поля: наземна станція показує ним,
     * чи не калібрували апарат поруч із динаміком або сталевим столом. */
    const float scale_factor = (cal->earth_field > 1.0f)
                             ? (cal->sphere_radius / cal->earth_field)
                             : 1.0f;

    mavlink_message_t msg;
    mavlink_msg_mag_cal_report_pack(tm->system_id, tm->component_id, &msg,
                                    tm->compass_id,
                                    (uint8_t)(1u << (tm->compass_id & 7u)),
                                    success ? MAG_CAL_SUCCESS : MAG_CAL_FAILED,
                                    autosaved ? 1u : 0u,
                                    cal->rms_residual,
                                    cal->offset.x, cal->offset.y, cal->offset.z,
                                    cal->soft_iron.m[0][0],
                                    cal->soft_iron.m[1][1],
                                    cal->soft_iron.m[2][2],
                                    cal->soft_iron.m[0][1],
                                    cal->soft_iron.m[0][2],
                                    cal->soft_iron.m[1][2],
                                    0.0f,                    /* впевненість в орієнтації */
                                    MAV_SENSOR_ROTATION_NONE, /* стару не переглядаємо */
                                    MAV_SENSOR_ROTATION_NONE,
                                    scale_factor);

    (void)mag_cal_send(&msg);
}
