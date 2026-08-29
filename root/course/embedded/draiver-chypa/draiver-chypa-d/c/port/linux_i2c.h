/* port/linux_i2c.h — реалізація Рівня 1 поверх драйвера /dev/i2c-N.
 *
 * Це та сама «платформа», що на мікроконтролері зветься STM32 HAL чи ESP-IDF:
 * драйвер чипа про неї не знає нічого, крім таблиці функцій. Тут же видно, як
 * виглядає непрозорий контекст user_ctx у житті — це файловий дескриптор.
 */
#ifndef LINUX_I2C_H
#define LINUX_I2C_H

#include "../chip_bus.h"

typedef struct {
    int fd; /* дескриптор /dev/i2c-N, -1 якщо закрито */
} linux_i2c_bus_t;

/* Відкриває контролер шини. Повертає 0 або -errno. */
int linux_i2c_open(linux_i2c_bus_t *bus, const char *device_path);
void linux_i2c_close(linux_i2c_bus_t *bus);

/* Таблиця функцій для chip_config_t.bus_ops. */
const chip_bus_ops_t *linux_i2c_ops(void);

#endif /* LINUX_I2C_H */
