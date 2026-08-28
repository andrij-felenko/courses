#include <iostream>
#include <vector>
#include <queue>
#include <cstdint>
#include <span>
#include <string_view>
#include <memory>
#include <format>

enum class SensorType : uint8_t {
    Imu  = 1,
    Mag  = 2,
    Baro = 3,
    Gps  = 4
};

struct ReplayPacket {
    uint64_t timestamp_us{0};
    SensorType type{SensorType::Imu};
    std::vector<uint8_t> payload;

    // Компаратор для std::priority_queue (Min-Heap за timestamp)
    bool operator>(const ReplayPacket& other) const noexcept {
        return timestamp_us > other.timestamp_us;
    }
};

class ReplayEngine {
public:
    void pushPacket(ReplayPacket packet) {
        queue_.push(std::move(packet));
    }

    void executeReplay() {
        uint64_t simulated_time_us = 0;

        while (!queue_.empty()) {
            ReplayPacket pkt = std::move(const_cast<ReplayPacket&>(queue_.top()));
            queue_.pop();

            // Монотонне просування віртуального годинника
            if (pkt.timestamp_us > simulated_time_us) {
                simulated_time_us = pkt.timestamp_us;
            }

            dispatchToVirtualBus(pkt.type, simulated_time_us, pkt.payload);
        }

        std::cout << std::format("[Завершення переграшу] Усі кадри оброблено. Кінцевий час: {} мкс\n",
                                 simulated_time_us);
    }

private:
    std::priority_queue<ReplayPacket, std::vector<ReplayPacket>, std::greater<ReplayPacket>> queue_;

    void dispatchToVirtualBus(SensorType type, uint64_t t_sim, std::span<const uint8_t> payload) const {
        (void)payload;
        std::string_view name = "НЕВІДОМИЙ";
        switch (type) {
            case SensorType::Imu:  name = "IMU (1000 Гц)"; break;
            case SensorType::Mag:  name = "MAG (50 Гц)";   break;
            case SensorType::Baro: name = "BARO (100 Гц)"; break;
            case SensorType::Gps:  name = "GPS (10 Гц)";   break;
        }
        std::cout << std::format("[t_sim = {:10} мкс] Впорскування топіка uORB -> {}\n",
                                 t_sim, name);
    }
};
