#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    LAND_STATE_FLYING = 0,
    LAND_STATE_DESCENDING,
    LAND_STATE_NEAR_GROUND,
    LAND_STATE_GROUND_CONTACT,
    LAND_STATE_LANDED
} land_state_t;

typedef struct {
    float v_z_descend_target;    /* Цільова швидкість посадки, м/с (напр. -0.4f) */
    float v_z_stopped_thresh;    /* Поріг нульової вертикальної швидкості, м/с (0.15f) */
    float throttle_min_limit;    /* Мінімальний поріг газу (0.12f від діапазону 0..1) */
    float accel_shock_thresh;    /* Поріг ударного прискорення дотику, м/с^2 (3.5f) */
    float current_drop_ratio;    /* Відносне падіння струму при розвантаженні (0.65f) */
    uint32_t contact_time_ms;    /* Час витримки контакту до підтвердження (350 мс) */
    uint32_t disarm_delay_ms;    /* Затримка перед повним вимкненням моторів (500 мс) */
} land_detector_config_t;

typedef struct {
    float alt_ground_relative;   /* Висота над землею (ToF або EKF), м */
    float v_z_filtered;          /* Оцінка вертикальної швидкості (вгору > 0), м/с */
    float throttle_out;          /* Поточний вихідний газ регулятора (0.0 .. 1.0) */
    float accel_z_raw;           /* Прискорення по осі Z (з урахуванням 1g), м/с^2 */
    float battery_current;       /* Струм споживання, А */
    float hover_current;         /* Базовий струм висіння, А */
    bool is_landing_commanded;   /* Прапорець активного режиму посадки */
} land_sensor_data_t;

typedef struct {
    land_state_t state;
    uint32_t state_timer_ms;
    bool i_term_freeze;
    bool disarm_request;
    land_detector_config_t cfg;
} land_detector_t;

void land_detector_init(land_detector_t *detector, const land_detector_config_t *cfg) {
    detector->state = LAND_STATE_FLYING;
    detector->state_timer_ms = 0;
    detector->i_term_freeze = false;
    detector->disarm_request = false;
    detector->cfg = *cfg;
}

void land_detector_update(land_detector_t *detector, const land_sensor_data_t *sensors, uint32_t dt_ms) {
    if (!sensors->is_landing_commanded) {
        detector->state = LAND_STATE_FLYING;
        detector->state_timer_ms = 0;
        detector->i_term_freeze = false;
        detector->disarm_request = false;
        return;
    }

    switch (detector->state) {
        case LAND_STATE_FLYING:
            detector->state = LAND_STATE_DESCENDING;
            detector->state_timer_ms = 0;
            detector->i_term_freeze = false;
            break;

        case LAND_STATE_DESCENDING:
            /* Перехід у зону екранного ефекту за даними висотоміра */
            if (sensors->alt_ground_relative <= 1.5f && sensors->alt_ground_relative > 0.0f) {
                detector->state = LAND_STATE_NEAR_GROUND;
                detector->state_timer_ms = 0;
                detector->i_term_freeze = true; /* Заморожуємо інтегратор кута для захисту від tip-over */
            }
            break;

        case LAND_STATE_NEAR_GROUND: {
            detector->i_term_freeze = true;

            /* Перевірка умов фізичного контакту з поверхнею */
            bool v_z_stopped = fabsf(sensors->v_z_filtered) < detector->cfg.v_z_stopped_thresh;
            bool throttle_low = sensors->throttle_out <= detector->cfg.throttle_min_limit;
            bool accel_shock = fabsf(sensors->accel_z_raw - 9.81f) > detector->cfg.accel_shock_thresh;
            bool current_dropped = (sensors->battery_current < (sensors->hover_current * detector->cfg.current_drop_ratio));

            if (throttle_low && (v_z_stopped || accel_shock || current_dropped)) {
                detector->state_timer_ms += dt_ms;
                if (detector->state_timer_ms >= detector->cfg.contact_time_ms) {
                    detector->state = LAND_STATE_GROUND_CONTACT;
                    detector->state_timer_ms = 0;
                }
            } else {
                detector->state_timer_ms = 0;
            }
            break;
        }

        case LAND_STATE_GROUND_CONTACT:
            detector->i_term_freeze = true;
            detector->state_timer_ms += dt_ms;

            /* Якщо апарат знову підкинуло вітром/газом - повернення на попередній стан */
            if (sensors->throttle_out > detector->cfg.throttle_min_limit * 1.5f ||
                sensors->v_z_filtered > detector->cfg.v_z_stopped_thresh * 2.0f) {
                detector->state = LAND_STATE_NEAR_GROUND;
                detector->state_timer_ms = 0;
                break;
            }

            if (detector->state_timer_ms >= detector->cfg.disarm_delay_ms) {
                detector->state = LAND_STATE_LANDED;
                detector->disarm_request = true;
            }
            break;

        case LAND_STATE_LANDED:
            detector->disarm_request = true;
            detector->i_term_freeze = true;
            break;
    }
}
