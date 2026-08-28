// Idiomatic C++ Seam: HubTelemetrySeam.hpp
#include <iostream>
#include <string>
#include <functional>
#include <memory>

struct TelemetryPacket {
    int device_id;
    float raw_temperature;
    int status_flags;
};

// Інтерфейс шва для підміни залежностей у характеристичних тестах (RAII / DI)
class INotificationSink {
public:
    virtual ~INotificationSink() = default;
    virtual void send(int device_id, std::string_view message) = 0;
};

class DefaultNetworkSink : public INotificationSink {
public:
    void send(int device_id, std::string_view message) override {
        std::cout << "[NET-SEND] Device " << device_id << ": " << message << "\n";
    }
};

class TelemetryProcessor {
private:
    std::shared_ptr<INotificationSink> sink_;

public:
    // Конструктор приймає шов (за замовчуванням — мережевий Sink)
    explicit TelemetryProcessor(std::shared_ptr<INotificationSink> sink = std::make_shared<DefaultNetworkSink>())
        : sink_(std::move(sink)) {}

    int process(const TelemetryPacket& pkt) {
        if (pkt.raw_temperature > 85.0f && (pkt.status_flags & 0x01)) {
            sink_->send(pkt.device_id, "CRITICAL_OVERHEAT");
            return 2;
        } else if (pkt.raw_temperature < -20.0f) {
            sink_->send(pkt.device_id, "SENSOR_FREEZE");
            return 1;
        }
        return 0;
    }
};
