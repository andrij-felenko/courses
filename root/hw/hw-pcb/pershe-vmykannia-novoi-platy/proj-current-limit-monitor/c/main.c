#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define INA226_I2C_ADDR         0x40
#define INA226_REG_CONFIG       0x00
#define INA226_REG_SHUNTVOLT    0x01
#define INA226_REG_BUSVOLT      0x02
#define INA226_REG_POWER        0x03
#define INA226_REG_CURRENT      0x04
#define INA226_REG_CALIBRATION  0x05
#define INA226_REG_MASKENABLE   0x06
#define INA226_REG_ALERTLIMIT   0x07

#define INA226_CFG_RESET        0x8000
#define INA226_CFG_AVG_16       (0x02 << 9)
#define INA226_CFG_VBUS_1100US  (0x04 << 6)
#define INA226_CFG_VSH_1100US   (0x04 << 3)
#define INA226_CFG_MODE_CONT    0x07

#define INA226_MASK_SOL         (1 << 15)  /* Shunt Over-Limit Alert */
#define INA226_MASK_POL         (1 << 14)  /* Power Over-Limit Alert */
#define INA226_MASK_AFF         (1 << 4)   /* Alert Function Flag */
#define INA226_MASK_APOL        (1 << 1)   /* Alert Polarity Active High */
#define INA226_MASK_LEN         (1 << 0)   /* Latch Enable */

#define BLACKBOX_BUFFER_SIZE    256
#define CURRENT_LSB_UA          200        /* 200 uA per LSB */
#define VOLTAGE_LSB_UV          1250       /* 1.25 mV per LSB */
#define POWER_LSB_UW            5000       /* 5 mW per LSB */

typedef enum {
    MONITOR_STATE_DISARMED = 0,
    MONITOR_STATE_SOFT_START,
    MONITOR_STATE_ARMED,
    MONITOR_STATE_FAULT_OVERCURRENT,
    MONITOR_STATE_FAULT_OVERVOLTAGE,
    MONITOR_STATE_FAULT_BROWNOUT,
    MONITOR_STATE_HARDWARE_TRIP
} MonitorState_t;

typedef struct {
    uint32_t timestamp_ms;
    int32_t  current_ma;
    uint32_t voltage_mv;
    uint32_t power_mw;
} TelemetryFrame_t;

typedef struct {
    TelemetryFrame_t frames[BLACKBOX_BUFFER_SIZE];
    uint16_t head;
    uint16_t count;
    bool is_locked;
} BlackboxRecorder_t;

typedef struct {
    uint16_t i2c_address;
    uint16_t cal_register_val;
    int32_t  max_current_limit_ma;
    uint32_t min_voltage_limit_mv;
    uint32_t max_voltage_limit_mv;
    uint32_t inrush_grace_period_ms;
    int32_t  current_ema_ma;
    uint32_t state_entered_timestamp_ms;
    MonitorState_t state;
    BlackboxRecorder_t blackbox;
    bool (*i2c_write_reg)(uint8_t addr, uint8_t reg, uint16_t val);
    bool (*i2c_read_reg)(uint8_t addr, uint8_t reg, uint16_t *val);
    void (*set_switch_state)(bool enabled);
    uint32_t (*get_system_tick_ms)(void);
} PowerMonitor_t;

static inline uint16_t swap_bytes(uint16_t val) {
    return (uint16_t)((val << 8) | (val >> 8));
}

void blackbox_record(BlackboxRecorder_t *bb, const TelemetryFrame_t *frame) {
    if (bb->is_locked) return;
    bb->frames[bb->head] = *frame;
    bb->head = (bb->head + 1) % BLACKBOX_BUFFER_SIZE;
    if (bb->count < BLACKBOX_BUFFER_SIZE) {
        bb->count++;
    }
}

void blackbox_lock(BlackboxRecorder_t *bb) {
    bb->is_locked = true;
}

bool power_monitor_init(PowerMonitor_t *mon, uint8_t i2c_addr, uint16_t cal_val,
                        int32_t limit_ma, uint32_t min_mv, uint32_t max_mv) {
    if (!mon || !mon->i2c_write_reg || !mon->i2c_read_reg || !mon->set_switch_state) {
        return false;
    }

    mon->i2c_address = i2c_addr;
    mon->cal_register_val = cal_val;
    mon->max_current_limit_ma = limit_ma;
    mon->min_voltage_limit_mv = min_mv;
    mon->max_voltage_limit_mv = max_mv;
    mon->inrush_grace_period_ms = 25; /* 25 ms inrush mask */
    mon->current_ema_ma = 0;
    mon->state = MONITOR_STATE_DISARMED;
    mon->blackbox.head = 0;
    mon->blackbox.count = 0;
    mon->blackbox.is_locked = false;

    /* Примусове розмикання силового ключа */
    mon->set_switch_state(false);

    /* Скидання мікросхеми INA226 */
    if (!mon->i2c_write_reg(mon->i2c_address, INA226_REG_CONFIG, swap_bytes(INA226_CFG_RESET))) {
        return false;
    }

    /* Запис конфігурації: 16 усереднень, час конверсії 1.1 мс для напруги та струму */
    uint16_t cfg = INA226_CFG_AVG_16 | INA226_CFG_VBUS_1100US | INA226_CFG_VSH_1100US | INA226_CFG_MODE_CONT;
    if (!mon->i2c_write_reg(mon->i2c_address, INA226_REG_CONFIG, swap_bytes(cfg))) {
        return false;
    }

    /* Запис регістра калібрування */
    if (!mon->i2c_write_reg(mon->i2c_address, INA226_REG_CALIBRATION, swap_bytes(mon->cal_register_val))) {
        return false;
    }

    /* Налаштування апаратного ALERT виводу на перевищення струму шунта */
    int16_t raw_alert_limit = (int16_t)((limit_ma * 1000) / CURRENT_LSB_UA);
    if (!mon->i2c_write_reg(mon->i2c_address, INA226_REG_ALERTLIMIT, swap_bytes((uint16_t)raw_alert_limit))) {
        return false;
    }

    uint16_t mask_enable = INA226_MASK_SOL | INA226_MASK_APOL | INA226_MASK_LEN;
    if (!mon->i2c_write_reg(mon->i2c_address, INA226_REG_MASKENABLE, swap_bytes(mask_enable))) {
        return false;
    }

    return true;
}

