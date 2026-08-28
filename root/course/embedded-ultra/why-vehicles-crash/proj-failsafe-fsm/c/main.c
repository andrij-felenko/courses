#include <stdint.h>
#include <stdbool.h>

/* Перелік станів аварійного автомата */
typedef enum {
    FAILSAFE_STATE_NORMAL = 0,
    FAILSAFE_STATE_DEGRADED,
    FAILSAFE_STATE_RTH,
    FAILSAFE_STATE_EMERGENCY_LAND,
    FAILSAFE_STATE_TERMINATE
} failsafe_state_t;

/* Вхідні сенсорні метрики здоров'я апарата */
typedef struct {
    uint32_t last_rc_packet_ms;
    uint32_t last_gps_fix_ms;
    uint32_t last_imu_sample_ms;
    float battery_voltage_v;
    float roll_deg;
    float pitch_deg;
    bool i2c_bus_healthy;
} vehicle_health_t;

/* Конфігурація часових порогів (мс) та напруг (В) */
#define RC_TIMEOUT_MS           1500
#define GPS_TIMEOUT_MS          3000
#define IMU_TIMEOUT_MS          40
#define BATT_WARNING_VOLTS      14.4f   /* 4S LiPo: 3.6 В/банка */
#define BATT_CRITICAL_VOLTS     13.2f   /* 4S LiPo: 3.3 В/банка */
#define MAX_TILT_ANGLE_DEG      75.0f

typedef struct {
    failsafe_state_t current_state;
    uint32_t state_entry_time_ms;
    bool parachute_deployed;
    bool motors_disarmed;
} failsafe_manager_t;

void failsafe_init(failsafe_manager_t *mgr) {
    mgr->current_state = FAILSAFE_STATE_NORMAL;
    mgr->state_entry_time_ms = 0;
    mgr->parachute_deployed = false;
    mgr->motors_disarmed = false;
}

/* Процедура апаратного вивільнення лінії SDA шини I2C (Bit-Banging) */
bool i2c_bus_clear_recovery(void (*set_scl)(bool high),
                            void (*set_sda)(bool high),
                            bool (*read_sda)(void),
                            void (*delay_us)(uint32_t us)) {
    /* 1. Відпускаємо лінію SDA (налаштування як вхід із pull-up) */
    set_sda(true);
    delay_us(5);

    /* 2. Якщо SDA вже висока — шина не заблокована */
    if (read_sda()) {
        return true;
    }

    /* 3. Генеруємо до 9 тактів SCL для виштовхування біта зі Slave */
    for (uint8_t i = 0; i < 9; ++i) {
        set_scl(false);
        delay_us(5);
        set_scl(true);
        delay_us(5);

        /* Якщо Slave відпустив SDA, виходимо з циклу */
        if (read_sda()) {
            break;
        }
    }

    /* 4. Генерація умови STOP (перехід SDA з 0 в 1 при високому SCL) */
    set_sda(false);
    delay_us(5);
    set_scl(true);
    delay_us(5);
    set_sda(true);
    delay_us(5);

    return read_sda();
}

/* Крок обчислення кінцевого автомата Failsafe */
void failsafe_update(failsafe_manager_t *mgr,
                     const vehicle_health_t *health,
                     uint32_t now_ms) {
    const bool rc_lost = (now_ms - health->last_rc_packet_ms) > RC_TIMEOUT_MS;
    const bool gps_lost = (now_ms - health->last_gps_fix_ms) > GPS_TIMEOUT_MS;
    const bool imu_lost = (now_ms - health->last_imu_sample_ms) > IMU_TIMEOUT_MS;
    const bool batt_critical = health->battery_voltage_v < BATT_CRITICAL_VOLTS;
    const bool batt_warning = health->battery_voltage_v < BATT_WARNING_VOLTS;
    const bool angle_exceeded = (health->roll_deg > MAX_TILT_ANGLE_DEG) ||
                                (health->roll_deg < -MAX_TILT_ANGLE_DEG) ||
                                (health->pitch_deg > MAX_TILT_ANGLE_DEG) ||
                                (health->pitch_deg < -MAX_TILT_ANGLE_DEG);

    /* 1. Безумовна перевірка катастрофічних умов (Перекидання / Втрата IMU) */
    if (angle_exceeded || imu_lost) {
        mgr->current_state = FAILSAFE_STATE_TERMINATE;
        mgr->parachute_deployed = true;
        mgr->motors_disarmed = true;
        return;
    }

    /* 2. Обробка переходів за станами */
    switch (mgr->current_state) {
        case FAILSAFE_STATE_NORMAL:
            if (rc_lost && !gps_lost) {
                mgr->current_state = FAILSAFE_STATE_RTH;
                mgr->state_entry_time_ms = now_ms;
            } else if (rc_lost && gps_lost) {
                mgr->current_state = FAILSAFE_STATE_EMERGENCY_LAND;
                mgr->state_entry_time_ms = now_ms;
            } else if (batt_warning || !health->i2c_bus_healthy) {
                mgr->current_state = FAILSAFE_STATE_DEGRADED;
                mgr->state_entry_time_ms = now_ms;
            }
            break;

        case FAILSAFE_STATE_DEGRADED:
            if (batt_critical) {
                mgr->current_state = FAILSAFE_STATE_EMERGENCY_LAND;
                mgr->state_entry_time_ms = now_ms;
            } else if (rc_lost && !gps_lost) {
                mgr->current_state = FAILSAFE_STATE_RTH;
                mgr->state_entry_time_ms = now_ms;
            } else if (!rc_lost && !batt_warning && health->i2c_bus_healthy) {
                mgr->current_state = FAILSAFE_STATE_NORMAL;
            }
            break;

        case FAILSAFE_STATE_RTH:
            if (batt_critical || gps_lost) {
                mgr->current_state = FAILSAFE_STATE_EMERGENCY_LAND;
                mgr->state_entry_time_ms = now_ms;
            }
            break;

        case FAILSAFE_STATE_EMERGENCY_LAND:
            /* Якщо апарат знижується довше 30 секунд — примусове вимикання моторів */
            if (now_ms - mgr->state_entry_time_ms > 30000) {
                mgr->motors_disarmed = true;
            }
            break;

        case FAILSAFE_STATE_TERMINATE:
            mgr->parachute_deployed = true;
            mgr->motors_disarmed = true;
            break;
    }
}
