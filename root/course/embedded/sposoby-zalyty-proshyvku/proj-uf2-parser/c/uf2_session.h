/*
 * Сеанс завантаження образу: приймає перевірені блоки, стирає Flash рівно
 * один раз на сектор і сам бачить момент, коли образ зібрано повністю.
 */
#ifndef UF2_SESSION_H
#define UF2_SESSION_H

#include "uf2_block.h"

#define UF2_FLASH_SECTOR_SIZE 4096u /* гранула стирання NOR Flash */

/*
 * Стелі бітових карт. 8192 блоків × 256 байтів = 2 МіБ образу (карта — 1 КіБ RAM);
 * 4096 секторів × 4 КіБ = 16 МіБ адресного простору (карта — 512 байтів RAM).
 */
#define UF2_MAX_BLOCKS  8192u
#define UF2_MAX_SECTORS 4096u

typedef struct {
    uint32_t family_id;
    uint32_t flash_start;
    uint32_t flash_size;
    uint32_t total_blocks;   /* 0, поки не прийшов перший блок */
    uint32_t handled_blocks; /* скільки РІЗНИХ блоків уже опрацьовано */
    uint32_t block_mask[UF2_MAX_BLOCKS / 32];
    uint32_t erased_mask[UF2_MAX_SECTORS / 32];
} uf2_session_t;

void uf2_session_init(uf2_session_t *s,
                      uint32_t       family_id,
                      uint32_t       flash_start,
                      uint32_t       flash_size);

/*
 * Головний вхід: сирий сектор від USB. Розбирає, стирає за потреби, пише
 * у Flash і зводить бітову карту. Повертає UF2_OK, UF2_SKIPPED або відмову.
 */
uf2_status_t uf2_session_accept_sector(uf2_session_t *s,
                                       const uint8_t *sector,
                                       uint32_t       sector_len);

/* true, коли всі num_blocks бітів карти виставлені. */
bool uf2_session_complete(const uf2_session_t *s);

/*
 * Контракт порту: реалізується під конкретний кристал (див. uf2_msc.c).
 * address — абсолютна адреса у просторі Flash, вирівняна на сектор для стирання.
 */
bool uf2_flash_erase_sector(uint32_t address);
bool uf2_flash_program(uint32_t address, const uint8_t *data, uint32_t length);

#endif /* UF2_SESSION_H */
