#include <stdio.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <linux/i2c.h>

#define BATTERY_ADDR 0x0B
#define CMD_VOLTAGE  0x09

int main(void) {
    int file = open("/dev/i2c-0", O_RDWR);
    if (file < 0) {
        perror("Не вдалося відкрити I2C пристрій");
        return 1;
    }

    /* Встановлення адреси веденого пристрою */
    if (ioctl(file, I2C_SLAVE, BATTERY_ADDR) < 0) {
        perror("Помилка встановлення адреси веденого");
        close(file);
        return 1;
    }

    /* Увімкнення апаратного/програмного контролю PEC в ядрі */
    if (ioctl(file, I2C_PEC, 1) < 0) {
        perror("Попередження: контролер не підтримує I2C_PEC");
    }

    union i2c_smbus_data data;
    struct i2c_smbus_ioctl_data args = {
        .read_write = I2C_SMBUS_READ,
        .command = CMD_VOLTAGE,
        .size = I2C_SMBUS_WORD_DATA,
        .data = &data
    };

    if (ioctl(file, I2C_SMBUS, &args) < 0) {
        perror("Помилка виконання транзакції SMBus Read Word");
        close(file);
        return 1;
    }

    printf("Напруга акумулятора: %u мВ\n", data.word);
    close(file);
    return 0;
}
