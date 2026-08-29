/* chip_bus.h — Рівень 1: транспортна абстракція шини.
 *
 * У цьому файлі немає жодного #include бібліотек виробника мікроконтролера.
 * Платформа передає драйверу таблицю функцій; драйвер лише викликає їх і
 * повертає назад непрозорий контекст user_ctx.
 *
 * Контракт функцій шини:
 *   - повертають 0 при успіху й будь-яке від'ємне число при апаратній помилці;
 *   - виконують транзакцію повністю або не виконують зовсім (часткових читань
 *     драйвер не обробляє — це помилка);
 *   - reg — адреса регістру, ВЖЕ доповнена прапорцем автоінкременту, якщо
 *     викликач просить більше одного байта (див. chip_regops.c);
 *   - dev_addr — 7-бітна адреса I2C (без біта напрямку) або індекс лінії CS
 *     для SPI; зсув адреси на один біт робить платформа, не драйвер;
 *   - виклик блокуючий; якщо платформа використовує DMA — функція повертає
 *     керування лише після завершення передачі.
 */
#ifndef CHIP_BUS_H
#define CHIP_BUS_H

#include <stdbool.h>
#include <stdint.h>

typedef int32_t (*chip_bus_read_fn)(void *user_ctx, uint8_t dev_addr,
                                    uint8_t reg, uint8_t *data, uint16_t len);

typedef int32_t (*chip_bus_write_fn)(void *user_ctx, uint8_t dev_addr,
                                     uint8_t reg, const uint8_t *data, uint16_t len);

typedef void (*chip_delay_ms_fn)(uint32_t ms);

typedef struct {
    chip_bus_read_fn  read;
    chip_bus_write_fn write;
    chip_delay_ms_fn  delay_ms;
} chip_bus_ops_t;

/* Лінії SCL/SDA, переведені в режим звичайного GPIO заради аварійного
 * скидання шини. Виходи мусять бути типу «відкритий стік»: level = false
 * притискає лінію до землі, level = true відпускає її на резистор підтяжки.
 */
typedef struct {
    void (*scl_set)(void *user_ctx, bool level);
    void (*sda_set)(void *user_ctx, bool level);
    bool (*sda_get)(void *user_ctx);
    void (*delay_us)(uint32_t us);
    /* Повертає лінії периферії I2C з режиму GPIO назад під контролер шини.
     * Може бути NULL, якщо платформа робить це сама при реініціалізації. */
    void (*release)(void *user_ctx);
} chip_gpio_ops_t;

#endif /* CHIP_BUS_H */
