#include <stdint.h>

// Спрощені адреси регістрів банку 1 FMC (у реальному коді — з CMSIS-заголовка МК).
#define FSMC_BCR1  (*(volatile uint32_t *)0xA0000000)  // керування банком
#define FSMC_BTR1  (*(volatile uint32_t *)0xA0000004)  // таймінги банку

void ext_sram_init(void) {
    // BTR: ADDSET = 1 такт (біти 0..3), DATAST = 6 тактів (біти 8..15).
    FSMC_BTR1 = (1u << 0) | (6u << 8);

    // BCR: MTYP=00 (SRAM), MWID=01 (16 біт, біти 4..5), MBKEN=1 — увімкнути банк (біт 0).
    FSMC_BCR1 = (0u << 2) | (1u << 4) | (1u << 0);
}

void ext_sram_demo(void) {
    // Зовнішня SRAM тепер — просто масив за адресою 0x6000_0000.
    volatile uint16_t *sram = (uint16_t *)0x60000000;

    sram[0]   = 0xBEEF;          // FMC сам зробить цикл запису на ніжках ~NE1/~NWE
    sram[100] = 0x1234;
    uint16_t back = sram[0];     // а це — цикл читання (~NE1/~NOE); back == 0xBEEF
    (void)back;
}
