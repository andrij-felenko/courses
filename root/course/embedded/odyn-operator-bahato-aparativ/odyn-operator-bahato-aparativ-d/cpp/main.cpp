#include <iostream>
#include <vector>
#include <cmath>
#include <chrono>
#include <string>
#include <algorithm>
#include <optional>
#include <span>

enum class VehicleStatus : uint8_t {
    Nominal  = 0,
    Advisory = 1,
    Warning  = 2,
    Critical = 3
};

struct VehicleTelemetry {
    uint8_t id{0};
    float lat{0.0f};
    float lon{0.0f};
    float screen_x{0.0f};
    float screen_y{0.0f};
    float battery_pct{100.0f};
    float speed_mps{0.0f};
    std::chrono::steady_clock::time_point last_heartbeat{};
    VehicleStatus status{VehicleStatus::Nominal};
    bool active{false};
};

struct ScreenCluster {
    uint8_t cluster_id{0};
    std::vector<uint8_t> member_ids{};
    float center_x{0.0f};
    float center_y{0.0f};
    float avg_speed_mps{0.0f};
    VehicleStatus worst_status{VehicleStatus::Nominal};
};

struct FleetAlert {
    uint8_t vehicle_id{0};
    VehicleStatus priority{VehicleStatus::Nominal};
    std::chrono::steady_clock::time_point timestamp{};
    std::string message{};
    bool acknowledged{false};
};

class FleetAggregator {
public:
    static constexpr float ClusterRadiusPx = 45.0f;
    static constexpr size_t MaxVehicles = 64;

    FleetAggregator() : vehicles_(MaxVehicles) {}

    void update_vehicle(uint8_t id, float lat, float lon, float sx, float sy,
                        float battery, float speed,
                        std::chrono::steady_clock::time_point now) {
        if (id >= vehicles_.size()) return;
        auto& v = vehicles_[id];
        v.id = id;
        v.lat = lat;
        v.lon = lon;
        v.screen_x = sx;
        v.screen_y = sy;
        v.battery_pct = battery;
        v.speed_mps = speed;
        v.last_heartbeat = now;
        v.active = true;

        classify_status(v, now);
    }

    void recalculate_clusters() {
        clusters_.clear();
        std::vector<bool> assigned(vehicles_.size(), false);

        for (size_t i = 0; i < vehicles_.size(); ++i) {
            if (!vehicles_[i].active || assigned[i]) continue;

            ScreenCluster cluster;
            cluster.cluster_id = static_cast<uint8_t>(clusters_.size() + 1);
            cluster.worst_status = VehicleStatus::Nominal;

            float sum_x = 0.0f, sum_y = 0.0f, sum_spd = 0.0f;

            for (size_t j = i; j < vehicles_.size(); ++j) {
                if (!vehicles_[j].active || assigned[j]) continue;

                float dx = vehicles_[i].screen_x - vehicles_[j].screen_x;
                float dy = vehicles_[i].screen_y - vehicles_[j].screen_y;
                float dist = std::hypot(dx, dy);

                if (dist <= ClusterRadiusPx || i == j) {
                    assigned[j] = true;
                    cluster.member_ids.push_back(vehicles_[j].id);
                    sum_x += vehicles_[j].screen_x;
                    sum_y += vehicles_[j].screen_y;
                    sum_spd += vehicles_[j].speed_mps;

                    // Принцип найгіршого стану: ескалація статусу всього кластера
                    if (static_cast<uint8_t>(vehicles_[j].status) >
                        static_cast<uint8_t>(cluster.worst_status)) {
                        cluster.worst_status = vehicles_[j].status;
                    }
                }
            }

            if (!cluster.member_ids.empty()) {
                const auto count = static_cast<float>(cluster.member_ids.size());
                cluster.center_x = sum_x / count;
                cluster.center_y = sum_y / count;
                cluster.avg_speed_mps = sum_spd / count;
                clusters_.push_back(std::move(cluster));
            }
        }
    }

    [[nodiscard]] float estimate_workload_pct() const noexcept {
        size_t active_count = 0;
        size_t warning_count = 0;

        for (const auto& v : vehicles_) {
            if (v.active) {
                ++active_count;
                if (v.status >= VehicleStatus::Warning) {
                    ++warning_count;
                }
            }
        }

        // 1.5% на кожен автономний борт + 25% на кожну активну аномалію
        float total_w = static_cast<float>(active_count) * 1.5f +
                        static_cast<float>(warning_count) * 25.0f;
        return std::min(100.0f, total_w);
    }

    [[nodiscard]] std::span<const ScreenCluster> clusters() const noexcept {
        return clusters_;
    }

private:
    static void classify_status(VehicleTelemetry& v, std::chrono::steady_clock::time_point now) {
        using namespace std::chrono_literals;
        const auto silence = now - v.last_heartbeat;

        if (v.battery_pct < 15.0f || silence > 3000ms) {
            v.status = VehicleStatus::Critical;
        } else if (v.battery_pct < 30.0f || silence > 1500ms) {
            v.status = VehicleStatus::Warning;
        } else if (v.battery_pct < 45.0f) {
            v.status = VehicleStatus::Advisory;
        } else {
            v.status = VehicleStatus::Nominal;
        }
    }

    std::vector<VehicleTelemetry> vehicles_;
    std::vector<ScreenCluster> clusters_;
    std::vector<FleetAlert> alerts_;
};
