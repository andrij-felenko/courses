#include <cstdint>
#include <array>
#include <span>
#include <expected>

namespace bringup {

struct Registers {
    static constexpr std::uintptr_t rcc_base   = 0x40023800U;
    static constexpr std::uintptr_t gpioa_base = 0x40020000U;
    static constexpr std::uintptr_t i2c1_base  = 0x40005400U;

    static volatile std::uint32_t& rcc_cr()   { return *reinterpret_cast<volatile std::uint32_t*>(rcc_base + 0x00U); }
    static volatile std::uint32_t& rcc_ahb1() { return *reinterpret_cast<volatile std::uint32_t*>(rcc_base + 0x30U); }
    static volatile std::uint32_t& gpio_moder(){ return *reinterpret_cast<volatile std::uint32_t*>(gpioa_base + 0x00U); }
    static volatile std::uint32_t& gpio_bsrr() { return *reinterpret_cast<volatile std::uint32_t*>(gpioa_base + 0x18U); }
    static volatile std::uint32_t& i2c_cr1()  { return *reinterpret_cast<volatile std::uint32_t*>(i2c1_base + 0x00U); }
    static volatile std::uint32_t& i2c_sr1()  { return *reinterpret_cast<volatile std::uint32_t*>(i2c1_base + 0x14U); }
    static volatile std::uint32_t& i2c_sr2()  { return *reinterpret_cast<volatile std::uint32_t*>(i2c1_base + 0x18U); }
    static volatile std::uint32_t& i2c_dr()   { return *reinterpret_cast<volatile std::uint32_t*>(i2c1_base + 0x10U); }
};

enum class Error : std::uint8_t {
    hse_timeout,
    pll_timeout,
    i2c_timeout,
    i2c_nack
};

struct ClockStatus {
    bool hsi_ready{false};
    bool hse_ready{false};
    bool pll_ready{false};
};

class BringupRunner {
public:
    static void delay(std::uint32_t count) noexcept {
        volatile std::uint32_t c = count;
        while (c > 0) {
            --c;
        }
    }

    static std::expected<ClockStatus, Error> verify_clocks() noexcept {
        ClockStatus status;
        constexpr std::uint32_t hsirdy_mask = (1U << 1);
        constexpr std::uint32_t hseon_mask  = (1U << 16);
        constexpr std::uint32_t hserdy_mask = (1U << 17);
        constexpr std::uint32_t pllrdy_mask = (1U << 25);

        status.hsi_ready = (Registers::rcc_cr() & hsirdy_mask) != 0;

        Registers::rcc_cr() |= hseon_mask;
        std::uint32_t timeout = 50000;
        while (!(Registers::rcc_cr() & hserdy_mask) && timeout > 0) {
            --timeout;
        }
        
        status.hse_ready = (timeout > 0);
        if (!status.hse_ready) {
            return std::unexpected(Error::hse_timeout);
        }

        status.pll_ready = (Registers::rcc_cr() & pllrdy_mask) != 0;
        return status;
    }

    static void exerciser_testpoints(std::span<const std::uint8_t> pins, std::uint32_t cycles) noexcept {
        Registers::rcc_ahb1() |= (1U << 0);

        for (auto pin : pins) {
            Registers::gpio_moder() &= ~(3U << (pin * 2));
            Registers::gpio_moder() |=  (1U << (pin * 2));
        }

        for (std::uint32_t i = 0; i < cycles; ++i) {
            std::uint32_t set_mask = 0;
            std::uint32_t reset_mask = 0;
            for (auto pin : pins) {
                set_mask |= (1U << pin);
                reset_mask |= (1U << (pin + 16));
            }
            Registers::gpio_bsrr() = set_mask;
            delay(1000);
            Registers::gpio_bsrr() = reset_mask;
            delay(1000);
        }
    }

    static std::expected<void, Error> probe_i2c_device(std::uint8_t address_7bit) noexcept {
        constexpr std::uint32_t start_bit = (1U << 8);
        constexpr std::uint32_t stop_bit  = (1U << 9);
        constexpr std::uint32_t sb_flag   = (1U << 0);
        constexpr std::uint32_t addr_flag = (1U << 1);
        constexpr std::uint32_t af_flag   = (1U << 10);

        Registers::i2c_cr1() |= start_bit;
        std::uint32_t timeout = 20000;
        while (!(Registers::i2c_sr1() & sb_flag) && timeout > 0) {
            --timeout;
        }
        if (timeout == 0) {
            Registers::i2c_cr1() |= stop_bit;
            return std::unexpected(Error::i2c_timeout);
        }

        Registers::i2c_dr() = static_cast<std::uint32_t>(address_7bit << 1);
        timeout = 20000;
        while (!(Registers::i2c_sr1() & (addr_flag | af_flag)) && timeout > 0) {
            --timeout;
        }

        if (Registers::i2c_sr1() & af_flag) {
            Registers::i2c_sr1() &= ~af_flag;
            Registers::i2c_cr1() |= stop_bit;
            return std::unexpected(Error::i2c_nack);
        }

        static_cast<void>(Registers::i2c_sr1());
        static_cast<void>(Registers::i2c_sr2());
        Registers::i2c_cr1() |= stop_bit;
        return {};
    }
};

} // namespace bringup
