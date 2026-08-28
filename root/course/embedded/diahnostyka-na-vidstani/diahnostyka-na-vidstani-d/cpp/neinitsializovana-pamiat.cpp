#include <cstdint>
#include <array>

namespace Diag {

constexpr uint32_t CrashMagicWord = 0xDEADBEEFU;

struct alignas(4) CrashDump {
    uint32_t magic{0};
    uint32_t boot_counter{0};
    uint32_t timestamp{0};
    uint32_t reset_reason{0};
    uint32_t r0{0}, r1{0}, r2{0}, r3{0};
    uint32_t r12{0}, lr{0}, pc{0}, xpsr{0};
    uint32_t hfsr{0}, cfsr{0}, mmfar{0}, bfar{0};
    uint32_t stack_len{0};
    std::array<uint32_t, 32> stack_data{};
    uint32_t crc32{0};
};

__attribute__((section(".noinit"))) static CrashDump g_crash_record;

} // namespace Diag
