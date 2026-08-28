#include <variant>
#include <iostream>
#include <string>
#include <type_traits>

// Допоміжний шаблон для відкладеної перевірки повноти гілок
template<typename> inline constexpr bool dependent_false = false;

struct SystemAlert {
    int severity_code;
    std::string message;
};

struct SensorReading {
    uint32_t sensor_id;
    double value;
};

struct HeartbeatPing {
    uint64_t timestamp_ns;
};

using TelemetryEvent = std::variant<SystemAlert, SensorReading, HeartbeatPing>;

void process_telemetry(const TelemetryEvent& event) {
    std::visit([](const auto& item) {
        using T = std::decay_t<decltype(item)>;

        if constexpr (std::is_same_v<T, SystemAlert>) {
            std::cout << "[ТРИВОГА Рівень " << item.severity_code << "] " 
                      << item.message << "\n";
        } else if constexpr (std::is_same_v<T, SensorReading>) {
            std::cout << "[ДАТЧИК #" << item.sensor_id << "] Показник: " 
                      << item.value << "\n";
        } else if constexpr (std::is_same_v<T, HeartbeatPing>) {
            std::cout << "[ПУЛЬС] Позначка часу: " 
                      << item.timestamp_ns << " нс\n";
        } else {
            // Якщо у variant буде додано новий тип, компілятор видасть помилку тут!
            static_assert(dependent_false<T>, "Не всі типи variant покрито обробником!");
        }
    }, event);
}
