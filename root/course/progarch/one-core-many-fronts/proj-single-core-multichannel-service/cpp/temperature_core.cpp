#include "temperature_core.hpp"
#include <cmath>

TemperatureControlService::TemperatureControlService() {
    // Ініціалізація доменних зон будівлі з їхніми інваріантами безпеки та правами доступу
    register_zone("living-room", 20.0, 16.0, 28.0, "operator_1");
    register_zone("bedroom", 19.0, 15.0, 26.0, "operator_1");
    register_zone("server-room", 18.0, 10.0, 22.0, "admin"); // Доступ дозволено лише admin
    register_zone("greenhouse", 24.0, 18.0, 35.0, "operator_2");
}

void TemperatureControlService::register_zone(std::string id, double current_temp, 
                                             double min_temp, double max_temp, 
                                             std::string authorized_user) {
    ClimateZone zone{
        .id = id,
        .current_temperature = current_temp,
        .min_temperature = min_temp,
        .max_temperature = max_temp,
        .authorized_user = std::move(authorized_user),
        .is_busy = false
    };
    zones_[id] = std::move(zone);
}

void TemperatureControlService::set_zone_busy(const std::string& zone_id, bool busy) {
    auto it = zones_.find(zone_id);
    if (it != zones_.end()) {
        it->second.is_busy = busy;
    }
}

std::optional<double> TemperatureControlService::get_temperature(const std::string& zone_id) const {
    auto it = zones_.find(zone_id);
    if (it != zones_.end()) {
        return it->second.current_temperature;
    }
    return std::nullopt;
}

std::expected<TemperatureResult, DomainError> 
TemperatureControlService::execute(const SetTemperatureCommand& command) {
    // 1. Первинна валідація інваріантів самої команди
    if (command.zone_id().empty() || command.user_id().empty() || std::isnan(command.target_temperature())) {
        return std::unexpected(DomainError::InvalidCommand);
    }

    // 2. Перевірка існування цільової кліматичної зони
    auto it = zones_.find(command.zone_id());
    if (it == zones_.end()) {
        return std::unexpected(DomainError::ZoneNotFound);
    }

    ClimateZone& zone = it->second;

    // 3. Перевірка тимчасової апаратної зайнятості пристрою (симуляція відмови для черги)
    if (zone.is_busy) {
        return std::unexpected(DomainError::DeviceBusy);
    }

    // 4. Контроль прав доступу: "admin" має повний доступ, інші лише до закріплених зон
    if (command.user_id() != "admin" && command.user_id() != zone.authorized_user) {
        return std::unexpected(DomainError::AccessDenied);
    }

    // 5. Перевірка фізичних інваріантів безпечного діапазону температур для даної зони
    if (command.target_temperature() < zone.min_temperature || 
        command.target_temperature() > zone.max_temperature) {
        return std::unexpected(DomainError::TemperatureOutOfRange);
    }

    // 6. Успішне оновлення внутрішнього стану ядра
    const double previous_temperature = zone.current_temperature;
    zone.current_temperature = command.target_temperature();

    return TemperatureResult{
        .zone_id = zone.id,
        .new_temperature = zone.current_temperature,
        .previous_temperature = previous_temperature,
        .timestamp = std::chrono::system_clock::now()
    };
}
