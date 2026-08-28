#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAX_PAYLOAD_EVENTS      16
#define MAX_DROP_RETRIES        3
#define DEFAULT_SHUTTER_PULSE_MS 50
#define DROP_TIMEOUT_MS         400
#define CURRENT_STALL_THRESHOLD_MA 2500

typedef enum {
    TRIGGER_MODE_DISABLED = 0,
    TRIGGER_MODE_DISTANCE,
    TRIGGER_MODE_TIME,
    TRIGGER_MODE_MANUAL
} trigger_mode_t;

typedef enum {
    DROP_STATE_IDLE = 0,
    DROP_STATE_ARMED,
    DROP_STATE_TRIGGERED,
    DROP_STATE_VERIFYING,
    DROP_STATE_SUCCESS,
    DROP_STATE_STALLED,
    DROP_STATE_FAULT
} drop_state_t;

typedef struct {
    double lat;
    double lon;
    float alt_ned;
} geo_point_t;

typedef struct {
    float x;
    float y;
    float z;
} vector3f_t;

typedef struct {
    uint32_t timestamp_ms;
    uint32_t sequence_id;
    uint8_t  event_type; // 1: Shutter, 2: Drop Success, 3: Drop Fault, 4: ROI Lock
    geo_point_t position;
    float pitch_deg;
    float yaw_deg;
    uint16_t current_ma;
} payload_event_log_t;

typedef struct {
    // Тригер камери
    trigger_mode_t cam_mode;
    float trigger_dist_m;
    uint32_t trigger_interval_ms;
    vector3f_t last_cam_pos;
    uint32_t last_cam_time_ms;
    uint32_t shutter_off_time_ms;
    bool shutter_active;
    uint32_t photo_count;

    // Скидання навантаження
    drop_state_t drop_state;
    uint32_t drop_start_time_ms;
    uint8_t drop_retry_count;
    bool limit_switch_active;
    uint16_t measured_current_ma;

    // Наведення підвісу (ROI)
    bool roi_active;
    geo_point_t roi_target;
    float gimbal_cmd_pitch;
    float gimbal_cmd_yaw;

    // Кільцевий буфер подій
    payload_event_log_t events[MAX_PAYLOAD_EVENTS];
    uint8_t event_head;
    uint8_t event_tail;
} payload_manager_t;

// Апаратні заглушки інтерфейсів платформи
extern uint32_t platform_get_time_ms(void);
extern void platform_gpio_set_shutter(bool high);
extern void platform_pwm_set_drop_servo(uint16_t pwm_us);
extern void platform_solenoid_enable(bool enable);
extern bool platform_read_limit_switch(void);
extern uint16_t platform_adc_read_drop_current_ma(void);
extern void platform_send_gimbal_setpoint(float pitch_deg, float yaw_deg);

void payload_init(payload_manager_t *pm) {
    memset(pm, 0, sizeof(payload_manager_t));
    pm->cam_mode = TRIGGER_MODE_DISABLED;
    pm->drop_state = DROP_STATE_IDLE;
    pm->roi_active = false;
}

static void log_payload_event(payload_manager_t *pm, uint8_t event_type, const geo_point_t *pos, float pitch, float yaw, uint16_t current_ma) {
    uint8_t next = (pm->event_head + 1) % MAX_PAYLOAD_EVENTS;
    if (next != pm->event_tail) {
        payload_event_log_t *e = &pm->events[pm->event_head];
        e->timestamp_ms = platform_get_time_ms();
        e->sequence_id = pm->photo_count;
        e->event_type = event_type;
        e->position = *pos;
        e->pitch_deg = pitch;
        e->yaw_deg = yaw;
        e->current_ma = current_ma;
        pm->event_head = next;
    }
}

void payload_set_roi_target(payload_manager_t *pm, double lat, double lon, float alt_ned) {
    pm->roi_target.lat = lat;
    pm->roi_target.lon = lon;
    pm->roi_target.alt_ned = alt_ned;
    pm->roi_active = true;
}

void payload_clear_roi(payload_manager_t *pm) {
    pm->roi_active = false;
}

void payload_start_drop_sequence(payload_manager_t *pm) {
    if (pm->drop_state == DROP_STATE_IDLE || pm->drop_state == DROP_STATE_ARMED) {
        pm->drop_state = DROP_STATE_TRIGGERED;
        pm->drop_start_time_ms = platform_get_time_ms();
        pm->drop_retry_count = 0;

        // Подача команди на розблокування замка (імпульс серво або соленоїда)
        platform_pwm_set_drop_servo(2000);
        platform_solenoid_enable(true);
    }
}

