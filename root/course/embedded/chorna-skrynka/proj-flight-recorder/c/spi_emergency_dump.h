/* spi_emergency_dump.h — автономне вивантаження тому в SPI FRAM або NOR Flash.
 * Жодного DMA, жодних переривань, жодної RTOS: усе опитуванням регістрів. */
#ifndef BLACKBOX_SPI_EMERGENCY_DUMP_H
#define BLACKBOX_SPI_EMERGENCY_DUMP_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    BB_FLUSH_OK = 0,
    BB_FLUSH_TIMEOUT,     /* SPI не відповів у відведену кількість обертів */
    BB_FLUSH_NO_DEVICE,   /* мікросхема не підняла біт дозволу запису */
    BB_FLUSH_NOT_ERASED   /* сектор NOR Flash не стерли заздалегідь */
} BlackBoxFlushStatus_t;

/* FRAM пише на швидкості шини й не потребує стирання: увесь том іде однією
 * транзакцією. Це шлях для аварії — від виклику до останнього байта мілісекунди. */
BlackBoxFlushStatus_t spi_emergency_write(uint32_t dst_addr);

/* NOR Flash програмує сторінками по 256 байтів і лише в стерті комірки, тож
 * сектор під дамп стирають ЗАЗДАЛЕГІДЬ, на справному запуску. */
BlackBoxFlushStatus_t spi_flash_erase_slot(uint32_t dst_addr);
BlackBoxFlushStatus_t spi_emergency_write_flash(uint32_t dst_addr);

#ifdef __cplusplus
}
#endif

#endif /* BLACKBOX_SPI_EMERGENCY_DUMP_H */
