/* Ведучий I2C, зібраний вручну з двох GPIO: адресна транзакція
   нульової довжини та процедура виведення шини із зависання. */
#ifndef I2C_BITBANG_H
#define I2C_BITBANG_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    I2C_OK = 0,
    I2C_NACK,             /* адресний байт видано, підтвердження на 9-му такті немає */
    I2C_LINES_BUSY,       /* SDA лежить у нулі ще до умови START */
    I2C_STRETCH_TIMEOUT,  /* SCL не піднімається: немає підтяжки або ведений тримає такт */
    I2C_STOP_FAILED       /* після умови STOP лінія SDA не піднялася */
} i2c_status_t;

const char *i2c_status_text(i2c_status_t st);

/* Рівні обох ліній у стані спокою: справна шина дає 1 і 1 */
typedef struct {
    bool scl_high;
    bool sda_high;
} i2c_idle_state_t;

i2c_idle_state_t i2c_read_idle_state(void);

/* Дев'ять тактів SCL і примусовий STOP.
   true — SDA відпущена; false — лінія тримається нулем і після дев'ятого такту. */
bool i2c_recover_bus(void);

/* START + адресний байт (запис) + читання ACK + STOP */
i2c_status_t i2c_probe(uint8_t addr7);

#endif /* I2C_BITBANG_H */
