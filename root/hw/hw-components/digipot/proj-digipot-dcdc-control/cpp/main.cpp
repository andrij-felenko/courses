#include <cstdint>
#include <cstddef>
#include <concepts>
#include <expected>
#include <array>
#include <algorithm>
#include <cmath>

namespace dcdc_control {

// Конфігураційні константи вузла перетворювача
struct HardwareConfig {
    static constexpr uint32_t vfb_mv         = 800;    // Опора FB, мВ
    static constexpr uint32_t r1_top_ohm     = 33000;  // Верхнє плече, Ом
    static constexpr uint32_t r2_bottom_ohm  = 10000;  // Нижній базовий резистор, Ом
    static constexpr uint32_t rs_series_ohm  = 4700;   // Послідовний резистор захисту, Ом
    static constexpr uint32_t rab_digipot_ohm= 10000;  // Повний опір диджипота, Ом
    static constexpr uint32_t rw_wiper_ohm   = 100;    // Опір ключа, Ом
    static constexpr uint8_t  max_steps      = 255;    // Кількість кроків 8-біт
};

enum class Error : uint8_t {
    VoltageOutOfRange,
    HardwareFault,
    Timeout
};

// Концепт апаратного інтерфейсу SPI з RAII-керуванням лінією Chip Select
template <typename T>
concept SpiInterface = requires(T spi, const uint8_t* tx, uint8_t* rx, size_t len, bool cs) {
    { spi.set_cs(cs) } -> std::same_as<void>;
    { spi.transfer(tx, rx, len) } -> std::same_as<bool>;
};

template <SpiInterface Bus>
class SafeDigiPot {
public:
    explicit SafeDigiPot(Bus& bus) noexcept
        : bus_(bus), current_code_(128) {
        bus_.set_cs(true);
        min_safe_mv_ = calculate_voltage(HardwareConfig::max_steps);
        max_safe_mv_ = calculate_voltage(0);
    }

    // Обчислення напруги для довільного коду (constexpr)
    [[nodiscard]] static constexpr uint16_t calculate_voltage(uint8_t code) noexcept {
        const uint32_t r_branch = HardwareConfig::rs_series_ohm + 
                                  HardwareConfig::rw_wiper_ohm + 
                                  (static_cast<uint32_t>(code) * HardwareConfig::rab_digipot_ohm) / 
                                  HardwareConfig::max_steps;

        const uint32_t r_bottom = (HardwareConfig::r2_bottom_ohm * r_branch) / 
                                  (HardwareConfig::r2_bottom_ohm + r_branch);

        const uint32_t v_out = HardwareConfig::vfb_mv + 
                               (HardwareConfig::vfb_mv * HardwareConfig::r1_top_ohm) / r_bottom;

        return static_cast<uint16_t>(v_out);
    }

    // Встановлення коду повзунка
    [[nodiscard]] std::expected<void, Error> set_wiper_code(uint8_t code) noexcept {
        if (auto res = send_command(0x00, code); !res) {
            return std::unexpected(res.error());
        }
        current_code_ = code;
        return {};
    }

    // Встановлення цільової вихідної напруги
    [[nodiscard]] std::expected<uint16_t, Error> set_target_voltage(uint16_t target_mv) noexcept {
        if (target_mv < min_safe_mv_ || target_mv > max_safe_mv_) {
            return std::unexpected(Error::VoltageOutOfRange);
        }

        uint8_t best_code = 0;
        int32_t min_diff = 0x7FFFFFFF;

        for (uint16_t code = 0; code <= HardwareConfig::max_steps; ++code) {
            const uint16_t v = calculate_voltage(static_cast<uint8_t>(code));
            const int32_t diff = std::abs(static_cast<int32_t>(v) - static_cast<int32_t>(target_mv));
            if (diff < min_diff) {
                min_diff = diff;
                best_code = static_cast<uint8_t>(code);
            }
        }

        if (auto res = set_wiper_code(best_code); !res) {
            return std::unexpected(res.error());
        }

        return calculate_voltage(best_code);
    }

    // Збереження калібрувального значення в EEPROM
    [[nodiscard]] std::expected<void, Error> save_to_eeprom() noexcept {
        return send_command(0x20, current_code_);
    }

    [[nodiscard]] uint8_t current_code() const noexcept { return current_code_; }
    [[nodiscard]] uint16_t min_voltage_mv() const noexcept { return min_safe_mv_; }
    [[nodiscard]] uint16_t max_voltage_mv() const noexcept { return max_safe_mv_; }

private:
    Bus&     bus_;
    uint8_t  current_code_;
    uint16_t min_safe_mv_{0};
    uint16_t max_safe_mv_{0};

    [[nodiscard]] std::expected<void, Error> send_command(uint8_t cmd, uint8_t data) noexcept {
        struct CsGuard {
            Bus& b;
            CsGuard(Bus& bus) : b(bus) { b.set_cs(false); }
            ~CsGuard() { b.set_cs(true); }
        } guard(bus_);

        const std::array<uint8_t, 2> tx_buf{ cmd, data };
        std::array<uint8_t, 2> rx_buf{ 0, 0 };

        if (!bus_.transfer(tx_buf.data(), rx_buf.data(), tx_buf.size())) {
            return std::unexpected(Error::HardwareFault);
        }
        return {};
    }
};

} // namespace dcdc_control