void payload_update(payload_manager_t *pm, const vector3f_t *pos_ned, const geo_point_t *current_geo, float roll_deg, float pitch_deg, float yaw_deg) {
    uint32_t now = platform_get_time_ms();

    // 1. Обробка імпульсу затвора камери
    if (pm->shutter_active && now >= pm->shutter_off_time_ms) {
        platform_gpio_set_shutter(false);
        pm->shutter_active = false;
    }

    // 2. Генератор інтервалів зйомки
    if (pm->cam_mode == TRIGGER_MODE_DISTANCE && pm->trigger_dist_m > 0.1f) {
        // Блокуємо спрацьовування на крутих віражах (крен > 15 градусів)
        if (fabsf(roll_deg) < 15.0f && fabsf(pitch_deg) < 20.0f) {
            float dx = pos_ned->x - pm->last_cam_pos.x;
            float dy = pos_ned->y - pm->last_cam_pos.y;
            float dz = pos_ned->z - pm->last_cam_pos.z;
            float dist_moved = sqrtf(dx * dx + dy * dy + dz * dz);

            if (dist_moved >= pm->trigger_dist_m) {
                pm->last_cam_pos = *pos_ned;
                pm->shutter_active = true;
                pm->shutter_off_time_ms = now + DEFAULT_SHUTTER_PULSE_MS;
                pm->photo_count++;
                platform_gpio_set_shutter(true);
                log_payload_event(pm, 1, current_geo, pm->gimbal_cmd_pitch, pm->gimbal_cmd_yaw, 0);
            }
        }
    }

    // 3. Автомат стану механізму скидання вантажу
    switch (pm->drop_state) {
        case DROP_STATE_TRIGGERED:
            pm->measured_current_ma = platform_adc_read_drop_current_ma();
            pm->limit_switch_active = platform_read_limit_switch();

            // Перевірка на коротке замикання або заклинювання
            if (pm->measured_current_ma > CURRENT_STALL_THRESHOLD_MA) {
                platform_solenoid_enable(false);
                pm->drop_state = DROP_STATE_STALLED;
                log_payload_event(pm, 3, current_geo, 0, 0, pm->measured_current_ma);
                break;
            }

            // Перевірка спрацьовування кінцевика
            if (pm->limit_switch_active) {
                platform_solenoid_enable(false);
                pm->drop_state = DROP_STATE_SUCCESS;
                log_payload_event(pm, 2, current_geo, 0, 0, pm->measured_current_ma);
            } else if (now - pm->drop_start_time_ms > DROP_TIMEOUT_MS) {
                // Таймаут ходу ригеля: спроба повторного циклу
                if (pm->drop_retry_count < MAX_DROP_RETRIES) {
                    pm->drop_retry_count++;
                    pm->drop_start_time_ms = now;
                    // Цикл розхитування (вібрації замка)
                    platform_pwm_set_drop_servo(1000);
                    platform_solenoid_enable(false);
                    platform_pwm_set_drop_servo(2000);
                    platform_solenoid_enable(true);
                } else {
                    platform_solenoid_enable(false);
                    pm->drop_state = DROP_STATE_FAULT;
                    log_payload_event(pm, 3, current_geo, 0, 0, pm->measured_current_ma);
                }
            }
            break;

        default:
            break;
    }

    // 4. Розрахунок наведення підвісу на ціль (ROI)
    if (pm->roi_active) {
        // Локальна апроксимація зміщення в метрах
        double d_lat = (pm->roi_target.lat - current_geo->lat) * 111132.95;
        double d_lon = (pm->roi_target.lon - current_geo->lon) * (111412.84 * cos(current_geo->lat * 0.01745329));
        float d_z = pm->roi_target.alt_ned - current_geo->alt_ned;

        float dist_xy = sqrtf((float)(d_lat * d_lat + d_lon * d_lon));
        if (dist_xy > 1.0f) {
            pm->gimbal_cmd_pitch = atan2f(-d_z, dist_xy) * 57.29578f;
            pm->gimbal_cmd_yaw   = atan2f((float)d_lon, (float)d_lat) * 57.29578f;
            platform_send_gimbal_setpoint(pm->gimbal_cmd_pitch, pm->gimbal_cmd_yaw);
        }
    }
}
