#include <cstdint>

namespace diagnostic {

struct [[gnu::packed]] FaultContext {
    std::uint32_t r0{};
    std::uint32_t r1{};
    std::uint32_t r2{};
    std::uint32_t r3{};
    std::uint32_t r12{};
    std::uint32_t lr{};
    std::uint32_t pc{};
    std::uint32_t xpsr{};
    std::uint32_t msp{};
    std::uint32_t psp{};
    std::uint32_t cfsr{};
    std::uint32_t hfsr{};
    std::uint32_t mmfar{};
    std::uint32_t bfar{};
    std::uint32_t active_task{};
    std::uint32_t stack_high_water{};
};

} // namespace diagnostic
