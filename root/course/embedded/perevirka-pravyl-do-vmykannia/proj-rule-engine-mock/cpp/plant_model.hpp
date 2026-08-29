#pragma once

#include <cstdint>

#include "contracts.hpp"

// Модель об'єкта керування: тепловий баланс бака й проста гідравліка.
// Замикає контур — команди рушія змінюють стан, стан повертається у вимірювання.
class PlantModel : public ISensorSource {
public:
    struct Params {
        float thermal_capacity_kj_per_k{80.0f};    // C_тепл: вода плюс корпус
        float thermal_resistance_k_per_kw{12.0f};  // R_тепл: втрати крізь стінки
        float ambient_c{20.0f};                    // температура приміщення
        float stage_power_kw{6.0f};                // потужність одного ТЕНа
        float static_pressure_bar{1.8f};           // тиск без помпи
        float running_pressure_bar{2.2f};          // робочий динамічний тиск
    };

    PlantModel(float initial_temp_c, Params params);

    // Один крок явного інтегрування за Ейлером.
    void step(const ActuatorState& act, float dt_seconds);

    SensorSnapshot read_snapshot() override;

    [[nodiscard]] float temperature_c() const { return temp_c_; }
    [[nodiscard]] std::uint32_t time_ms() const { return time_ms_; }
    [[nodiscard]] int dry_heating_steps() const { return dry_heating_steps_; }

private:
    Params p_;
    float temp_c_;
    float pressure_bar_;
    bool flow_{false};
    std::uint32_t time_ms_{0};
    int dry_heating_steps_{0};
};
