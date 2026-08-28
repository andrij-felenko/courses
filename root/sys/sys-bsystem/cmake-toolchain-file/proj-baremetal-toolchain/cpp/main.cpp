// main.cpp — типізована робота з регістрами мікроконтролера через шаблони
#include <cstdint>

namespace mcu {

template <std::uintptr_t Addr>
struct Register {
    static void write(std::uint32_t val) noexcept {
        *reinterpret_cast<volatile std::uint32_t *>(Addr) = val;
    }

    [[nodiscard]] static std::uint32_t read() noexcept {
        return *reinterpret_cast<volatile std::uint32_t *>(Addr);
    }

    static void set_bits(std::uint32_t mask) noexcept {
        write(read() | mask);
    }

    static void clear_bits(std::uint32_t mask) noexcept {
        write(read() & ~mask);
    }
};

using RccAhb1Enr = Register<0x40023830>;
using GpiocModer = Register<0x40020800>;
using GpiocOdr   = Register<0x40020814>;

inline void delay(volatile std::uint32_t count) noexcept {
    while (count--) {
        asm volatile("nop");
    }
}

} // namespace mcu

extern "C" void main_app() noexcept {
    // Увімкнення тактування GPIOC (біт 2)
    mcu::RccAhb1Enr::set_bits(1U << 2);

    // Налаштування PC13 (режим виходу 0b01)
    mcu::GpiocModer::clear_bits(3U << (13 * 2));
    mcu::GpiocModer::set_bits(1U << (13 * 2));

    while (true) {
        mcu::GpiocOdr::write(mcu::GpiocOdr::read() ^ (1U << 13));
        mcu::delay(500000);
    }
}
