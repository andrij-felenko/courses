#include "flash_sim.h"

#include <string.h>

/* Вирівнювання на 4 — щоб копіювання заголовка з сектора не впиралося
   в невирівняний доступ на Cortex-M0. */
static uint8_t g_sector[FLASH_SLOT_COUNT][FLASH_SECTOR_SIZE] __attribute__((aligned(4)));
static bool    g_ready = false;

static void ensure_ready(void)
{
    if (!g_ready) {
        memset(g_sector, 0xFF, sizeof g_sector);
        g_ready = true;
    }
}

void flash_sim_wipe(void)
{
    memset(g_sector, 0xFF, sizeof g_sector);
    g_ready = true;
}

bool flash_erase(uint8_t slot)
{
    ensure_ready();
    if (slot >= FLASH_SLOT_COUNT) {
        return false;
    }
    memset(g_sector[slot], 0xFF, FLASH_SECTOR_SIZE);
    return true;
}

bool flash_program(uint8_t slot, size_t offset, const void *src, size_t len)
{
    ensure_ready();
    if (slot >= FLASH_SLOT_COUNT || src == NULL) {
        return false;
    }
    if (offset > FLASH_SECTOR_SIZE || len > (size_t)FLASH_SECTOR_SIZE - offset) {
        return false;
    }

    const uint8_t *in = (const uint8_t *)src;
    uint8_t *page = g_sector[slot] + offset;

    /* Спершу перевіряємо всю сторінку: відмова не має лишати запис наполовину. */
    for (size_t i = 0; i < len; ++i) {
        if ((page[i] & in[i]) != in[i]) {
            return false;   /* біт треба підняти 0 → 1, а це вміє лише стирання */
        }
    }
    for (size_t i = 0; i < len; ++i) {
        page[i] &= in[i];
    }
    return true;
}

const uint8_t *flash_map(uint8_t slot)
{
    ensure_ready();
    return (slot < FLASH_SLOT_COUNT) ? g_sector[slot] : NULL;
}
