#include <cstdint>
#include <array>

namespace SystemPower {

struct GpioBlock {
    volatile std::uint32_t moder;
    volatile std::uint32_t otyper;
    volatile std::uint32_t ospeedr;
    volatile std::uint32_t pupdr;
    volatile std::uint32_t idr;
    volatile std::uint32_t odr;
    volatile std::uint32_t bsrr;
};

inline auto& port_a = *reinterpret_cast<GpioBlock*>(0x48000000UL);
inline auto& port_b = *reinterpret_cast<GpioBlock*>(0x48000400UL);
inline auto& dbgmcu_cr = *reinterpret_cast<volatile std::uint32_t*>(0xE0042004UL);

class LowPowerController {
public:
    static void prepare_pins_and_sleep() noexcept {
        /* 1. Ізоляція шин даних */
        port_a.odr &= ~((1U << 2) | (1U << 3) | (1U << 5) | (1U << 7));

        /* 2. Закриття ключа живлення датчиків (PB12 HIGH) */
        port_b.bsrr = (1U << 12);

        /* 3. Порт A: всі в Analog mode, зберігаючи конфігурацію Wakeup PA0 */
        port_a.moder = 0xFFFFFFFCUL | (port_a.moder & 0x03UL);
        port_a.pupdr = 0x00000000UL | (port_a.pupdr & 0x03UL);

        /* 4. Порт B: всі в Analog mode, зберігаючи вихід ключа PB12 */
        constexpr std::uint32_t pb12_mask = (0b11U << (12 * 2));
        port_b.moder = (~pb12_mask) | (0b01U << (12 * 2));
        port_b.pupdr = 0x00000000UL;

        /* 5. Вимкнення блоку налагодження */
        dbgmcu_cr = 0x00000000UL;

        /* Вхід у сон */
        asm volatile("wfi");
    }
};

} // namespace SystemPower
