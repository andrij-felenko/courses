#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define INA226_I2C_ADDR_DEFAULT  0x40

/* Адреси внутрішніх регістрів */
#define INA226_REG_CONFIG        0x00
#define INA226_REG_SHUNTVOLTAGE  0x01
#define INA226_REG_BUSVOLTAGE    0x02
#define INA226_REG_POWER         0x03
#define INA226_REG_CURRENT       0x04
#define INA226_REG_CALIBRATION   0x05
#define INA226_REG_MASKENABLE    0x06
#define INA226_REG_ALERTLIMIT    0x07
#define INA226_REG_MANUF_ID      0xFE
#define INA226_REG_DIE_ID        0xFF

/* Бітові маски конфігурації */
#define INA226_RESET_BIT         0x8000
#define INA226_AVG_16            (0x02 << 9)
#define INA226_VBUS_CT_1100US    (0x04 << 6)
#define INA226_VSH_CT_1100US     (0x04 << 3)
#define INA226_MODE_CONTINUOUS   0x07
#define INA226_MODE_POWERDOWN    0x00
#define INA226_MODE_TRIGGERED    0x03

/* Бітові маски регістра переривань (MASK_ENABLE) */
#define INA226_ALERT_SHUNT_OVER  (1 << 15)
#define INA226_ALERT_BUS_OVER    (1 << 12)
#define INA226_ALERT_BUS_UNDER   (1 << 11)
#define INA226_ALERT_POWER_OVER  (1 << 10)
#define INA226_ALERT_CONV_READY  (1 << 14)

/* Абстракція платформного рівня I2C */
typedef bool (*ina226_i2c_write_fn)(uint8_t dev_addr, uint8_t reg, const uint8_t *data, uint16_t len);
typedef bool (*ina226_i2c_read_fn)(uint8_t dev_addr, uint8_t reg, uint8_t *data, uint16_t len);

typedef struct {
    uint8_t dev_addr;
    ina226_i2c_write_fn i2c_write;
    ina226_i2c_read_fn i2c_read;
    double current_lsb_a;    /* Ціна молодшого розряду струму в амперах */
    double power_lsb_w;      /* Ціна молодшого розряду потужності у ватах */
    uint16_t cal_val;        /* Розраховане значення регістра калібрування */
} ina226_handle_t;

static bool ina226_write_reg(ina226_handle_t *dev, uint8_t reg, uint16_t val) {
    uint8_t buf[2];
    buf[0] = (uint8_t)(val >> 8);    /* Старший байт (Big-Endian) */
    buf[1] = (uint8_t)(val & 0xFF);  /* Молодший байт */
    return dev->i2c_write(dev->dev_addr, reg, buf, 2);
}

static bool ina226_read_reg(ina226_handle_t *dev, uint8_t reg, uint16_t *val) {
    uint8_t buf[2];
    if (!dev->i2c_read(dev->dev_addr, reg, buf, 2)) {
        return false;
    }
    *val = ((uint16_t)buf[0] << 8) | buf[1];
    return true;
}

bool ina226_init(ina226_handle_t *dev, uint8_t addr, double r_shunt_ohms, double max_expected_current_a,
                 ina226_i2c_write_fn write_fn, ina226_i2c_read_fn read_fn) {
    dev->dev_addr = addr;
    dev->i2c_write = write_fn;
    dev->i2c_read = read_fn;

    /* Перевірка ідентифікатора виробника (TI = 0x5449) */
    uint16_t manuf_id = 0;
    if (!ina226_read_reg(dev, INA226_REG_MANUF_ID, &manuf_id) || manuf_id != 0x5449) {
        return false;
    }

    /* Програмне скидання мікросхеми */
    ina226_write_reg(dev, INA226_REG_CONFIG, INA226_RESET_BIT);

    /* Розрахунок ціни молодшого розряду: Current_LSB = Max_Current / 32768 */
    dev->current_lsb_a = max_expected_current_a / 32768.0;
    dev->power_lsb_w = 25.0 * dev->current_lsb_a;

    /* Розрахунок калібрувального коефіцієнта CAL = trunc(0.00512 / (Current_LSB * R_shunt)) */
    double cal = 0.00512 / (dev->current_lsb_a * r_shunt_ohms);
    dev->cal_val = (uint16_t)cal;

    /* Запис калібрувального значення у чіп */
    if (!ina226_write_reg(dev, INA226_REG_CALIBRATION, dev->cal_val)) {
        return false;
    }

    /* Налаштування режиму: усереднення на 16 вибірок, час перетворення 1.1 мс */
    uint16_t config = INA226_AVG_16 | INA226_VBUS_CT_1100US | INA226_VSH_CT_1100US | INA226_MODE_CONTINUOUS;
    return ina226_write_reg(dev, INA226_REG_CONFIG, config);
}

bool ina226_read_bus_voltage_mv(ina226_handle_t *dev, uint32_t *voltage_mv) {
    uint16_t raw = 0;
    if (!ina226_read_reg(dev, INA226_REG_BUSVOLTAGE, &raw)) {
        return false;
    }
    /* Крок напруги шини фіксований: 1.25 мВ / LSB */
    *voltage_mv = (uint32_t)((raw * 1250ULL) / 1000ULL);
    return true;
}

bool ina226_read_current_ma(ina226_handle_t *dev, int32_t *current_ma) {
    uint16_t raw = 0;
    if (!ina226_read_reg(dev, INA226_REG_CURRENT, &raw)) {
        return false;
    }
    int16_t signed_raw = (int16_t)raw;
    *current_ma = (int32_t)(signed_raw * dev->current_lsb_a * 1000.0);
    return true;
}

bool ina226_read_power_mw(ina226_handle_t *dev, uint32_t *power_mw) {
    uint16_t raw = 0;
    if (!ina226_read_reg(dev, INA226_REG_POWER, &raw)) {
        return false;
    }
    *power_mw = (uint32_t)(raw * dev->power_lsb_w * 1000.0);
    return true;
}

bool ina226_set_overcurrent_alert(ina226_handle_t *dev, double r_shunt_ohms, double limit_current_a) {
    /* Спад напруги на шунті для порогу струму: V_shunt_limit = I_limit * R_shunt */
    double v_shunt_v = limit_current_a * r_shunt_ohms;
    /* Крок регістра напруги шунта фіксований: 2.5 мкВ / LSB */
    int16_t limit_raw = (int16_t)(v_shunt_v / 0.0000025);

    if (!ina226_write_reg(dev, INA226_REG_ALERTLIMIT, (uint16_t)limit_raw)) {
        return false;
    }
    return ina226_write_reg(dev, INA226_REG_MASKENABLE, INA226_ALERT_SHUNT_OVER);
}
