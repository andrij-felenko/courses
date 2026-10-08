#ifndef MQTT_TELEMETRY_HPP
#define MQTT_TELEMETRY_HPP

#include <cstdint>
#include <string>
#include <sstream>
#include <iomanip>
#include <iostream>
#include "water_flow_sensor.hpp"

class MqttTelemetry {
public:
    MqttTelemetry(const std::string& broker_url, const std::string& client_id, const std::string& topic)
        : broker_url_(broker_url), client_id_(client_id), topic_(topic) {}

    void begin() {
        is_connected_ = true;
        std::cout << "[MQTT] З'єднання встановлено з " << broker_url_ 
                  << " (Client ID: " << client_id_ << ")\n";
    }

    bool is_connected() const { return is_connected_; }

    // Формування та відправка JSON-пакета телеметрії
    bool publish_telemetry(const FlowMetrics& metrics, float battery_voltage, uint32_t current_time_ms) {
        if (!is_connected_) return false;

        // Дотримання інтервалу публікації
        if (current_time_ms - last_publish_ms_ < publish_interval_ms_ && last_publish_ms_ != 0) {
            return false;
        }

        std::string json_payload = serialize_payload(metrics, battery_voltage, current_time_ms);

        std::cout << "[MQTT Pub -> " << topic_ << "]: " << json_payload << "\n";

        last_publish_ms_ = current_time_ms;
        return true;
    }

    // Зміна інтервалу публікацій залежно від режимів енергозбереження
    void set_publish_interval(uint32_t interval_ms) {
        publish_interval_ms_ = interval_ms;
    }

private:
    std::string broker_url_;
    std::string client_id_;
    std::string topic_;
    bool is_connected_{false};
    uint32_t last_publish_ms_{0};
    uint32_t publish_interval_ms_{3000}; // 3 секунди за замовчуванням

    std::string serialize_payload(const FlowMetrics& metrics, float battery_voltage, uint32_t uptime_ms) const {
        std::ostringstream ss;
        ss << std::fixed << std::setprecision(3);
        ss << "{"
           << "\"flow_rate_lpm\":" << metrics.flow_rate_lpm << ","
           << "\"total_liters\":" << metrics.total_liters << ","
           << "\"total_pulses\":" << metrics.total_pulses << ","
           << "\"v_bat\":" << battery_voltage << ","
           << "\"uptime_ms\":" << uptime_ms
           << "}";
        return ss.str();
    }
};

#endif // MQTT_TELEMETRY_HPP
