#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>
#include <chrono>
#include <array>

enum class SpiMode : uint8_t {
    Mode0 = 0, // CPOL=0, CPHA=0
    Mode1 = 1, // CPOL=0, CPHA=1
    Mode2 = 2, // CPOL=1, CPHA=0
    Mode3 = 3  // CPOL=1, CPHA=1
};

// C++20 концепт апаратного адаптера виводів GPIO
template <typename T>
concept SpiGpioPort = requires(T port, bool level) {
    { port.set_sclk(level) } -> std::same_as<void>;
    { port.set_mosi(level) } -> std::same_as<void>;
    { port.get_miso() }      -> std::same_as<bool>;
    { port.set_cs(level) }   -> std::same_as<void>;
    { port.delay_ns(100u) }  -> std::same_as<void>;
};

// RAII охоронець вибору кристала Chip Select
template <SpiGpioPort Gpio>
class ChipSelectGuard {
public:
    explicit ChipSelectGuard(Gpio& gpio, uint32_t hold_delay_ns = 50)
        : gpio_(gpio), delay_ns_(hold_delay_ns) {
        gpio_.set_cs(false); // Активувати веденого (LOW)
        gpio_.delay_ns(delay_ns_); // Захисна пауза t_CSS
    }

    ~ChipSelectGuard() {
        gpio_.delay_ns(delay_ns_); // Захисна пауза t_CSH
        gpio_.set_cs(true);  // Деактивувати веденого (HIGH)
    }

    ChipSelectGuard(const ChipSelectGuard&) = delete;
    ChipSelectGuard& operator=(const ChipSelectGuard&) = delete;

private:
    Gpio& gpio_;
    uint32_t delay_ns_;
};

// Шаблонний клас програмного контролера SPI
template <SpiGpioPort Gpio>
class SoftwareSpiMaster {
public:
    constexpr SoftwareSpiMaster(Gpio& gpio, SpiMode mode, uint32_t half_period_ns = 500)
        : gpio_(gpio), mode_(mode), half_period_ns_(half_period_ns) {
        init();
    }

    void init() const {
        const bool cpol = (mode_ == SpiMode::Mode2 || mode_ == SpiMode::Mode3);
        gpio_.set_cs(true);
        gpio_.set_sclk(cpol);
        gpio_.set_mosi(false);
    }

    uint8_t transfer_byte(uint8_t byte_out) const {
        const bool cpol = (mode_ == SpiMode::Mode2 || mode_ == SpiMode::Mode3);
        const bool cpha = (mode_ == SpiMode::Mode1 || mode_ == SpiMode::Mode3);
        uint8_t byte_in = 0;

        for (uint8_t bit = 0; bit < 8; ++bit) {
            const bool out_bit = (byte_out & (1 << (7 - bit))) != 0;

            if (!cpha) {
                // CPHA = 0: встановлення біта перед 1-м фронтом
                gpio_.set_mosi(out_bit);
                gpio_.delay_ns(half_period_ns_);

                // 1-й фронт: вибірка
                gpio_.set_sclk(!cpol);
                gpio_.delay_ns(half_period_ns_);
                if (gpio_.get_miso()) {
                    byte_in |= static_cast<uint8_t>(1 << (7 - bit));
                }

                // 2-й фронт: зміна такту назад у спокій
                gpio_.set_sclk(cpol);
            } else {
                // CPHA = 1: 1-й фронт змінює стан лінії
                gpio_.set_sclk(!cpol);
                gpio_.set_mosi(out_bit);
                gpio_.delay_ns(half_period_ns_);

                // 2-й фронт: вибірка
                gpio_.set_sclk(cpol);
                gpio_.delay_ns(half_period_ns_);
                if (gpio_.get_miso()) {
                    byte_in |= static_cast<uint8_t>(1 << (7 - bit));
                }
            }
        }
        return byte_in;
    }

    void transfer(std::span<const uint8_t> tx_data, std::span<uint8_t> rx_data) const {
        const ChipSelectGuard<Gpio> guard(gpio_, half_period_ns_);
        const size_t count = tx_data.size();
        for (size_t i = 0; i < count; ++i) {
            uint8_t byte_rx = transfer_byte(tx_data[i]);
            if (i < rx_data.size()) {
                rx_data[i] = byte_rx;
            }
        }
    }

private:
    Gpio& gpio_;
    SpiMode mode_;
    uint32_t half_period_ns_;
};
