// Драйвер програмного SPI Master для ISP-програматора (C++20)
#include <cstdint>
#include <array>
#include <span>
#include <chrono>
#include <expected>

// Зовнішні апаратні абстракції GPIO
extern void gpio_set_reset(bool level);
extern void gpio_set_sck(bool level);
extern void gpio_set_mosi(bool level);
extern bool gpio_get_miso();
extern void delay_us(std::uint32_t us);
extern void delay_ms(std::uint32_t ms);

enum class IspError {
    InvalidParameters,
    TargetUnresponsive,
    SyncFailed,
    WriteTimeout,
    VerificationFailed
};

class IspMasterController {
public:
    struct Config {
        std::uint32_t target_cpu_hz{1'000'000};
        std::uint32_t desired_isp_hz{125'000};
    };

    explicit IspMasterController(Config cfg) noexcept {
        // Обмеження частоти: f_ISP <= f_CPU / 6 для гарантії стабільності
        const std::uint32_t max_safe_hz = cfg.target_cpu_hz / 6;
        const std::uint32_t actual_hz = std::min(cfg.desired_isp_hz, max_safe_hz);
        half_period_us_ = std::max(1u, 1'000'000u / (actual_hz * 2));
    }

    ~IspMasterController() noexcept {
        if (in_prog_mode_) {
            leave_programming_mode();
        }
    }

    // Заборона копіювання контролера через апаратний стан RESET
    IspMasterController(const IspMasterController&) = delete;
    IspMasterController& operator=(const IspMasterController&) = delete;

    [[nodiscard]] std::expected<void, IspError> enter_programming_mode() noexcept {
        gpio_set_sck(false);
        gpio_set_mosi(false);
        gpio_set_reset(true);
        delay_ms(20);

        // Притискаємо RESET до 0V для блокування CPU ядра
        gpio_set_reset(false);
        delay_ms(25);

        // Команда Programming Enable
        constexpr std::array<std::uint8_t, 4> enter_cmd{0xAC, 0x53, 0x00, 0x00};
        const auto resp = transfer_transaction(enter_cmd);

        // Верифікація відлуння ключа 0x53 у 3-му байті
        if (resp[2] != 0x53) {
            gpio_set_reset(true);
            in_prog_mode_ = false;
            return std::unexpected(IspError::SyncFailed);
        }

        in_prog_mode_ = true;
        return {};
    }

    void leave_programming_mode() noexcept {
        gpio_set_sck(false);
        gpio_set_mosi(false);
        gpio_set_reset(true); // Зняття сигналу скидання
        in_prog_mode_ = false;
        delay_ms(20);
    }

    [[nodiscard]] std::array<std::uint8_t, 4> transfer_transaction(
        std::span<const std::uint8_t, 4> cmd) const noexcept 
    {
        std::array<std::uint8_t, 4> result{};
        for (std::size_t b = 0; b < 4; ++b) {
            result[b] = transfer_byte(cmd[b]);
        }
        return result;
    }

    [[nodiscard]] std::expected<std::array<std::uint8_t, 3>, IspError> read_signature() const noexcept {
        if (!in_prog_mode_) {
            return std::unexpected(IspError::SyncFailed);
        }

        std::array<std::uint8_t, 3> sig{};
        for (std::uint8_t addr = 0; addr < 3; ++addr) {
            const std::array<std::uint8_t, 4> cmd{0x30, 0x00, addr, 0x00};
            const auto resp = transfer_transaction(cmd);
            sig[addr] = resp[3];
        }
        return sig;
    }

private:
    [[nodiscard]] std::uint8_t transfer_byte(std::uint8_t out_byte) const noexcept {
        std::uint8_t in_byte = 0;
        for (int i = 7; i >= 0; --i) {
            gpio_set_mosi(((out_byte >> i) & 1) != 0);
            delay_us(half_period_us_);

            gpio_set_sck(true);
            delay_us(half_period_us_);

            if (gpio_get_miso()) {
                in_byte |= static_cast<std::uint8_t>(1u << i);
            }

            gpio_set_sck(false);
        }
        return in_byte;
    }

    std::uint32_t half_period_us_{4};
    bool in_prog_mode_{false};
};
