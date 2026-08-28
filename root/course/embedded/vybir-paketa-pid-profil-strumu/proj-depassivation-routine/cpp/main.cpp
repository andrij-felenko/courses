// depassivation_driver.hpp — Ідіоматичний C++20 модуль контролю джерела живлення
#include <cstdint>
#include <concepts>
#include <chrono>
#include <expected>
#include <utility>

enum class BatteryError {
    HardwareFault,
    CriticalBrownoutRisk,
    EndOfLifeDepleted,
    PassivationUnresolved
};

struct BatteryMetrics {
    std::uint32_t open_circuit_mv{0};
    std::uint32_t loaded_voltage_mv{0};
    std::uint32_t internal_resistance_mohm{0};
    std::uint8_t depassivation_pulses{0};
};

template <typename PlatformHAL>
concept BatteryHALConcept = requires(PlatformHAL hal, bool enable, std::chrono::milliseconds ms) {
    { hal.read_voltage_mv() } -> std::same_as<std::uint32_t>;
    { hal.set_load_resistor(enable) } -> std::same_as<void>;
    { hal.sleep_for(ms) } -> std::same_as<void>;
};

template <BatteryHALConcept HAL>
class AdaptiveBatteryGuard {
public:
    static constexpr std::uint32_t LoadResistorMohm = 100'000;  // 100 Ом
    static constexpr std::uint32_t SafeTxVoltageMv = 3'000;     // 3.0 В
    static constexpr std::uint32_t CriticalVoltageMv = 2'400;   // 2.4 В
    static constexpr std::uint8_t MaxAttempts = 10;

    explicit constexpr AdaptiveBatteryGuard(HAL& hal) noexcept : hal_(hal) {}

    [[nodiscard]] std::expected<BatteryMetrics, BatteryError> prepare_for_transmission() noexcept {
        BatteryMetrics metrics{};
        
        // 1. Зчитування напруги холостого ходу
        hal_.set_load_resistor(false);
        hal_.sleep_for(std::chrono::milliseconds(5));
        metrics.open_circuit_mv = hal_.read_voltage_mv();

        if (metrics.open_circuit_mv < SafeTxVoltageMv) {
            return std::unexpected(BatteryError::EndOfLifeDepleted);
        }

        // 2. Цикл адаптивної депасивації
        for (std::uint8_t i = 0; i < MaxAttempts; ++i) {
            hal_.set_load_resistor(true);
            hal_.sleep_for(std::chrono::milliseconds(15));
            metrics.loaded_voltage_mv = hal_.read_voltage_mv();

            if (metrics.loaded_voltage_mv >= SafeTxVoltageMv) {
                hal_.set_load_resistor(false);
                metrics.depassivation_pulses = i;

                const std::uint64_t delta_v = metrics.open_circuit_mv - metrics.loaded_voltage_mv;
                metrics.internal_resistance_mohm = static_cast<std::uint32_t>(
                    (delta_v * LoadResistorMohm) / metrics.loaded_voltage_mv
                );
                return metrics;
            }

            // Додаткова витримка під струмом для розчинення LiCl
            hal_.sleep_for(std::chrono::milliseconds(50));
            hal_.set_load_resistor(false);
            hal_.sleep_for(std::chrono::milliseconds(25));
        }

        if (metrics.loaded_voltage_mv < CriticalVoltageMv) {
            return std::unexpected(BatteryError::CriticalBrownoutRisk);
        }
        return std::unexpected(BatteryError::PassivationUnresolved);
    }

private:
    HAL& hal_;
};
