#include <cstdint>
#include <cstddef>
#include <array>

struct GuestContext {
    std::array<uint32_t, 4> regs{0, 0, 0, 0}; // R0, R1, R2, R3
    uint32_t                pc{0};            // Guest Program Counter
    uint32_t                zf{0};            // Zero Flag (1 або 0)
    bool                    halted{false};    // Прапорець завершення роботи
};
