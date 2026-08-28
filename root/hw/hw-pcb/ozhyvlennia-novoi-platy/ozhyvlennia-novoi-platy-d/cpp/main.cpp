// Bringup SWD Low-Level Master Driver (Idiomatic C++20)
#include <cstdint>
#include <concepts>
#include <expected>
#include <span>
#include <bit>

enum class SwdError : uint8_t {
    AckWait,
    AckFault,
    AckProtocolError,
    ParityMismatch,
    Timeout
};

template <typename GpioDriver>
concept SwdGpioInterface = requires(GpioDriver gpio, bool level, uint32_t cycles) {
    { gpio.set_swclk(level) } -> std::same_as<void>;
    { gpio.set_swdio(level) } -> std::same_as<void>;
    { gpio.get_swdio() } -> std::same_as<bool>;
    { gpio.set_swdio_dir_out(level) } -> std::same_as<void>;
    { gpio.delay_cycles(cycles) } -> std::same_as<void>;
};

template <SwdGpioInterface Gpio>
class SwdMaster {
public:
    explicit constexpr SwdMaster(Gpio& gpio) noexcept : gpio_{gpio} {}

    void line_reset() noexcept {
        gpio_.set_swdio_dir_out(true);
        gpio_.set_swdio(true);
        for (std::size_t i = 0; i < 56; ++i) {
            clock_pulse();
        }
    }

    void switch_jtag_to_swd() noexcept {
        constexpr uint16_t seq = 0xE79E; // LSB-first для 0x79E7
        gpio_.set_swdio_dir_out(true);
        for (std::size_t i = 0; i < 16; ++i) {
            gpio_.set_swdio(((seq >> i) & 1) != 0);
            clock_pulse();
        }
    }

    [[nodiscard]] std::expected<uint32_t, SwdError> read_dp_register(uint8_t addr_reg) noexcept {
        uint8_t req = 0x81 | static_cast<uint8_t>((addr_reg & 0x0C) << 1);
        uint8_t parity = ((req >> 1) ^ (req >> 2) ^ (req >> 3) ^ (req >> 4)) & 1;
        req |= static_cast<uint8_t>(parity << 5);

        // 1. Відправка Host Request
        gpio_.set_swdio_dir_out(true);
        for (std::size_t i = 0; i < 8; ++i) {
            gpio_.set_swdio(((req >> i) & 1) != 0);
            clock_pulse();
        }

        // 2. Turnaround
        gpio_.set_swdio_dir_out(false);
        clock_pulse();

        // 3. Читання 3-бітного ACK
        uint8_t ack = 0;
        for (std::size_t i = 0; i < 3; ++i) {
            gpio_.set_swclk(false);
            gpio_.delay_cycles(2);
            if (gpio_.get_swdio()) {
                ack |= static_cast<uint8_t>(1 << i);
            }
            gpio_.set_swclk(true);
            gpio_.delay_cycles(2);
        }

        if (ack == 0x02) return std::unexpected(SwdError::AckWait);
        if (ack == 0x04) return std::unexpected(SwdError::AckFault);
        if (ack != 0x01) return std::unexpected(SwdError::AckProtocolError);

        // 4. Читання 32-бітного значення Data
        uint32_t data = 0;
        for (std::size_t i = 0; i < 32; ++i) {
            gpio_.set_swclk(false);
            gpio_.delay_cycles(2);
            if (gpio_.get_swdio()) {
                data |= (1UL << i);
            }
            gpio_.set_swclk(true);
            gpio_.delay_cycles(2);
        }

        // 5. Читання біта парності
        gpio_.set_swclk(false);
        gpio_.delay_cycles(2);
        const bool rcv_parity = gpio_.get_swdio();
        gpio_.set_swclk(true);
        gpio_.delay_cycles(2);

        // 6. Завершення транзакції (Idle cycles)
        gpio_.set_swdio_dir_out(true);
        gpio_.set_swdio(false);
        for (std::size_t i = 0; i < 4; ++i) {
            clock_pulse();
        }

        const bool calc_parity = (std::popcount(data) % 2) != 0;
        if (rcv_parity != calc_parity) {
            return std::unexpected(SwdError::ParityMismatch);
        }

        return data;
    }

private:
    void clock_pulse() noexcept {
        gpio_.set_swclk(false);
        gpio_.delay_cycles(2);
        gpio_.set_swclk(true);
        gpio_.delay_cycles(2);
    }

    Gpio& gpio_;
};
