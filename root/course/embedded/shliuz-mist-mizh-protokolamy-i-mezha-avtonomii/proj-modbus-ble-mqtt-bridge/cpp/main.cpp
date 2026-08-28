#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <deque>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <thread>
#include <optional>
#include <random>
#include <format>

struct TelemetryMessage {
    std::string topic;
    std::string payload;
    std::chrono::system_clock::time_point timestamp;
    uint32_t sequence_id{0};
};

/* Потокобезпечний буфер Store-and-Forward з обмеженням розміру (RAII) */
class StoreForwardBuffer {
public:
    explicit StoreForwardBuffer(size_t max_capacity) : max_capacity_(max_capacity) {}

    void push(TelemetryMessage msg) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (queue_.size() >= max_capacity_) {
            queue_.pop_front(); // FIFO drop: видалення застарілих даних
            dropped_count_++;
        }
        queue_.push_back(std::move(msg));
        cv_.notify_one();
    }

    std::optional<TelemetryMessage> pop() {
        std::lock_guard<std::mutex> lock(mutex_);
        if (queue_.empty()) {
            return std::nullopt;
        }
        auto msg = std::move(queue_.front());
        queue_.pop_front();
        return msg;
    }

    [[nodiscard]] size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return queue_.size();
    }

    [[nodiscard]] uint32_t dropped() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return dropped_count_;
    }

private:
    const size_t max_capacity_;
    std::deque<TelemetryMessage> queue_;
    uint32_t dropped_count_{0};
    mutable std::mutex mutex_;
    std::condition_variable cv_;
};

/* Клас промислового шлюзу */
class IndustrialGateway {
public:
    IndustrialGateway() : buffer_(512), running_(true), wan_connected_(false) {
        upstream_thread_ = std::thread(&IndustrialGateway::upstreamWorker, this);
    }

    ~IndustrialGateway() {
        running_ = false;
        if (upstream_thread_.joinable()) {
            upstream_thread_.join();
        }
    }

    void setWanConnected(bool state) {
        wan_connected_ = state;
    }

    void pollModbusNode(float raw_pressure) {
        std::cout << std::format("[MODBUS C++] Зчитано тиск: {:.2f} bar\n", raw_pressure);

        // Локальний контур безпеки (Edge Autonomy)
        if (raw_pressure > 10.0f) {
            executeEmergencyShutdown(raw_pressure);
        }

        TelemetryMessage msg{
            .topic = "plant/unit1/telemetry/pressure",
            .payload = std::format(R"({{"dev":"boiler_1","val":{:.2f},"unit":"bar"}})", raw_pressure),
            .timestamp = std::chrono::system_clock::now(),
            .sequence_id = ++seq_counter_
        };
        buffer_.push(std::move(msg));
    }

    void receiveBleBeacon(float temperature) {
        TelemetryMessage msg{
            .topic = "plant/unit1/telemetry/temperature",
            .payload = std::format(R"({{"dev":"ble_sensor_a4","val":{:.2f},"unit":"C"}})", temperature),
            .timestamp = std::chrono::system_clock::now(),
            .sequence_id = ++seq_counter_
        };
        buffer_.push(std::move(msg));
    }

    [[nodiscard]] size_t bufferSize() const { return buffer_.size(); }
    [[nodiscard]] uint32_t droppedCount() const { return buffer_.dropped(); }

private:
    void executeEmergencyShutdown(float pressure) {
        std::cout << std::format("[AUTONOMY ALERT C++] Тиск {:.2f} > 10.0 bar! "
                                 "Локальна дія: Modbus Coil 0x0010 = ON\n", pressure);
    }

    void upstreamWorker() {
        while (running_) {
            if (!wan_connected_) {
                std::this_thread::sleep_for(std::chrono::milliseconds(200));
                continue;
            }

            while (wan_connected_) {
                auto msg = buffer_.pop();
                if (!msg) break;

                std::cout << std::format("[MQTT PUB C++] -> {} : {}\n",
                                         msg->topic, msg->payload);
                std::this_thread::sleep_for(std::chrono::milliseconds(20)); // Rate limit
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    }

    StoreForwardBuffer buffer_;
    std::atomic<bool> running_{false};
    std::atomic<bool> wan_connected_{false};
    std::atomic<uint32_t> seq_counter_{0};
    std::thread upstream_thread_;
};

int main() {
    std::cout << "=== Старт IoT-шлюзу (C++20 версія) ===\n";
    IndustrialGateway gateway;

    std::mt19937 rng(42);
    std::uniform_real_distribution<float> press_dist(7.5f, 11.5f);
    std::uniform_real_distribution<float> temp_dist(38.0f, 44.0f);

    for (int step = 1; step <= 10; ++step) {
        std::cout << std::format("\n--- ТАКТ СИСТЕМИ {} ---\n", step);

        if (step >= 3 && step <= 7) {
            if (step == 3) std::cout << "[WAN] Обрив з'єднання! Активовано Store-and-Forward.\n";
            gateway.setWanConnected(false);
        } else {
            if (step == 8 || step == 1) std::cout << "[WAN] Зв'язок відновлено!\n";
            gateway.setWanConnected(true);
        }

        gateway.pollModbusNode(press_dist(rng));
        gateway.receiveBleBeacon(temp_dist(rng));

        std::cout << std::format("[BUFFER STATUS] У черзі: {}, Втрачено: {}\n",
                                 gateway.bufferSize(), gateway.droppedCount());

        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    std::cout << "=== Роботу шлюзу завершено ===\n";
    return 0;
}
