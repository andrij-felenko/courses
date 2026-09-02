/* Контракт ліній I2C, виведених у режим GPIO з відкритим стоком.
   Ці функції реалізує плата: у прошивці — записом у регістри порту,
   у цьому прикладі — моделлю шини із sim_lines.c. */
#ifndef I2C_LINES_H
#define I2C_LINES_H

#include <stdbool.h>
#include <stdint.h>

/* Забрати виводи в GPIO (альтернативну функцію апаратного блоку I2C вимкнено) */
void i2c_lines_take(void);

/* Повернути виводи апаратному блоку I2C — після діагностики */
void i2c_lines_release_to_peripheral(void);

/* Відкритий стік: "відпустити" — це вхід, і лінію піднімає підтяжка;
   "притиснути" — це вихід у нуль. Високий рівень не формує ніхто. */
void i2c_scl_release(void);
void i2c_scl_drive_low(void);
bool i2c_scl_read(void);

void i2c_sda_release(void);
void i2c_sda_drive_low(void);
bool i2c_sda_read(void);

void i2c_delay_us(uint32_t us);

#endif /* I2C_LINES_H */
