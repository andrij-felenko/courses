#include "ina226.h"

// Допоміжна функція запису 16-бітного регістру (Big-Endian: MSB спочатку, LSB другим)
static bool ina226_write_reg16(ina226_t *dev, uint8_t reg, uint16_t val) {
    if (!dev || !dev->i2c_write) return false;
    uint8_t buf[3];
    buf[0] = reg;
    buf[1] = (uint8_t)(val >> 8);   // MSB
    buf[2] = (uint8_t)(val & 0xFF); // LSB
    return dev->i2c_write(dev->config.i2c_addr, buf, 3);
}

// Допоміжна функція зчитування 16-бітного регістру (Big-Endian)
static bool ina226_read_reg16(ina226_t *dev, uint8_t reg, uint16_t *val) {
    if (!dev || !dev->i2c_write || !dev->i2c_read || !val) return false;
    if (!dev->i2c_write(dev->config.i2c_addr, &reg, 1)) return false;
    uint8_t buf[2];
    if (!dev->i2c_read(dev->config.i2c_addr, buf, 2)) return false;
    *val = ((uint16_t)buf[0] << 8) | buf[1]; // Збираємо Big-Endian порядок байтів
    return true;
}

// Розрахунок значення калібрувального регістру CAL цілочисельною арифметикою
// Формула TI Datasheet: CAL = trunc(0.00512 / (Current_LSB * R_shunt))
// Де Current_LSB в Амперах, R_shunt в Омах.
// При R_shunt в мОм та Current_LSB в мкА: CAL = 5,120,000 / (Current_LSB_uA * R_shunt_mOhm)
uint16_t ina226_calc_calibration(uint32_t r_shunt_mohm, uint32_t current_lsb_ua) {
    if (r_shunt_mohm == 0 || current_lsb_ua == 0) return 0;
    uint64_t denom = (uint64_t)r_shunt_mohm * current_lsb_ua;
    if (denom == 0) return 0;
    uint64_t cal = 5120000ULL / denom;
    if (cal > 0xFFFFULL) cal = 0xFFFFULL;
    return (uint16_t)cal;
}

bool ina226_reset(ina226_t *dev) {
    return ina226_write_reg16(dev, INA226_REG_CONFIG, INA226_CONFIG_RESET);
}

bool ina226_check_id(ina226_t *dev) {
    uint16_t manuf_id = 0, die_id = 0;
    if (!ina226_read_reg16(dev, INA226_REG_MANUFACTURER_ID, &manuf_id)) return false;
    if (!ina226_read_reg16(dev, INA226_REG_DIE_ID, &die_id)) return false;
    return (manuf_id == INA226_MANUFACTURER_ID_VAL) && (die_id == INA226_DIE_ID_VAL);
}

bool ina226_write_calibration(ina226_t *dev) {
    if (!dev) return false;
    return ina226_write_reg16(dev, INA226_REG_CALIBRATION, dev->cal_value);
}

bool ina226_init(ina226_t *dev, const ina226_config_t *cfg, ina226_i2c_write_fn w_fn, ina226_i2c_read_fn r_fn) {
    if (!dev || !cfg || !w_fn || !r_fn) return false;

    dev->config = *cfg;
    dev->i2c_write = w_fn;
    dev->i2c_read = r_fn;

    // Скидання пристрою до початкового стану
    if (!ina226_reset(dev)) return false;

    // Перевірка ідентифікаційних регістрів виробника та чипа
    if (!ina226_check_id(dev)) return false;

    // Обчислення вмісту калібрувального регістру CAL
    dev->cal_value = ina226_calc_calibration(dev->config.r_shunt_mohm, dev->config.current_lsb_ua);

    // Запис регістру калібрування
    if (!ina226_write_calibration(dev)) return false;

    // Формування конфігураційного слова
    uint16_t config_word = dev->config.avg_samples | dev->config.vbus_ct | 
                           dev->config.vsh_ct | dev->config.mode;

    return ina226_write_reg16(dev, INA226_REG_CONFIG, config_word);
}

bool ina226_read_bus_voltage(ina226_t *dev, uint32_t *voltage_mv) {
    if (!dev || !voltage_mv) return false;
    uint16_t raw = 0;
    if (!ina226_read_reg16(dev, INA226_REG_BUSVOLT, &raw)) return false;
    // LSB напруги шини = 1.25 мВ = 5/4 мВ
    *voltage_mv = ((uint32_t)raw * 5U) / 4U;
    return true;
}

bool ina226_read_shunt_voltage(ina226_t *dev, int32_t *voltage_uv) {
    if (!dev || !voltage_uv) return false;
    uint16_t raw_u = 0;
    if (!ina226_read_reg16(dev, INA226_REG_SHUNTVOLT, &raw_u)) return false;
    int16_t raw = (int16_t)raw_u; // Доповнювальний код до 2 (знакове число)
    // LSB напруги шунта = 2.5 мкВ = 5/2 мкВ
    *voltage_uv = ((int32_t)raw * 5) / 2;
    return true;
}

bool ina226_read_current(ina226_t *dev, int32_t *current_ma) {
    if (!dev || !current_ma) return false;
    uint16_t raw_u = 0;
    if (!ina226_read_reg16(dev, INA226_REG_CURRENT, &raw_u)) return false;
    int16_t raw = (int16_t)raw_u;
    // Current (мкА) = raw * current_lsb_ua
    // Current (мА) = Current (мкА) / 1000
    int64_t current_ua = (int64_t)raw * dev->config.current_lsb_ua;
    *current_ma = (int32_t)(current_ua / 1000);
    return true;
}

bool ina226_read_power(ina226_t *dev, uint32_t *power_mw) {
    if (!dev || !power_mw) return false;
    uint16_t raw = 0;
    if (!ina226_read_reg16(dev, INA226_REG_POWER, &raw)) return false;
    // Power LSB = 25 * Current LSB (мкВт)
    // Power (мкВт) = raw * 25 * current_lsb_ua
    // Power (мВт) = Power (мкВт) / 1000
    uint64_t power_uw = (uint64_t)raw * 25ULL * dev->config.current_lsb_ua;
    *power_mw = (uint32_t)(power_uw / 1000ULL);
    return true;
}

bool ina226_read_all(ina226_t *dev, ina226_data_t *data) {
    if (!dev || !data) return false;
    if (!ina226_read_bus_voltage(dev, &data->bus_voltage_mv)) return false;
    if (!ina226_read_shunt_voltage(dev, &data->shunt_voltage_uv)) return false;
    if (!ina226_read_current(dev, &data->current_ma)) return false;
    if (!ina226_read_power(dev, &data->power_mw)) return false;
    return true;
}

bool ina226_configure_alert(ina226_t *dev, uint16_t mask_flags, uint16_t limit_raw) {
    if (!dev) return false;
    if (!ina226_write_reg16(dev, INA226_REG_ALERT_LIMIT, limit_raw)) return false;
    return ina226_write_reg16(dev, INA226_REG_MASK_ENABLE, mask_flags);
}

bool ina226_read_mask_enable(ina226_t *dev, uint16_t *flags) {
    if (!dev || !flags) return false;
    return ina226_read_reg16(dev, INA226_REG_MASK_ENABLE, flags);
}
