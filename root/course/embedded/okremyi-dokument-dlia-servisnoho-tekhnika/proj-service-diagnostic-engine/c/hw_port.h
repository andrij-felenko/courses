/* hw_port.h — контракт плати: те, чого сервісний рушій вимагає від BSP.
   Реалізація цих функцій живе у BSP конкретного виробу (регістри GPIO,
   ADC, UART, TRNG) і в цьому модулі свідомо відсутня. */
#ifndef HW_PORT_H
#define HW_PORT_H

#include <stdbool.h>
#include <stdint.h>

/* Біти апаратних захистів, які повертає hw_fault_flags() */
#define HW_FAULT_OVERTEMP    0x0001u
#define HW_FAULT_OVERCURRENT 0x0002u
#define HW_FAULT_UNDERVOLT   0x0004u

/* Скільки силових каналів має плата */
#define HW_RELAY_COUNT 2

/* Монотонний лічильник мілісекунд. Переповнюється раз на 49.7 доби —
   тому час порівнюємо різницею, а не оператором «більше» (див. reached()). */
uint32_t hw_get_tick_ms(void);
void     hw_delay_us(uint32_t us);
uint32_t hw_trng_get_random(void);

/* Блокуючий вивід у сервісний UART. З ISR НЕ викликати. */
void hw_uart_puts(const char *s);

void     hw_gpio_set_relay(uint8_t channel, bool on); /* channel 1..HW_RELAY_COUNT */
uint16_t hw_adc_read_raw(uint8_t channel);
uint32_t hw_fault_flags(void);

bool hw_eeprom_write(uint16_t addr, const void *data, uint16_t len);
bool hw_eeprom_read(uint16_t addr, void *data, uint16_t len);

/* Софтовий I2C: обидві лінії з відкритим стоком, підтяжка зовнішня.
   «release» = відпустити в третій стан, «low» = притиснути до нуля. */
void hw_i2c_sda_release(void);
void hw_i2c_sda_low(void);
bool hw_i2c_sda_read(void);
void hw_i2c_scl_release(void);
void hw_i2c_scl_low(void);
bool hw_i2c_scl_read(void);

/* Захоплення шини на час тесту. Голе залізо: BSP повертає true.
   Під RTOS ці дві функції реалізує srv_rtos.c через м'ютекс. */
bool hw_bus_try_lock(uint32_t timeout_ms);
void hw_bus_unlock(void);

#endif /* HW_PORT_H */
