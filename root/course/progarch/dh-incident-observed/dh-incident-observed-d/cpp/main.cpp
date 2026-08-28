// C++20 / OpenTelemetry C++ SDK / Scoped Trace Context
#include <iostream>
#include <string>
#include <memory>
#include <chrono>

// Обгортка для автоматичного додавання trace_id до кожного запису логу
class TelemetryScopedLogger {
public:
    static void log_db_error(const std::string& trace_id, 
                             const std::string& span_id, 
                             const std::string& query, 
                             double duration_ms, 
                             const std::string& error_msg) {
        auto now = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();

        std::cout << "{"
                  << "\"timestamp\":" << now << ","
                  << "\"level\":\"ERROR\","
                  << "\"service\":\"device-telemetry-service\","
                  << "\"trace_id\":\"" << trace_id << "\","
                  << "\"span_id\":\"" << span_id << "\","
                  << "\"db\":{"
                  << "\"statement\":\"" << query << "\","
                  << "\"duration_ms\":" << duration_ms
                  << "},"
                  << "\"error\":\"" << error_msg << "\""
                  << "}\n";
    }
};
