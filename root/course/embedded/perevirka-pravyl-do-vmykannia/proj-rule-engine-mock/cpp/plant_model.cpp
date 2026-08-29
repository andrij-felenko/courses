#include "plant_model.hpp"

#include <stdexcept>

PlantModel::PlantModel(float initial_temp_c, Params params)
    : p_(params), temp_c_(initial_temp_c), pressure_bar_(params.static_pressure_bar) {
    if (!(p_.thermal_capacity_kj_per_k > 0.0f) || !(p_.thermal_resistance_k_per_kw > 0.0f)) {
        throw std::invalid_argument("теплоємність і тепловий опір мають бути додатні");
    }
}

void PlantModel::step(const ActuatorState& act, float dt_seconds) {
    // Явний Ейлер стійкий лише поки крок менший за сталу часу tau = C·R.
    // Для 80 кДж/К і 12 К/кВт це 960 с — крок 0.5 с має величезний запас.
    const float tau_s = p_.thermal_capacity_kj_per_k * p_.thermal_resistance_k_per_kw;
    if (!(dt_seconds > 0.0f) || dt_seconds >= tau_s) {
        throw std::invalid_argument("крок інтегрування поза межею стійкості (треба dt < C·R)");
    }

    float p_heat_kw = 0.0f;
    if (act.heater_stage1) p_heat_kw += p_.stage_power_kw;
    if (act.heater_stage2) p_heat_kw += p_.stage_power_kw;

    // Сухий нагрів модель не описує чесно: без теплознімання ТЕН згорає за
    // десятки секунд, і жодне рівняння балансу тут не працює. Тому просто
    // рахуємо такі кроки — жоден із них не має статися.
    if (p_heat_kw > 0.0f && !act.circulation_pump) {
        ++dry_heating_steps_;
    }

    const float loss_kw = (temp_c_ - p_.ambient_c) / p_.thermal_resistance_k_per_kw;
    temp_c_ += ((p_heat_kw - loss_kw) / p_.thermal_capacity_kj_per_k) * dt_seconds;

    // Гідравліка: протік і робочий тиск з'являються разом із помпою.
    flow_ = act.circulation_pump;
    pressure_bar_ = flow_ ? p_.running_pressure_bar : p_.static_pressure_bar;

    time_ms_ += static_cast<std::uint32_t>(dt_seconds * 1000.0f + 0.5f);
}

SensorSnapshot PlantModel::read_snapshot() {
    SensorSnapshot s{};
    s.temperature_c = temp_c_;
    s.pressure_bar = pressure_bar_;
    s.flow_detected = flow_;
    s.emergency_stop_btn = false;  // фізика кнопки не тисне — це справа ін'єктора
    s.sensor_fault = false;
    s.timestamp_ms = time_ms_;
    return s;
}
