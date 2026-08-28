#include <stdint.h>

static uint32_t regfile[32];   // 32 регістри по 32 біти

// два порти читання — комбінаційні: просто дивимось у масив
static inline uint32_t rf_read(uint8_t addr) {
    return regfile[addr & 31];        // 5-бітна адреса
}

// порт запису — «спрацьовує» на фронті такту (виклик = фронт)
static inline void rf_write_on_edge(uint8_t addr, uint32_t data, int wen) {
    if (wen) regfile[addr & 31] = data;
}
