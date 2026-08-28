#include <cstddef>
#include <cstdint>

struct SpiRegisters {
    volatile uint32_t cr1;
    volatile uint32_t cr2;
    uint8_t           reserved0[8];
    volatile uint32_t sr;
    volatile uint32_t dr;
};

static_assert(offsetof(SpiRegisters, cr1) == 0x00, "SPI cr1 offset mismatch!");
static_assert(offsetof(SpiRegisters, cr2) == 0x04, "SPI cr2 offset mismatch!");
static_assert(offsetof(SpiRegisters, sr)  == 0x10, "SPI sr offset mismatch!");
static_assert(offsetof(SpiRegisters, dr)  == 0x14, "SPI dr offset mismatch!");
static_assert(sizeof(SpiRegisters)        == 0x18, "SPI struct size mismatch!");
