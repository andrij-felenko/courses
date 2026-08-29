/* flash_sim.h — модель двох секторів Flash. Поводиться як справжня пам'ять:
   стерте — це 0xFF, а програмування вміє лише гасити біти (1 → 0). */
#ifndef FLASH_SIM_H
#define FLASH_SIM_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define FLASH_SLOT_COUNT   2u
#define FLASH_SECTOR_SIZE  256u

/* Стан пам'яті з конвеєра: обидва сектори стерті. */
void flash_sim_wipe(void);

bool flash_erase(uint8_t slot);
bool flash_program(uint8_t slot, size_t offset, const void *src, size_t len);

/* Сектор читається напряму, як пам'ять (memory-mapped Flash). */
const uint8_t *flash_map(uint8_t slot);

#endif /* FLASH_SIM_H */
