/*
 * Контракт платформного шару — усе, що драйвер знає про залізо під собою.
 *
 * Тут немає жодного #include конкретного HAL: файл однаково збирається
 * під Cortex-M, RISC-V і під x86_64 у юніт-тестах. Вимагає C11 (_Alignas,
 * _Static_assert).
 */
#ifndef CHIP_BUS_H
#define CHIP_BUS_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди, якими платформа звітує драйверові. Драйвер розрізняє рівно три
 * випадки: успіх, збій лінії та вичерпаний час — більшого йому не треба,
 * а платформа не мусить вигадувати спільний словник помилок. */
#define CHIP_BUS_OK             0
#define CHIP_BUS_ERR_IO       (-1)
#define CHIP_BUS_ERR_TIMEOUT  (-2)

/*
 * Пакетне читання регістрів.
 *
 * Реалізація зобовʼязана виконати неподільну транзакцію:
 *   START · адреса+W · reg_addr · Repeated Start · адреса+R · len байтів · STOP.
 * Якщо на шині кілька пристроїв — захоплення й звільнення мʼютекса шини
 * лежить тут, а не в драйвері датчика.
 *
 * Нескінченного опитування апаратних прапорців бути не може: обрив SDA чи SCL
 * мусить завершитися CHIP_BUS_ERR_TIMEOUT, а не зависанням задачі.
 *
 * Якщо транзакцію виконує DMA і на ядрі увімкнено кеш даних, інвалідація
 * (SCB_InvalidateDCache_by_Addr) робиться ТУТ, перед поверненням керування:
 * драйвер читає data[] відразу після виходу з функції й застарілих рядків
 * кешу не переживе.
 *
 * dev_addr — 7-бітна адреса на шині; user_ctx — непрозорий хендл платформи
 * (I2C_HandleTypeDef*, файловий дескриптор, вказівник на мʼютекс). Драйвер
 * не розіменовує user_ctx ніколи й нічого не припускає про його тип.
 */
typedef int32_t (*chip_bus_read_fn)(uint8_t dev_addr,
                                    uint8_t reg_addr,
                                    uint8_t *data,
                                    uint16_t len,
                                    void *user_ctx);

typedef int32_t (*chip_bus_write_fn)(uint8_t dev_addr,
                                     uint8_t reg_addr,
                                     const uint8_t *data,
                                     uint16_t len,
                                     void *user_ctx);

/* Квантована затримка. Драйвер викликає її лише з контексту задачі —
 * жодна функція, що чіпає delay_ms, не є ISR-безпечною. */
typedef void (*chip_delay_ms_fn)(uint32_t ms, void *user_ctx);

typedef struct {
    chip_bus_read_fn  read;
    chip_bus_write_fn write;
    chip_delay_ms_fn  delay_ms;
} chip_bus_ops_t;

/* Розмір рядка кешу на Cortex-M7/Cortex-A. Буфери під DMA вирівнюємо саме
 * за ним, інакше інвалідація зачепить сусідні змінні (false sharing). */
#define CHIP_CACHE_LINE 32u

#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 201112L
#  define CHIP_DMA_ALIGNED _Alignas(CHIP_CACHE_LINE)
#  define CHIP_STATIC_ASSERT(cond, msg) _Static_assert(cond, msg)
#elif defined(__GNUC__)
#  define CHIP_DMA_ALIGNED __attribute__((aligned(CHIP_CACHE_LINE)))
#  define CHIP_STATIC_ASSERT(cond, msg) extern char chip_sa[(cond) ? 1 : -1]
#else
#  error "Потрібен C11 або GCC-сумісні розширення: драйвер вимагає вирівнювання під DMA"
#endif

/* Сам буфер розміщує викликач — і саме він відповідає за те, щоб буфер лежав
 * у пам'яті, доступній контролеру DMA (звичайний SRAM, а не DTCM/CCM):
 *     static CHIP_DMA_SECTION chip_fifo_buf_t g_fifo;
 * де CHIP_DMA_SECTION — атрибут секції з лінкер-скрипта плати. Драйвер про
 * карту пам'яті конкретної плати не знає нічого. */

#ifdef __cplusplus
}
#endif

#endif /* CHIP_BUS_H */
