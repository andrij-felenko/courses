/* platform.h — усе, чого драйвер АЦП хоче від плати, і нічого більше.
 *
 * Межа навмисно вузька: SPI, лінія DRDY, час. Драйвер не знає ні про HAL,
 * ні про конкретний мікроконтролер — на іншій платі міняється лише
 * platform_stm32.c.
 */
#ifndef PLATFORM_H
#define PLATFORM_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Тактування, GPIO, SPI, UART. Кличеться один раз на самому початку main(). */
void board_init(void);

/* Керування лінією вибору кристала (CS активний низьким рівнем). */
void board_spi_select(void);
void board_spi_release(void);

/* Повнодуплексний обмін: одночасно віддаємо len байтів із tx і збираємо len
 * байтів у rx. Повертає false, коли контролер SPI не вклався у свій таймаут —
 * це вже апаратна відмова, а не «дані трохи затрималися». */
bool board_spi_transfer(const uint8_t *tx, uint8_t *rx, size_t len);

/* Стан виводу DRDY мікросхеми АЦП: true, коли готовий новий результат.
 * Вивід активний низьким рівнем, інверсію ховаємо тут. */
bool board_adc_data_ready(void);

/* Монотонний лічильник мілісекунд від старту. Переповнення через 49 діб
 * нікого не турбує: усі порівняння в коді робляться на різницях беззнакових
 * величин, а вони переповнення переживають правильно. */
uint32_t board_millis(void);

void board_delay_ms(uint32_t ms);

#endif /* PLATFORM_H */
