#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t neutral_us;    // Тривалість імпульсу нейтралі (1500 мкс)
    uint32_t deadband_us;   // Напівширина зони спокою (наприклад, 10 мкс)
    uint32_t max_dev_us;    // Відхилення для досягнення 100% швидкості (400 мкс)
} continuous_servo_cfg_t;

typedef struct {
    int8_t speed_pct;       // Швидкість обертання від -100% до +100%
    bool is_in_deadband;    // Прапор знаходження в зоні спокою
} continuous_servo_state_t;

continuous_servo_state_t compute_continuous_servo_drive(uint32_t pulse_us, const continuous_servo_cfg_t *cfg) {
    continuous_servo_state_t result = { .speed_pct = 0, .is_in_deadband = true };
    int32_t diff = (int32_t)pulse_us - (int32_t)cfg->neutral_us;

    if (diff > (int32_t)cfg->deadband_us) {
        result.is_in_deadband = false;
        int32_t active_dev = diff - (int32_t)cfg->deadband_us;
        int32_t max_active = (int32_t)cfg->max_dev_us - (int32_t)cfg->deadband_us;
        int32_t speed = (active_dev * 100) / max_active;
        result.speed_pct = (speed > 100) ? 100 : (int8_t)speed;
    } else if (diff < -(int32_t)cfg->deadband_us) {
        result.is_in_deadband = false;
        int32_t active_dev = (-diff) - (int32_t)cfg->deadband_us;
        int32_t max_active = (int32_t)cfg->max_dev_us - (int32_t)cfg->deadband_us;
        int32_t speed = (active_dev * 100) / max_active;
        result.speed_pct = (speed > 100) ? -100 : (int8_t)(-speed);
    }

    return result;
}
