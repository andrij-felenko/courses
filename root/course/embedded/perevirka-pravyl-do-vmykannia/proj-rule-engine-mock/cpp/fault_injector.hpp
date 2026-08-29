#pragma once

#include <optional>

#include "contracts.hpp"

// Ін'єктор стоїть МІЖ джерелом вимірювань і рушієм правил і підміняє окремі
// поля знімка. Модель фізики про підміну не знає — саме тому нею можна показати
// те, чого фізика не робить: обрив АЦП, NaN після перетворення, завмерлу шину.
class FaultInjector : public ISensorSource {
public:
    explicit FaultInjector(ISensorSource& upstream) : upstream_(upstream) {}

    SensorSnapshot read_snapshot() override {
        // Шина не відповіла: драйвер віддає останній вдалий знімок разом
        // зі старою міткою часу. Числа правдоподібні, а дані мертві.
        if (frozen_ && held_) {
            return *held_;
        }
        SensorSnapshot s = upstream_.read_snapshot();
        if (temperature_) s.temperature_c = *temperature_;
        if (pressure_) s.pressure_bar = *pressure_;
        held_ = s;
        return s;
    }

    void override_temperature(float value) { temperature_ = value; }
    void clear_temperature() { temperature_.reset(); }

    void override_pressure(float value) { pressure_ = value; }
    void clear_pressure() { pressure_.reset(); }

    void freeze(bool on) { frozen_ = on; }

private:
    ISensorSource& upstream_;
    std::optional<float> temperature_{};
    std::optional<float> pressure_{};
    bool frozen_{false};
    std::optional<SensorSnapshot> held_{};
};
