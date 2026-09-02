#ifndef MODEM_HAL_H
#define MODEM_HAL_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Контракт плати: усе, чого автомат з'єднання потребує від заліза.
   Реалізацію пише файл підтримки конкретної плати — вона залежить від
   мікроконтролера, силового ключа й розводки UART. */

/* Монотонний лічильник мілісекунд. Переповнення через 49 діб безпечне:
   усі порівняння в автоматі рахують РІЗНИЦЮ, а не абсолютний час. */
uint32_t hal_now_ms(void);

/* Силовий P-канальний ключ VBAT_EN, що живить модем. */
void hal_modem_power_set(bool on);

/* Піни PWRKEY і RESET тримає автомат: тривалість імпульсу відмірюється
   неблокуюче, тому HAL лише перемикає рівень. */
void hal_modem_pwrkey_set(bool pressed);
void hal_modem_reset_set(bool asserted);

/* Пін STATUS модема: логічна одиниця = модуль запустився. */
bool hal_modem_status_pin(void);

void hal_uart_write(const uint8_t *data, size_t len);

/* RTS мікроконтролера: true = "я готовий приймати". */
void hal_uart_rts_set(bool ready);

uint16_t hal_vbat_mv(void);    /* напруга на шині живлення модема */
uint32_t hal_random_u32(void); /* джерело джиттеру для відкату */
void hal_watchdog_kick(void);

/* Пам'ять, що переживає знеструмлення: RTC Backup SRAM, EEPROM або NOR. */
bool hal_nv_read(void *dst, size_t len);
bool hal_nv_write(const void *src, size_t len);

void board_init(void);

#endif /* MODEM_HAL_H */
