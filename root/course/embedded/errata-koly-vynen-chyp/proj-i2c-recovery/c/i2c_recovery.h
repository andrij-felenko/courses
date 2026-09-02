#ifndef I2C_RECOVERY_H
#define I2C_RECOVERY_H

#include <stdint.h>

/* Чим скінчилося ручне рятування шини I2C1 (PB6 = SCL, PB7 = SDA) */
typedef enum {
    I2C_BUS_OK = 0,      /* лінії у спокої, виводи повернуто модулю I2C1 */
    I2C_BUS_SCL_STUCK,   /* такт не піднімається: вічне розтягування або КЗ на землю */
    I2C_BUS_SDA_STUCK    /* дев'ять тактів не звільнили дані: мертвий чип або КЗ */
} i2c_bus_status_t;

typedef struct {
    i2c_bus_status_t status;
    uint8_t pulses;      /* скільки тактів довелося видати; 0 — шина була вільна */
} i2c_bus_report_t;

/* Уся процедура з п'яти кроків: скидання модуля через RCC, перехоплення виводів
   у GPIO Open-Drain, до дев'яти ручних тактів SCL, ручний STOP, перевірка ліній.
   Після I2C_BUS_OK виводи стоять в Alternate Function Open-Drain, модуль виведено
   зі скидання й він чекає на i2c1_init(). При будь-якій помилці модуль лишається
   У СКИДАННІ: шина фізично несправна, вмикати на ній передавач нічого. */
i2c_bus_report_t i2c1_bus_recover(void);

#endif /* I2C_RECOVERY_H */
