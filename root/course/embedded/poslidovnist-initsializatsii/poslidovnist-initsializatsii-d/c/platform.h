#ifndef PLATFORM_H
#define PLATFORM_H

#include <stdint.h>
#include <stdbool.h>

/*
 * Контракт платформного шару: усе, чим драйвер торкається заліза.
 * На платі ці функції лягають на HAL мікроконтролера; для хоста їх реалізує
 * platform_sim.c — модель чипа з POR-затримкою, NACK-ами до виходу на режим,
 * самоочисним бітом скидання та залипанням лінії SDA.
 */

enum {
    BUS_OK        =  0,
    BUS_ERR_NACK  = -1, /* ведений не підтвердив байт: ще не прокинувся або відсутній */
    BUS_ERR_STUCK = -2  /* SDA притиснута до нуля — шину треба розблоковувати */
};

int i2c_write_reg(uint8_t dev_addr, uint8_t reg, uint8_t value);
int i2c_read_reg(uint8_t dev_addr, uint8_t reg, uint8_t *out_value);

uint32_t platform_get_millis(void);
void delay_ms(uint32_t ms);
void delay_us(uint32_t us);

/* Сторожовий таймер: його треба годувати навіть поки чип виходить на режим */
void hw_watchdog_kick(void);

/* Ключ живлення периферії (обидва давачі сидять на одній лінії VDD) */
void hw_power_rail_enable(bool on);

/* Виводи шини напряму — лише для процедури відновлення I2C */
void hw_i2c_pins_to_gpio(void);
void hw_i2c_pins_to_peripheral(void);
void hw_scl_set(bool level);
void hw_sda_set(bool level);
bool hw_sda_read(void);

/* Апаратний вивід NRST давача, якщо він розведений на платі */
bool hw_has_nrst(uint8_t dev_addr);
void hw_nrst_pulse(uint8_t dev_addr);

/* Реакція виробу на відмову */
void hw_fault_led(bool on);
void hw_actuators_disable(void);

/* Тільки для хостової моделі: розкладка стенда й сценарій завад */
void sim_reset_board(void);

#endif /* PLATFORM_H */
