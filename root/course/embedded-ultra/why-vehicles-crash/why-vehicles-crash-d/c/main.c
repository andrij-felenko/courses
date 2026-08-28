#include <stdint.h>
#include <stdbool.h>

typedef enum {
    FAIL_MODE_NONE = 0,
    FAIL_MODE_SENSOR_DEGRADED,
    FAIL_MODE_RTH,
    FAIL_MODE_LAND,
    FAIL_MODE_TERMINATE
} failsafe_mode_t;

typedef struct {
    uint32_t last_rc_tick_ms;
    uint32_t last_imu_tick_ms;
    float vbat_volts;
    float tilt_roll_deg;
    float tilt_pitch_deg;
    bool gps_valid;
} flight_telemetry_t;

/* Процедура вивільнення заблокованої лінії SDA 9 тактами SCL */
bool i2c_bus_recover_sda(void (*scl_pin_set)(bool level),
                         bool (*sda_pin_read)(void),
                         void (*delay_fn)(uint32_t us)) {
    /* 1. Генеруємо до 9 імпульсів на лінії SCL */
    for (uint8_t i = 0; i < 9; ++i) {
        if (sda_pin_read()) {
            break; /* Ведений пристрій відпустив лінію SDA у High-Z */
        }
        scl_pin_set(false);
        delay_fn(5);
        scl_pin_set(true);
        delay_fn(5);
    }
    return sda_pin_read();
}

/* Оцінка стану безпеки та перемикання аварійного режиму */
failsafe_mode_t failsafe_evaluate_state(const flight_telemetry_t *telem, uint32_t now_ms) {
    const uint32_t rc_dt = now_ms - telem->last_rc_tick_ms;
    const uint32_t imu_dt = now_ms - telem->last_imu_tick_ms;

    /* 1. Фатальні умови: перекидання понад 75 градусів або відмова IMU */
    if (imu_dt > 40 || telem->tilt_roll_deg > 75.0f || telem->tilt_roll_deg < -75.0f ||
        telem->tilt_pitch_deg > 75.0f || telem->tilt_pitch_deg < -75.0f) {
        return FAIL_MODE_TERMINATE;
    }

    /* 2. Критичне падіння напруги живлення */
    if (telem->vbat_volts < 13.2f) { /* Поріг 3.3 В на банку для 4S */
        return FAIL_MODE_LAND;
    }

    /* 3. Втрата зв'язку керування RC */
    if (rc_dt > 1500) {
        return telem->gps_valid ? FAIL_MODE_RTH : FAIL_MODE_LAND;
    }

    return FAIL_MODE_NONE;
}
