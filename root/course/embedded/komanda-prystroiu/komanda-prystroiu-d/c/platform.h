#ifndef PLATFORM_H
#define PLATFORM_H

/* Тонкий шар плати: монотонний час, незалежна пам'ять, радіоканал.
 * На справжньому МК тут були б esp_timer_get_time(), драйвер FRAM по SPI
 * і черга модема. Для заняття вони змодельовані так, щоб демонстрацію
 * можна було проганяти на робочій станції й керувати часом уручну. */

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

/* Монотонний лічильник мілісекунд від старту чипа: ніколи не йде назад,
 * не залежить від NTP і часових поясів. Саме ним міряються TTL. */
uint32_t plat_now_ms(void);

/* Просування модельного часу (у прошивці цю роль виконує апаратний таймер). */
void plat_advance_ms(uint32_t dt_ms);

/* Незалежна пам'ять (FRAM/EEPROM): переживає зникнення живлення. */
#define PLAT_NVM_SIZE 32u
void plat_nvm_read(uint8_t *dst);
void plat_nvm_write(const uint8_t *src);

/* Передача квитанції в радіоканал. Тут — розбір і друк кадру,
 * щоб на занятті було видно, ЩО саме полетіло на сервер. */
void plat_uplink_send(const uint8_t *frame, size_t len);

/* Скидання живлення: SRAM гине (структури перестворює виклик), монотонний
 * годинник починається з нуля, вміст FRAM лишається недоторканим. */
void plat_power_cycle(void);

/* Друк заголовка сценарію в демонстрації. */
void plat_banner(const char *text);

#endif /* PLATFORM_H */
