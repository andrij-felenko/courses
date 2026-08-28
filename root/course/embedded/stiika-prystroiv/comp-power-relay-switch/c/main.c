// Драйвер комутатора живлення слота стенда (C99)
#include <stdint.h>
#include <stdbool.h>

#define SLOT_MAX_INRUSH_CURRENT_MA  1500U
#define SLOT_STEADY_CURRENT_LIMIT_MA 800U
#define SOFT_START_SETTLE_MS         20U

typedef enum {
    SLOT_PWR_OFF = 0,
    SLOT_PWR_SOFT_START,
    SLOT_PWR_ACTIVE,
    SLOT_PWR_OVERCURRENT_FAULT,
    SLOT_PWR_PARASITIC_LEAK_FAULT
} slot_pwr_state_t;

typedef struct {
    uint8_t slot_id;
    uint8_t i2c_addr_io;
    uint8_t i2c_addr_ina;
    slot_pwr_state_t state;
    uint16_t last_current_ma;
    uint16_t last_voltage_mv;
} slot_switch_t;

// Апаратні заглушки взаємодії з I2C шиною стенда
extern bool i2c_write_reg8(uint8_t dev_addr, uint8_t reg, uint8_t val);
extern bool i2c_read_reg16(uint8_t dev_addr, uint8_t reg, uint16_t *val);
extern void delay_ms(uint32_t ms);

// Ініціалізація слота
void slot_switch_init(slot_switch_t *slot, uint8_t id, uint8_t io_addr, uint8_t ina_addr) {
    slot->slot_id = id;
    slot->i2c_addr_io = io_addr;
    slot->i2c_addr_ina = ina_addr;
    slot->state = SLOT_PWR_OFF;
    slot->last_current_ma = 0;
    slot->last_voltage_mv = 0;
    
    // Переконатися, що силовий ключ закрито при старті
    i2c_write_reg8(slot->i2c_addr_io, 0x02, 0x00); // Output reg: Low
}

// Вимірювання струму через INA219 (LSB = 100 мкА)
bool slot_read_telemetry(slot_switch_t *slot) {
    uint16_t raw_current = 0;
    uint16_t raw_voltage = 0;
    
    if (!i2c_read_reg16(slot->i2c_addr_ina, 0x04, &raw_current)) {
        return false;
    }
    if (!i2c_read_reg16(slot->i2c_addr_ina, 0x02, &raw_voltage)) {
        return false;
    }
    
    slot->last_current_ma = raw_current / 10U; // переведення в мА
    slot->last_voltage_mv = (raw_voltage >> 3) * 4U; // INA219 Bus Voltage
    return true;
}

// Увімкнення живлення слота з контролем струму
bool slot_power_on(slot_switch_t *slot) {
    // 1. Перевірка на паразитне живлення до вмикання
    slot_read_telemetry(slot);
    if (slot->last_voltage_mv > 500U) {
        // На вимкненій платі напруга вища 0.5 В — витік через UART/SWD!
        slot->state = SLOT_PWR_PARASITIC_LEAK_FAULT;
        return false;
    }
    
    // 2. Подача сигналу на відкриття P-MOSFET
    slot->state = SLOT_PWR_SOFT_START;
    i2c_write_reg8(slot->i2c_addr_io, 0x02, (uint8_t)(1U << slot->slot_id));
    
    // 3. Очікування часу Soft-Start
    delay_ms(SOFT_START_SETTLE_MS);
    
    // 4. Перевірка струму після пуску
    slot_read_telemetry(slot);
    if (slot->last_current_ma > SLOT_MAX_INRUSH_CURRENT_MA) {
        // Струмовий удар / коротке замикання — аварійне вимкнення
        i2c_write_reg8(slot->i2c_addr_io, 0x02, 0x00);
        slot->state = SLOT_PWR_OVERCURRENT_FAULT;
        return false;
    }
    
    slot->state = SLOT_PWR_ACTIVE;
    return true;
}

// Вимкнення живлення слота (Hard Reset / Power Cycle)
void slot_power_off(slot_switch_t *slot) {
    i2c_write_reg8(slot->i2c_addr_io, 0x02, 0x00);
    slot->state = SLOT_PWR_OFF;
}
