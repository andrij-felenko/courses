#include <iostream>
#include <vector>
#include <deque>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <span>
#include <string>
#include <sstream>
#include <iomanip>

// 1. Двійковий кадр (24 байти) та утиліти розбору
struct RawPacket {
    std::vector<uint8_t> data;
    std::chrono::system_clock::time_point ingress_time;
    uint32_t peer_id{0};
};

struct NormalizedEvent {
    std::string event_id;
    std::string device_id;
    std::chrono::system_clock::time_point timestamp;
    double temperature_c{0.0};
    double humidity_pct{0.0};
    double battery_voltage_v{0.0};
    uint16_t seq_num{0};
    bool valid{false};
};

class TelemetryCodec {
public:
    static uint16_t crc16_ccitt(std::span<const uint8_t> buffer) noexcept {
        uint16_t crc = 0xFFFF;
        for (uint8_t byte : buffer) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (int i = 0; i < 8; ++i) {
                if (crc & 0x8000) {
                    crc = (crc << 1) ^ 0x1021;
                } else {
                    crc = crc << 1;
                }
            }
        }
        return crc;
    }

    static std::vector<uint8_t> serialize_mock(uint32_t dev_id, uint32_t uptime_ms,
                                               int16_t raw_temp, uint16_t raw_hum,
                                               uint16_t raw_vbat, uint16_t seq) {
        std::vector<uint8_t> frame(24, 0);
        // Magic 0xAA55
        frame[0] = 0xAA; frame[1] = 0x55;
        frame[2] = 0x01; // Version 1
        frame[3] = 0x00; // Flags

        // Device ID (Big Endian)
        frame[4] = (dev_id >> 24) & 0xFF; frame[5] = (dev_id >> 16) & 0xFF;
        frame[6] = (dev_id >> 8) & 0xFF;  frame[7] = dev_id & 0xFF;

        // Uptime ms
        frame[8] = (uptime_ms >> 24) & 0xFF; frame[9] = (uptime_ms >> 16) & 0xFF;
        frame[10] = (uptime_ms >> 8) & 0xFF; frame[11] = uptime_ms & 0xFF;

        // Raw Temp
        frame[12] = (raw_temp >> 8) & 0xFF; frame[13] = raw_temp & 0xFF;

        // Raw Humidity
        frame[14] = (raw_hum >> 8) & 0xFF;  frame[15] = raw_hum & 0xFF;

        // Raw Battery
        frame[16] = (raw_vbat >> 8) & 0xFF; frame[17] = raw_vbat & 0xFF;

        // Seq
        frame[18] = (seq >> 8) & 0xFF;      frame[19] = seq & 0xFF;

        // Status Mask
        frame[20] = 0x00; frame[21] = 0x07; // Sensors valid + Power

        // CRC16
        uint16_t crc = crc16_ccitt(std::span<const uint8_t>(frame.data(), 22));
        frame[22] = (crc >> 8) & 0xFF;
        frame[23] = crc & 0xFF;

        return frame;
    }

    static bool parse(const RawPacket& raw, NormalizedEvent& out) noexcept {
        if (raw.data.size() < 24) return false;
        if (raw.data[0] != 0xAA || raw.data[1] != 0x55) return false;

        uint16_t expected_crc = (static_cast<uint16_t>(raw.data[22]) << 8) | raw.data[23];
        uint16_t actual_crc = crc16_ccitt(std::span<const uint8_t>(raw.data.data(), 22));
        if (expected_crc != actual_crc) return false;

        uint32_t dev_id = (static_cast<uint32_t>(raw.data[4]) << 24) |
                          (static_cast<uint32_t>(raw.data[5]) << 16) |
                          (static_cast<uint32_t>(raw.data[6]) << 8)  |
                           raw.data[7];

        int16_t raw_temp = static_cast<int16_t>((raw.data[12] << 8) | raw.data[13]);
        uint16_t raw_hum = (static_cast<uint16_t>(raw.data[14]) << 8) | raw.data[15];
        uint16_t raw_vbat = (static_cast<uint16_t>(raw.data[16]) << 8) | raw.data[17];
        uint16_t seq = (static_cast<uint16_t>(raw.data[18]) << 8) | raw.data[19];

        std::stringstream ss;
        ss << "esp32-" << std::hex << std::setw(8) << std::setfill('0') << dev_id;
        out.device_id = ss.str();
        out.timestamp = raw.ingress_time;
        out.temperature_c = raw_temp * 0.01;
        out.humidity_pct = raw_hum * 0.01;
        out.battery_voltage_v = raw_vbat * 0.001;
        out.seq_num = seq;
        out.valid = (out.temperature_c >= -40.0 && out.temperature_c <= 125.0 &&
                     out.humidity_pct >= 0.0 && out.humidity_pct <= 100.0);
        return true;
    }
};

