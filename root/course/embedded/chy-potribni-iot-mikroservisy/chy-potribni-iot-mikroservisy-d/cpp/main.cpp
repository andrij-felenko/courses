#include <iostream>
#include <memory>
#include <vector>
#include <string_view>
#include <cstdint>

// 1. Незмінна структура події телеметрії (Domain Event)
struct TelemetryEvent {
    uint64_t device_id;
    uint64_t timestamp_ms;
    float temperature_c;
    float pressure_bar;
    uint32_t flags;
};

// 2. Абстрактний інтерфейс слухача подій (In-Process Observer)
class ITelemetryConsumer {
public:
    virtual ~ITelemetryConsumer() = default;
    virtual void on_telemetry(const TelemetryEvent& event) = 0;
};

// 3. Модуль Digital Twin (утримує оперативний стан у пам'яті)
class DeviceTwinModule : public ITelemetryConsumer {
public:
    void on_telemetry(const TelemetryEvent& event) override {
        // Оновлення стану без серіалізації та мережевих викликів
        update_device_state(event.device_id, event.temperature_c, event.flags);
    }
private:
    void update_device_state(uint64_t id, float temp, uint32_t flags) {
        // Швидка атомарна зміна показників у хеш-таблиці
    }
};

// 4. Модуль порогових правил (Rules Engine)
class RulesEngineModule : public ITelemetryConsumer {
public:
    void on_telemetry(const TelemetryEvent& event) override {
        if (event.temperature_c > 80.0f) {
            trigger_emergency_alert(event.device_id, event.temperature_c);
        }
    }
private:
    void trigger_emergency_alert(uint64_t id, float temp) {
        // Локальна генерація аварійного сигналу
    }
};

// 5. Внутрішньопроцесний диспетчер шини подій (In-Memory Event Bus)
class InMemoryEventBus {
public:
    void subscribe(std::shared_ptr<ITelemetryConsumer> consumer) {
        consumers_.push_back(consumer);
    }

    void publish(const TelemetryEvent& event) {
        for (const auto& consumer : consumers_) {
            consumer->on_telemetry(event);
        }
    }
private:
    std::vector<std::shared_ptr<ITelemetryConsumer>> consumers_;
};
