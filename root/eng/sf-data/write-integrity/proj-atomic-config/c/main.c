#include <stdint.h>
#include <stddef.h>

#define SLOT_A_ADDR  0x9000     // окремий сектор під слот A
#define SLOT_B_ADDR  0xA000     // окремий сектор під слот B (інший сектор!)

typedef struct {                // підпис, що РОБИТЬ слот дійсним
    uint32_t version;           // лічильник; більший = новіший
    uint32_t crc;               // CRC від payload, рахується перед записом
} footer_t;                     // пишеться ОСТАННІМ, цілим коротким записом

// дані лежать на початку сектора, підпис — у його кінці
#define FOOTER_OFFSET  (SECTOR_SIZE - sizeof(footer_t))

// прочитати версію дійсного слота, або 0, якщо слот недійсний
static uint32_t slot_version(uint32_t base) {
    footer_t f;
    flash_read(base + FOOTER_OFFSET, &f, sizeof f);
    uint8_t payload[sizeof(config_t)];
    flash_read(base, payload, sizeof payload);
    return (crc32(payload, sizeof payload) == f.crc) ? f.version : 0;
}

void save_config(const config_t *cfg) {
    uint32_t va = slot_version(SLOT_A_ADDR);
    uint32_t vb = slot_version(SLOT_B_ADDR);

    // пишемо в СТАРІШИЙ слот; новій копії — версія на 1 більша за найбільшу
    uint32_t target = (va <= vb) ? SLOT_A_ADDR : SLOT_B_ADDR;
    uint32_t next_v = ((va > vb) ? va : vb) + 1;

    flash_erase_sector(target);                       // 1) стерти (усі біти в 1)
    flash_write(target, cfg, sizeof *cfg);            // 2) записати дані

    footer_t f = { .version = next_v,
                   .crc = crc32(cfg, sizeof *cfg) };
    flash_write(target + FOOTER_OFFSET, &f, sizeof f); // 3) підпис — ОСТАННІМ
}
