#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <random>
#include <memory>
#include <optional>
#include <expected>
#include <csignal>
#include <sw/redis++/redis++.h>

using namespace sw::redis;
using namespace std::chrono_literals;

namespace iot {

struct TelemetryPacket {
    std::string device_id;
    int64_t seq_no{0};
    double temperature{0.0};
    double pressure{0.0};
};

enum class ProcessingError {
    TransientDbFailure,
    FatalSensorAnomaly,
    DeserializationError
};

class TelemetryWorker {
public:
    TelemetryWorker(std::string_view redis_uri, std::string worker_name)
        : redis_(redis_uri),
          worker_name_(std::move(worker_name)),
          stream_name_("iot:telemetry:stream"),
          group_name_("telemetry_workers"),
          dlq_stream_name_("iot:telemetry:dlq"),
          rng_(std::random_device{}()) {
        init_consumer_group();
    }

    void run() {
        std::cout << "[Worker " << worker_name_ << "] Запущено. Очікування повідомлень...\n";
        
        while (!stop_requested_) {
            try {
                // Читаємо пакети з Redis Stream через Consumer Group
                using ItemStream = std::vector<std::pair<std::string, std::vector<std::pair<std::string, std::string>>>>;
                ItemStream result;

                redis_.xreadgroup(
                    group_name_,
                    worker_name_,
                    stream_name_,
                    ">",
                    std::back_inserter(result),
                    10,        // count
                    2000ms     // block timeout
                );

                for (const auto& [msg_id, fields] : result) {
                    if (stop_requested_) break;
                    handle_message(msg_id, fields);
                }
            } catch (const Error& err) {
                std::cerr << "[Redis Error] " << err.what() << "\n";
                std::this_thread::sleep_for(1s);
            }
        }
        std::cout << "[Worker " << worker_name_ << "] Зупинено штатно.\n";
    }

    static void request_stop() {
        stop_requested_ = true;
    }

private:
    Redis redis_;
    std::string worker_name_;
    std::string stream_name_;
    std::string group_name_;
    std::string dlq_stream_name_;
    std::mt19937 rng_;
    inline static volatile sig_atomic_t stop_requested_{false};

    void init_consumer_group() {
        try {
            redis_.xgroup_create(stream_name_, group_name_, "0", true);
            std::cout << "Створено групу споживачів: " << group_name_ << "\n";
        } catch (const ReplyError& e) {
            // Ігноруємо BUSYGROUP, якщо група вже існує
        }
    }

    double compute_full_jitter(int attempt, double base_sec, double max_sec) {
        double max_backoff = std::min(max_sec, base_sec * std::pow(2.0, attempt));
        std::uniform_real_distribution<double> dist(0.0, max_backoff);
        return dist(rng_);
    }

    std::expected<void, ProcessingError> process_packet(const TelemetryPacket& pkt) {
        // Фатальна помилка сенсора
        if (pkt.temperature < -50.0 || pkt.temperature > 150.0) {
            return std::unexpected(ProcessingError::FatalSensorAnomaly);
        }

        // Емуляція 10% тимчасових мережевих збоїв
        std::uniform_int_distribution<int> dist(1, 10);
        if (dist(rng_) == 1) {
            return std::unexpected(ProcessingError::TransientDbFailure);
        }

        // Успішний запис у Time-Series DB
        std::cout << "✓ [C++] Записано: " << pkt.device_id << " t=" << pkt.temperature << "°C\n";
        return {};
    }

    void handle_message(const std::string& msg_id, const std::vector<std::pair<std::string, std::string>>& fields) {
        TelemetryPacket packet;
        int attempts = 0;

        for (const auto& [k, v] : fields) {
            if (k == "device_id") packet.device_id = v;
            else if (k == "seq_no") packet.seq_no = std::stoll(v);
            else if (k == "temp") packet.temperature = std::stod(v);
            else if (k == "pressure") packet.pressure = std::stod(v);
            else if (k == "attempts") attempts = std::stoi(v);
        }

        // Дедуплікація
        std::string dedup_key = "iot:dedup:" + packet.device_id + ":" + std::to_string(packet.seq_no);
        bool is_new = redis_.set(dedup_key, "1", 3600s, UpdateType::NOT_EXIST);
        if (!is_new) {
            std::cout << "[Dedup] Пропуск дубліката " << packet.device_id << "\n";
            redis_.xack(stream_name_, group_name_, msg_id);
            return;
        }

        auto result = process_packet(packet);
        if (result.has_value()) {
            // Успіх
            redis_.xack(stream_name_, group_name_, msg_id);
        } else {
            if (result.error() == ProcessingError::TransientDbFailure && attempts < 3) {
                // Повтор із тремтінням
                attempts++;
                double delay = compute_full_jitter(attempts, 1.5, 30.0);
                std::cout << "[Retry] Спроба " << attempts << " через " << delay << " с\n";
                std::this_thread::sleep_for(std::chrono::duration<double>(delay));

                std::vector<std::pair<std::string, std::string>> new_fields = {
                    {"device_id", packet.device_id},
                    {"seq_no", std::to_string(packet.seq_no)},
                    {"temp", std::to_string(packet.temperature)},
                    {"pressure", std::to_string(packet.pressure)},
                    {"attempts", std::to_string(attempts)}
                };
                redis_.xadd(stream_name_, "*", new_fields.begin(), new_fields.end());
                redis_.xack(stream_name_, group_name_, msg_id);
            } else {
                // Фатальна помилка або вичерпано спроби -> DLQ
                std::cout << "[DLQ] Переміщення повідомлення " << msg_id << " в DLQ\n";
                std::vector<std::pair<std::string, std::string>> dlq_fields = {
                    {"original_id", msg_id},
                    {"device_id", packet.device_id},
                    {"error", result.error() == ProcessingError::FatalSensorAnomaly ? "SensorAnomaly" : "RetriesExhausted"}
                };
                redis_.xadd(dlq_stream_name_, "*", dlq_fields.begin(), dlq_fields.end());
                redis_.xack(stream_name_, group_name_, msg_id);
            }
        }
    }
};

} // namespace iot

int main() {
    std::signal(SIGINT, [](int) { iot::TelemetryWorker::request_stop(); });
    std::signal(SIGTERM, [](int) { iot::TelemetryWorker::request_stop(); });

    iot::TelemetryWorker worker("tcp://127.0.0.1:6379", "cpp_worker_1");
    worker.run();
    return 0;
}
