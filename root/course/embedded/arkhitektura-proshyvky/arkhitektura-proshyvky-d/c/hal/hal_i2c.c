/* hal/hal_i2c.c — регістрові помічники поверх таблиці операцій.
 * Увесь код тут переносний: він не згадує жодного регістра контролера,
 * лише розкладає «прочитати регістр» на виклики, які надав порт. */
#include "hal/hal_i2c.h"

bool hal_i2c_bus_is_valid(const hal_i2c_bus_t *bus)
{
    return bus != 0 && bus->ops != 0 && bus->ops->write != 0 && bus->ops->read != 0;
}

const char *hal_i2c_status_str(hal_i2c_status_t status)
{
    switch (status) {
    case HAL_I2C_OK:          return "OK";
    case HAL_I2C_ERR_NACK:    return "NACK";
    case HAL_I2C_ERR_BUS:     return "BUS";
    case HAL_I2C_ERR_TIMEOUT: return "TIMEOUT";
    case HAL_I2C_ERR_ARG:     return "ARG";
    default:                  return "?";
    }
}

hal_i2c_status_t hal_i2c_read_regs(const hal_i2c_bus_t *bus, uint8_t dev_addr,
                                   uint8_t reg_addr, uint8_t *dst, size_t len)
{
    if (!hal_i2c_bus_is_valid(bus) || dst == 0 || len == 0u) {
        return HAL_I2C_ERR_ARG;
    }

    if (bus->ops->write_read != 0) {
        return bus->ops->write_read(bus->ctx, dev_addr, &reg_addr, 1u, dst, len);
    }

    /* Порт не вміє повторного START: віддаємо адресу регістра окремою
     * транзакцією. Між викликами шина відпускається, тож у системі з двома
     * майстрами така пара може перерватися — про це знає лише HAL. */
    const hal_i2c_status_t st = bus->ops->write(bus->ctx, dev_addr, &reg_addr, 1u);
    if (st != HAL_I2C_OK) {
        return st;
    }
    return bus->ops->read(bus->ctx, dev_addr, dst, len);
}

hal_i2c_status_t hal_i2c_read_reg(const hal_i2c_bus_t *bus, uint8_t dev_addr,
                                  uint8_t reg_addr, uint8_t *value)
{
    return hal_i2c_read_regs(bus, dev_addr, reg_addr, value, 1u);
}

hal_i2c_status_t hal_i2c_write_reg(const hal_i2c_bus_t *bus, uint8_t dev_addr,
                                   uint8_t reg_addr, uint8_t value)
{
    if (!hal_i2c_bus_is_valid(bus)) {
        return HAL_I2C_ERR_ARG;
    }
    const uint8_t frame[2] = { reg_addr, value };
    return bus->ops->write(bus->ctx, dev_addr, frame, sizeof frame);
}

hal_i2c_status_t hal_i2c_write_reg_verify(const hal_i2c_bus_t *bus, uint8_t dev_addr,
                                          uint8_t reg_addr, uint8_t value)
{
    hal_i2c_status_t st = hal_i2c_write_reg(bus, dev_addr, reg_addr, value);
    if (st != HAL_I2C_OK) {
        return st;
    }

    uint8_t readback = 0u;
    st = hal_i2c_read_reg(bus, dev_addr, reg_addr, &readback);
    if (st != HAL_I2C_OK) {
        return st;
    }
    return (readback == value) ? HAL_I2C_OK : HAL_I2C_ERR_BUS;
}

hal_i2c_status_t hal_i2c_probe(const hal_i2c_bus_t *bus, uint8_t dev_addr)
{
    if (!hal_i2c_bus_is_valid(bus)) {
        return HAL_I2C_ERR_ARG;
    }
    return bus->ops->write(bus->ctx, dev_addr, 0, 0u);
}
