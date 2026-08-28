#include <cstdint>
#include <array>

struct [[gnu::packed]] CrashDump {
    uint32_t                magic{0xDEADBEEFUL};
    uint32_t                resetReason{0};
    uint32_t                cfsr{0};
    uint32_t                hfsr{0};
    uint32_t                mmar{0};
    uint32_t                bfar{0};
    uint32_t                pc{0};
    uint32_t                lr{0};
    uint32_t                sp{0};
    std::array<uint32_t, 64> stackSnapshot{};
    uint32_t                dumpCrc{0};
};

[[gnu::section(".noinit")]] static CrashDump g_crashDump;
