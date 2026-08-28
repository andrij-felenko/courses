/* telemetry_engine.hpp — ідіоматичний PIMPL-інтерфейс для C++20 */
#pragma once

#include <memory>
#include <span>
#include <string_view>
#include <expected>
#include <cstdint>

enum class TelemetryError {
    InvalidArg,
    NoMemory,
    Overflow,
    HardwareIo
};

struct TelemetryConfig {
    uint32_t sample_rate_hz{100};
    size_t   max_channels{16};
};

class TelemetryEngine {
public:
    explicit TelemetryEngine(const TelemetryConfig &config);
    ~TelemetryEngine();

    /* Заборона небезпечного копіювання, дозвіл переміщення ресурсу (RAII) */
    TelemetryEngine(const TelemetryEngine &) = delete;
    TelemetryEngine &operator=(const TelemetryEngine &) = delete;
    TelemetryEngine(TelemetryEngine &&) noexcept;
    TelemetryEngine &operator=(TelemetryEngine &&) noexcept;

    /* Публічні операції з типізованою обробкою результатів через std::expected */
    [[nodiscard]] std::expected<void, TelemetryError> 
    push_sample(uint16_t channel_id, float value) noexcept;

    [[nodiscard]] std::expected<float, TelemetryError> 
    get_channel_mean(uint16_t channel_id) const noexcept;

    void reset() noexcept;

private:
    /* Неповний тип внутрішньої реалізації (Pointer to Implementation) */
    struct Impl;
    std::unique_ptr<Impl> pimpl_;
};
