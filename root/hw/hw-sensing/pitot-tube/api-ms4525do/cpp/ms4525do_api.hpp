// ms4525do_api.hpp — Сучасний типізований C++20 контракт драйвера MS4525DO
#pragma once

#include <cstdint>
#include <concepts>
#include <span>
#include <expected>

namespace AirData {

enum class SensorStatus : uint8_t {
    Ok = 0,
    CommandMode = 1,
    StaleData = 2,
    DiagnosticFault = 3,
    BusError = 4
};

struct AirspeedReading {
    float differential_pressure_pa{0.0f};
    float temperature_c{0.0f};
    bool is_fresh{false};
};

template <typename I2cBus>
concept AirspeedI2c = requires(I2cBus bus, uint8_t addr, std::span<uint8_t> buffer) {
    { bus.read(addr, buffer) } -> std::same_as<bool>;
};

template <AirspeedI2c Bus>
class Ms4525DO {
public:
    constexpr Ms4525DO(Bus& bus, uint8_t address = 0x28, float p_span_psi = 1.0f)
        : bus_(bus), address_(address),
          p_min_pa_(-p_span_psi * PSI_TO_PA),
          p_max_pa_(p_span_psi * PSI_TO_PA) {}

    std::expected<AirspeedReading, SensorStatus> read();
    bool calibrateZero(size_t samples = 100);

    void setZeroOffset(float offset_pa) noexcept { zero_offset_pa_ = offset_pa; }
    [[nodiscard]] float getZeroOffset() const noexcept { return zero_offset_pa_; }

private:
    static constexpr float PSI_TO_PA = 6894.757f;
    static constexpr float COUNT_MIN = 1638.0f;  // 10% від 16383
    static constexpr float COUNT_MAX = 14745.0f; // 90% від 16383
    static constexpr float COUNT_SPAN = COUNT_MAX - COUNT_MIN;

    Bus& bus_;
    uint8_t address_;
    float p_min_pa_;
    float p_max_pa_;
    float zero_offset_pa_{0.0f};
};

} // namespace AirData
