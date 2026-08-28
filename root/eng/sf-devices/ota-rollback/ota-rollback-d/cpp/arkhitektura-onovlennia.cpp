#include <cstdint>

struct [[gnu::packed]] ImageVectorTable {
    uint32_t header{0x402000D1UL};
    uint32_t entry{0};
    uint32_t reserved1{0};
    uint32_t dcd{0};
    uint32_t bootData{0};
    uint32_t self{0};
    uint32_t csf{0};
    uint32_t reserved2{0};
};