bool power_monitor_arm(PowerMonitor_t *mon) {
    if (mon->state != MONITOR_STATE_DISARMED) {
        return false;
    }
    mon->state_entered_timestamp_ms = mon->get_system_tick_ms();
    mon->state = MONITOR_STATE_SOFT_START;
    mon->set_switch_state(true);
    return true;
}

void power_monitor_emergency_trip(PowerMonitor_t *mon, MonitorState_t reason) {
    mon->set_switch_state(false);
    mon->state = reason;
    blackbox_lock(&mon->blackbox);
}

void power_monitor_hardware_isr_callback(PowerMonitor_t *mon) {
    /* Негайне переривання від лінії ALERT INA226 або швидкого компаратора */
    mon->set_switch_state(false);
    mon->state = MONITOR_STATE_HARDWARE_TRIP;
    blackbox_lock(&mon->blackbox);
}

void power_monitor_process(PowerMonitor_t *mon) {
    if (mon->state == MONITOR_STATE_DISARMED ||
        mon->state == MONITOR_STATE_FAULT_OVERCURRENT ||
        mon->state == MONITOR_STATE_FAULT_OVERVOLTAGE ||
        mon->state == MONITOR_STATE_FAULT_BROWNOUT ||
        mon->state == MONITOR_STATE_HARDWARE_TRIP) {
        return;
    }

    uint32_t now = mon->get_system_tick_ms();
    uint16_t raw_vbus = 0, raw_curr = 0, raw_pwr = 0, raw_mask = 0;

    if (!mon->i2c_read_reg(mon->i2c_address, INA226_REG_BUSVOLT, &raw_vbus) ||
        !mon->i2c_read_reg(mon->i2c_address, INA226_REG_CURRENT, &raw_curr) ||
        !mon->i2c_read_reg(mon->i2c_address, INA226_REG_POWER, &raw_pwr) ||
        !mon->i2c_read_reg(mon->i2c_address, INA226_REG_MASKENABLE, &raw_mask)) {
        power_monitor_emergency_trip(mon, MONITOR_STATE_HARDWARE_TRIP);
        return;
    }

    raw_vbus = swap_bytes(raw_vbus);
    raw_curr = swap_bytes(raw_curr);
    raw_pwr = swap_bytes(raw_pwr);
    raw_mask = swap_bytes(raw_mask);

    int16_t signed_raw_curr = (int16_t)raw_curr;
    int32_t current_ma = ((int32_t)signed_raw_curr * CURRENT_LSB_UA) / 1000;
    uint32_t voltage_mv = ((uint32_t)raw_vbus * VOLTAGE_LSB_UV) / 1000;
    uint32_t power_mw = ((uint32_t)raw_pwr * POWER_LSB_UW) / 1000;

    TelemetryFrame_t frame = {
        .timestamp_ms = now,
        .current_ma = current_ma,
        .voltage_mv = voltage_mv,
        .power_mw = power_mw
    };
    blackbox_record(&mon->blackbox, &frame);

    /* Оновлення експоненційного ковзного середнього (alpha = 0.25 -> 1/4) */
    if (mon->current_ema_ma == 0) {
        mon->current_ema_ma = current_ma;
    } else {
        mon->current_ema_ma = (mon->current_ema_ma * 3 + current_ma) / 4;
    }

    /* Перевірка стану плавного пуску (Soft Start Grace Period) */
    if (mon->state == MONITOR_STATE_SOFT_START) {
        if (now - mon->state_entered_timestamp_ms >= mon->inrush_grace_period_ms) {
            mon->state = MONITOR_STATE_ARMED;
        }
    }

    /* Перевірка прапорця апаратного алерту в мікросхемі */
    if (raw_mask & INA226_MASK_AFF) {
        power_monitor_emergency_trip(mon, MONITOR_STATE_FAULT_OVERCURRENT);
        return;
    }

    /* Аналіз напруги живлення на перенапругу та просідання (Brownout) */
    if (voltage_mv > mon->max_voltage_limit_mv) {
        power_monitor_emergency_trip(mon, MONITOR_STATE_FAULT_OVERVOLTAGE);
        return;
    }

    if (mon->state == MONITOR_STATE_ARMED && voltage_mv < mon->min_voltage_limit_mv) {
        power_monitor_emergency_trip(mon, MONITOR_STATE_FAULT_BROWNOUT);
        return;
    }

    /* Програмний контроль перевантаження за струмом */
    if (mon->state == MONITOR_STATE_ARMED && current_ma > mon->max_current_limit_ma) {
        power_monitor_emergency_trip(mon, MONITOR_STATE_FAULT_OVERCURRENT);
        return;
    }
}
