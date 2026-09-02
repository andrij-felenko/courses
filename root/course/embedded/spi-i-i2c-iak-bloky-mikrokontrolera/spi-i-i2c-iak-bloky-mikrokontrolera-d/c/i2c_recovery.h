#ifndef I2C_RECOVERY_H
#define I2C_RECOVERY_H

typedef enum {
    I2C_BUS_FREE = 0,   /* SDA була високою — лікувати нічого */
    I2C_BUS_RELEASED,   /* ведений відпустив лінію після тактів SCL */
    I2C_BUS_STUCK       /* SDA у нулі й після дев'яти тактів */
} i2c_recovery_t;

/* Викликати ДО ввімкнення блока I2C, при кожному старті системи */
i2c_recovery_t i2c1_bus_recover(void);

#endif /* I2C_RECOVERY_H */