// 2. Демпферна черга з ватерпостами та витісненням Drop-Oldest
class IngestionQueue {
public:
    explicit IngestionQueue(size_t capacity, double high_ratio = 0.85, double low_ratio = 0.60)
        : capacity_(capacity),
          high_watermark_(static_cast<size_t>(capacity * high_ratio)),
          low_watermark_(static_cast<size_t>(capacity * low_ratio)) {}

    void push(RawPacket packet) {
        std::unique_lock<std::mutex> lock(mutex_);
        if (queue_.size() >= capacity_) {
            queue_.pop_front(); // Drop Oldest
            dropped_packets_.fetch_add(1, std::memory_order_relaxed);
        }

        queue_.push_back(std::move(packet));

        if (queue_.size() >= high_watermark_) {
            backpressure_active_.store(true, std::memory_order_release);
        }

        lock.unlock();
        cv_pop_.notify_one();
    }

    bool pop(RawPacket& packet, std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        if (!cv_pop_.wait_for(lock, timeout, [this] { return !queue_.empty() || stopped_; })) {
            return false;
        }

        if (stopped_ && queue_.empty()) return false;

        packet = std::move(queue_.front());
        queue_.pop_front();

        if (queue_.size() <= low_watermark_) {
            backpressure_active_.store(false, std::memory_order_release);
        }

        return true;
    }

    void stop() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            stopped_ = true;
        }
        cv_pop_.notify_all();
    }

    bool is_backpressure_active() const noexcept {
        return backpressure_active_.load(std::memory_order_acquire);
    }

    uint64_t get_dropped_count() const noexcept {
        return dropped_packets_.load(std::memory_order_relaxed);
    }

    size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return queue_.size();
    }

private:
    const size_t capacity_;
    const size_t high_watermark_;
    const size_t low_watermark_;
    mutable std::mutex mutex_;
    std::condition_variable cv_pop_;
    std::deque<RawPacket> queue_;
    std::atomic<bool> backpressure_active_{false};
    std::atomic<uint64_t> dropped_packets_{0};
    bool stopped_{false};
};

// 3. Тестовий запуск конвеєра
int main() {
    std::cout << "Starting Telemetry Ingestion Pipeline (C++20)...\n";
    const size_t QUEUE_CAPACITY = 1000;
    IngestionQueue queue(QUEUE_CAPACITY, 0.80, 0.50);

    std::atomic<uint64_t> processed_count{0};
    std::atomic<uint64_t> valid_events{0};

    // Запуск пулу робітників (4 воркери)
    std::vector<std::thread> workers;
    for (int i = 0; i < 4; ++i) {
        workers.emplace_back([&queue, &processed_count, &valid_events, i] {
            RawPacket raw;
            while (queue.pop(raw, std::chrono::milliseconds(50))) {
                NormalizedEvent event;
                if (TelemetryCodec::parse(raw, event)) {
                    if (event.valid) {
                        valid_events.fetch_add(1, std::memory_order_relaxed);
                    }
                }
                processed_count.fetch_add(1, std::memory_order_relaxed);
            }
        });
    }

    // Симуляція пікового навантаження в приймачі
    auto start_time = std::chrono::steady_clock::now();
    const int TOTAL_BURST = 5000;

    for (int i = 0; i < TOTAL_BURST; ++i) {
        RawPacket p;
        p.data = TelemetryCodec::serialize_mock(
            0x000104A2, i * 100, 2345 + (i % 50), 5820, 3820, static_cast<uint16_t>(i)
        );
        p.ingress_time = std::chrono::system_clock::now();
        p.peer_id = i % 100;
        queue.push(std::move(p));
    }

    // Очікування завершення обробки
    while (queue.size() > 0) {
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    }
    queue.stop();

    for (auto& w : workers) {
        if (w.joinable()) w.join();
    }

    auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now() - start_time
    ).count();

    std::cout << "--- Ingestion Summary ---\n"
              << "Ingested / Sent: " << TOTAL_BURST << " frames\n"
              << "Processed:       " << processed_count.load() << "\n"
              << "Valid Events:    " << valid_events.load() << "\n"
              << "Dropped (Oldest):" << queue.get_dropped_count() << "\n"
              << "Total Time:      " << elapsed << " ms\n"
              << "Throughput:      " << (TOTAL_BURST * 1000.0 / elapsed) << " frames/sec\n";
    return 0;
}
