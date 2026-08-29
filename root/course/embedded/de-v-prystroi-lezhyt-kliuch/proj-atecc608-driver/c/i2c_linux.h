/* Апаратний рівень для Linux: /dev/i2c-N через ioctl I2C_RDWR.
 * На мікроконтролері цей файл заміняє свій — драйвер про нього не знає. */
#ifndef I2C_LINUX_H
#define I2C_LINUX_H

#include <stdbool.h>

#include "atecc608.h"

typedef struct {
    int fd;
} i2c_linux;

/* Відкриває шину; шлях на кшталт "/dev/i2c-1". */
bool i2c_linux_open(i2c_linux *bus, const char *path);
void i2c_linux_close(i2c_linux *bus);

/* Зшиває шину з драйвером у структуру зворотних викликів. */
atecc_hal i2c_linux_hal(i2c_linux *bus);

#endif /* I2C_LINUX_H */
