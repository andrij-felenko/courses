#ifndef FM_TELEMETRY_H
#define FM_TELEMETRY_H

#include <stdbool.h>
#include <stdint.h>

#include "mission.h"

/* Знімок стану борту на один такт автомата. Структура заповнюється драйверами
   й оцінювачами ДО виклику автомата й далі не міняється: усі охоронці бачать
   один і той самий вектор стану, інакше перевірка й дія розійшлися б у часі. */
typedef struct {
    uint32_t now_ms;                /* бортовий час такту                       */

    /* Живлення */
    float battery_cell_v;           /* напруга на комірці під навантаженням     */
    float battery_remaining;        /* розрахунковий залишок заряду, 0..1       */

    /* Інерціальний блок */
    bool  gyro_healthy;
    bool  accel_healthy;
    bool  attitude_valid;           /* оцінка кутів горизонту достовірна        */
    float accel_z_variance;         /* дисперсія вертикального прискорення      */

    /* Вертикальний канал */
    bool  baro_healthy;
    bool  rangefinder_healthy;
    bool  ekf_vert_pos_valid;
    float altitude_rel_m;           /* висота над точкою старту, метри          */
    float vertical_velocity;        /* м/с, додатна вгору                       */

    /* Горизонтальний канал */
    uint8_t gnss_fix_type;          /* 0 нема, 2 = 2D, 3 = 3D, 4/5 = RTK        */
    uint8_t gnss_sats;
    float   gnss_hdop;
    float   gnss_vdop;
    bool    ekf_horiz_pos_valid;
    float   ekf_innov_pos_norm;     /* нормалізована інновація положення        */
    float   ekf_innov_vel_norm;     /* нормалізована інновація швидкості        */
    bool    compass_healthy;
    float   compass_yaw_error_deg;  /* розбіжність компаса й гіроскопа          */
    int32_t lat_1e7;
    int32_t lon_1e7;
    float   vel_north_ms;           /* оцінка швидкості в системі NED           */
    float   vel_east_ms;

    /* Точка старту */
    bool    home_set;
    int32_t home_lat_1e7;
    int32_t home_lon_1e7;

    /* Органи керування */
    float stick_throttle;           /* 0..1, положення ручки газу               */
    float stick_roll;               /* -1..1                                    */
    float stick_pitch;              /* -1..1                                    */
    float stick_yaw;                /* -1..1                                    */
    bool  stick_disarm_combo;       /* газ униз + рудер ліворуч, витриманий     */
    bool  kill_switch;              /* виділений апаратний тумблер відсічки     */

    /* Канали зв'язку — не прапорці, а мітки часу останнього валідного пакета:
       тайм-аут вирішує автомат за своїм параметром, а не драйвер приймача. */
    uint32_t rc_last_frame_ms;
    uint32_t gcs_last_heartbeat_ms;
    uint32_t guided_setpoint_ms;

    /* Силова частина */
    bool  armed;
    float motor_output;             /* поточна усереднена тяга моторів, 0..1    */
    float hover_throttle;           /* оцінка тяги висіння, 0..1                */

    /* План місії; NULL — буфер порожній */
    const fm_mission_t *mission;
} fm_state_t;

/* Горизонтальна відстань до точки старту; без зафіксованої Home — нуль,
   бо міряти нема від чого (геозона в такому разі перевіряється лише за висотою). */
static inline float fm_state_home_distance_m(const fm_state_t *s)
{
    if (!s || !s->home_set) {
        return 0.0f;
    }
    return fm_geo_distance_m(s->home_lat_1e7, s->home_lon_1e7, s->lat_1e7, s->lon_1e7);
}

#endif /* FM_TELEMETRY_H */
