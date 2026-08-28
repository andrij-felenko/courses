#include <cstdint>

namespace mcu::clock {

struct GpioPinConfig {
    uint32_t pin;
    uint32_t mode;
    uint32_t pull;
    uint32_t speed;
    uint32_t alternate;
};

class ClockVerifier {
public:
    enum class McoSource : uint32_t {
        None     = 0x00000000,
        SysClk   = 0x00000001,
        Msi      = 0x00000002,
        Hsi      = 0x00000003,
        Hse      = 0x00000004,
        PllClk   = 0x00000005,
        Lsi      = 0x00000006,
        Lse      = 0x00000007
    };

    enum class McoPrescaler : uint32_t {
        Div1  = 0x00000000,
        Div2  = 0x10000000,
        Div4  = 0x20000000,
        Div8  = 0x30000000,
        Div16 = 0x40000000
    };

    static void enable_mco_output(McoSource source, McoPrescaler div) noexcept {
        // Увімкнення тактування порту GPIOA та налаштування PA8 в режим AF0
        // Регістрова конфігурація бітів RCC_CFGR_MCOSEL та RCC_CFGR_MCOPRE
        (void)source;
        (void)div;
    }
};

} // namespace mcu::clock
