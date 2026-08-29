// app/telemetry.hpp — накопичення вимірів у запис телеметрії.
// Вікно закривається за часом, а не за кількістю зразків: пропущений через
// відмову шини вимір не має зсувати розклад передавання.
#pragma once

#include "hal/clock.hpp"

#include <cstdint>
#include <optional>

namespace app {

struct TelemetryRecord {
    hal::Millis   window_start{0};
    hal::Millis   window_end{0};
    std::uint32_t sample_count{0};
    float         temp_avg_c{0.0F};
    float         temp_min_c{0.0F};
    float         temp_max_c{0.0F};
    float         humidity_avg_rh{0.0F};
    float         pressure_avg_hpa{0.0F};
    float         vibration_rms_g{0.0F};
    float         vibration_peak_g{0.0F};
    std::uint32_t fault_count{0};
};

// Приймач готового запису. Реалізацію дає порт: передавач UART на платі,
// друк у консоль на комп'ютері розробника.
class ITelemetrySink {
public:
    virtual ~ITelemetrySink() = default;
    virtual void publish(const TelemetryRecord& record) = 0;
};

struct Measurement {
    float temperature_c{0.0F};
    float humidity_rh{0.0F};
    float pressure_hpa{0.0F};
    float vibration_g{0.0F};
};

class TelemetryWindow {
public:
    TelemetryWindow(hal::Millis window, hal::Millis now) noexcept
        : window_{window}, start_{now} {}

    void add(const Measurement& m);

    // Невдале опитування теж потрапляє в запис: інакше телеметрія
    // виглядатиме бездоганною саме тоді, коли пристрій наполовину сліпий.
    void add_fault() noexcept { ++faults_; }

    [[nodiscard]] bool elapsed(hal::Millis now) const noexcept
    {
        return (now - start_) >= window_;
    }

    // Складає запис і починає нове вікно. std::nullopt — за вікно не було
    // жодного успішного виміру, тож усереднювати нема чого.
    [[nodiscard]] std::optional<TelemetryRecord> close(hal::Millis now);

    void restart(hal::Millis now) noexcept;

private:
    hal::Millis   window_;
    hal::Millis   start_;
    std::uint32_t samples_{0};
    std::uint32_t faults_{0};
    float         temp_sum_{0.0F};
    float         temp_min_{0.0F};
    float         temp_max_{0.0F};
    float         humidity_sum_{0.0F};
    float         pressure_sum_{0.0F};
    float         vibration_sq_sum_{0.0F};
    float         vibration_peak_{0.0F};
};

} // namespace app
