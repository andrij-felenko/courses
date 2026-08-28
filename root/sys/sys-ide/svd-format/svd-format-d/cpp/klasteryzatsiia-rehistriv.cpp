#include <cstdint>
#include <array>

struct DmaChannelRegisters {
    volatile uint32_t ccr;
    volatile uint32_t cndtr;
    volatile uint32_t cpar;
    volatile uint32_t cmar;
    uint32_t          reserved;
};

struct DmaRegisters {
    volatile uint32_t isr;
    volatile uint32_t ifcr;
    std::array<DmaChannelRegisters, 8> channels;
};
