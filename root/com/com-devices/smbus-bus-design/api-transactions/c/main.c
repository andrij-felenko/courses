#include <linux/i2c.h>
#include <linux/i2c-dev.h>
#include <stdint.h>

#define I2C_SMBUS_QUICK             0
#define I2C_SMBUS_BYTE              1
#define I2C_SMBUS_BYTE_DATA         2
#define I2C_SMBUS_WORD_DATA         3
#define I2C_SMBUS_PROC_CALL         4
#define I2C_SMBUS_BLOCK_DATA        5
#define I2C_SMBUS_I2C_BLOCK_DATA    8
#define I2C_SMBUS_BLOCK_PROC_CALL   9

#define I2C_SMBUS_READ  1
#define I2C_SMBUS_WRITE 0

union i2c_smbus_data {
    uint8_t  byte;
    uint16_t word;
    uint8_t  block[I2C_SMBUS_BLOCK_MAX + 2]; /* block[0] = лічильник довжини */
};

struct i2c_smbus_ioctl_data {
    uint8_t read_write;                  /* I2C_SMBUS_READ або I2C_SMBUS_WRITE */
    uint8_t command;                     /* Код команди (Command Code) */
    uint32_t size;                       /* Тип транзакції (I2C_SMBUS_*) */
    union i2c_smbus_data *data;          /* Покажчик на буфер даних */
};
