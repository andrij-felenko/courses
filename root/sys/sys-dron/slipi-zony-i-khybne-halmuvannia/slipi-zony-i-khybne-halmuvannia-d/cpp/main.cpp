#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <span>
#include <unordered_map>
#include <optional>

struct Point3D {
    float x{0.0f}, y{0.0f}, z{0.0f};
    float intensity{0.0f};
};

struct DroneKinematics {
    float x{0.0f}, y{0.0f}, z{0.0f};
    float vx{0.0f}, vy{0.0f}, vz{0.0f};
    float roll{0.0f}, pitch{0.0f}, yaw{0.0f};

    [[nodiscard]] float speed() const noexcept {
        return std::sqrt(vx * vx + vy * vy + vz * vz);
    }
};

struct VoxelIndex {
    int32_t x{0}, y{0}, z{0};

    bool operator==(const VoxelIndex& other) const noexcept {
        return x == other.x && y == other.y && z == other.z;
    }
};

struct VoxelIndexHash {
    std::size_t operator()(const VoxelIndex& v) const noexcept {
        return static_cast<std::size_t>(v.x * 73856093 ^ v.y * 19349663 ^ v.z * 83492791);
    }
};

struct VoxelState {
    float weight{0.0f};
    float last_updated{0.0f};
};

class ObstacleValidationFilter {
public:
    static constexpr float VoxelSize = 0.2f;        // 20 см
    static constexpr float OccupiedThreshold = 3.0f;
    static constexpr float MaxWeight = 10.0f;
    static constexpr float DecayRate = 2.0f;       // ваги на секунду

    void process_scan(std::span<const Point3D> raw_points, 
                      const DroneKinematics& kin, 
                      float current_time) {
        // 1. Часове згасання
        for (auto it = grid_.begin(); it != grid_.end();) {
            float dt = current_time - it->second.last_updated;
            if (dt > 0.02f) {
                it->second.weight -= DecayRate * dt;
                it->second.last_updated = current_time;
            }
            if (it->second.weight <= 0.0f) {
                it = grid_.erase(it);
            } else {
                ++it;
            }
        }

        // 2. Трансформація точок та оновлення сітки
        for (const auto& pt : raw_points) {
            Point3D world_pt = transform_to_world(pt, kin);
            VoxelIndex idx{
                static_cast<int32_t>(std::floor(world_pt.x / VoxelSize)),
                static_cast<int32_t>(std::floor(world_pt.y / VoxelSize)),
                static_cast<int32_t>(std::floor(world_pt.z / VoxelSize))
            };

            auto& state = grid_[idx];
            state.weight = std::min(state.weight + 1.0f, MaxWeight);
            state.last_updated = current_time;
        }
    }

    [[nodiscard]] bool check_braking_threat(const DroneKinematics& kin, 
                                           float max_decel, 
                                           float latency) const noexcept {
        const float spd = kin.speed();
        if (spd < 0.2f) return false;

        const float stop_distance = (spd * spd) / (2.0f * max_decel) + spd * latency + 1.0f;
        const float dir_x = kin.vx / spd;
        const float dir_y = kin.vy / spd;
        const float dir_z = kin.vz / spd;

        for (const auto& [idx, state] : grid_) {
            if (state.weight < OccupiedThreshold) continue;

            const float wx = idx.x * VoxelSize + VoxelSize * 0.5f;
            const float wy = idx.y * VoxelSize + VoxelSize * 0.5f;
            const float wz = idx.z * VoxelSize + VoxelSize * 0.5f;

            const float rel_x = wx - kin.x;
            const float rel_y = wy - kin.y;
            const float rel_z = wz - kin.z;

            const float longitudinal = rel_x * dir_x + rel_y * dir_y + rel_z * dir_z;
            if (longitudinal > 0.0f && longitudinal <= stop_distance) {
                const float perp_x = rel_x - longitudinal * dir_x;
                const float perp_y = rel_y - longitudinal * dir_y;
                const float perp_z = rel_z - longitudinal * dir_z;
                const float lateral = std::sqrt(perp_x * perp_x + perp_y * perp_y + perp_z * perp_z);

                if (lateral < 1.2f) { // Безпечний коридор діаметром 2.4 м
                    return true;
                }
            }
        }
        return false;
    }

private:
    std::unordered_map<VoxelIndex, VoxelState, VoxelIndexHash> grid_;

    [[nodiscard]] static Point3D transform_to_world(const Point3D& p, const DroneKinematics& k) noexcept {
        const float cy = std::cos(k.yaw), sy = std::sin(k.yaw);
        const float cp = std::cos(k.pitch), sp = std::sin(k.pitch);
        const float cr = std::cos(k.roll), sr = std::sin(k.roll);

        const float r00 = cy * cp;
        const float r01 = cy * sp * sr - sy * cr;
        const float r02 = cy * sp * cr + sy * sr;

        const float r10 = sy * cp;
        const float r11 = sy * sp * sr + cy * cr;
        const float r12 = sy * sp * cr - cy * sr;

        const float r20 = -sp;
        const float r21 = cp * sr;
        const float r22 = cp * cr;

        return Point3D{
            k.x + (r00 * p.x + r01 * p.y + r02 * p.z),
            k.y + (r10 * p.x + r11 * p.y + r12 * p.z),
            k.z + (r20 * p.x + r21 * p.y + r22 * p.z),
            p.intensity
        };
    }
};
