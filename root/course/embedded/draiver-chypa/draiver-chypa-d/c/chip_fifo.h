/* chip_fifo.h — апаратний буфер відліків.
 *
 * Опитування готовності в циклі марнує і шину, і процесор. З буфером чип
 * сам накопичує десятки вибірок, а мікроконтролер прокидається раз на пакет
 * і забирає його однією швидкою транзакцією.
 */
#ifndef CHIP_FIFO_H
#define CHIP_FIFO_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "chip_dev.h"
#include "chip_status.h"

typedef struct {
    chip_fifo_mode_t mode;
    uint8_t          watermark; /* поріг у вибірках, 1..CHIP_FIFO_DEPTH-1 */
} chip_fifo_config_t;

/* Вмикає буфер і виставляє режим та поріг заповнення. Перед зміною режиму
 * буфер обов'язково проганяється через Bypass — інакше в ньому лишаються
 * відліки, набрані за старих налаштувань. */
chip_status_t chip_fifo_configure(chip_dev_t *dev, const chip_fifo_config_t *cfg);

/* Скидає накопичене, не міняючи режиму: Bypass і назад. */
chip_status_t chip_fifo_restart(chip_dev_t *dev);

/* Маршрутизує сигнал «досягнуто порогу» на вивід INT1. */
chip_status_t chip_fifo_enable_watermark_interrupt(chip_dev_t *dev, bool enable);

/* Скільки вибірок лежить у буфері й чи були втрати. */
chip_status_t chip_fifo_level(chip_dev_t *dev, uint8_t *samples,
                              bool *watermark_hit, bool *overrun);

/* Забирає з буфера до max_samples вибірок у фізичних одиницях SI.
 * Читає пачками по кілька вибірок за транзакцію — саме так пакет і
 * вичитують по DMA. Порожній буфер дає CHIP_ERR_NO_DATA. */
chip_status_t chip_fifo_read(chip_dev_t *dev, chip_accel_si_t *out,
                             size_t max_samples, size_t *read_samples);

#endif /* CHIP_FIFO_H */
