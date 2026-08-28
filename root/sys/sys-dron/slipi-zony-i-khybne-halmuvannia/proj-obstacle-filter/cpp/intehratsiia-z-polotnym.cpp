#include <cstdint>
#include <vector>
#include <array>
#include <cmath>
#include <limits>

struct ObstacleDistancePayload {
    uint64_t timestamp_us{0};
    std::array<uint16_t, 72> distances{};
    uint16_t min_distance_cm{20};
    uint16_t max_distance_cm{2000};
    float increment_deg{5.0f};

    static constexpr size_t SectorCount = 72;

    void update_from_voxels(const std::unordered_map<VoxelCoord, VoxelData, VoxelCoordHash>& voxels,
                            const VehicleKinematics& kin,
                            float voxel_size,
                            uint64_t now_us) noexcept {
        timestamp_us = now_us;
        distances.fill(std::numeric_limits<uint16_t>::max());

        for (const auto& [coord, data] : voxels) {
            if (!data.is_occupied) continue;

            const float wx = (static_cast<float>(coord.x) + 0.5f) * voxel_size;
            const float wy = (static_cast<float>(coord.y) + 0.5f) * voxel_size;
            const float wz = (static_cast<float>(coord.z) + 0.5f) * voxel_size;

            const float dx = wx - kin.x;
            const float dy = wy - kin.y;
            const float dz = wz - kin.z;

            if (std::abs(dz) > 1.5f) continue;

            const float dist_m = std::sqrt(dx * dx + dy * dy);
            if (dist_m < 0.2f || dist_m > 20.0f) continue;

            float yaw_body = std::atan2(dy, dx) - std::atan2(2.0f * (kin.orientation.w * kin.orientation.z + kin.orientation.x * kin.orientation.y),
                                                             1.0f - 2.0f * (kin.orientation.y * kin.orientation.y + kin.orientation.z * kin.orientation.z));
            
            constexpr float TwoPi = 6.283185307f;
            while (yaw_body < 0.0f) yaw_body += TwoPi;
            while (yaw_body >= TwoPi) yaw_body -= TwoPi;

            const size_t sector = static_cast<size_t>(std::floor(yaw_body / (TwoPi / static_cast<float>(SectorCount)))) % SectorCount;
            const uint16_t dist_cm = static_cast<uint16_t>(dist_m * 100.0f);
            if (dist_cm < distances[sector]) {
                distances[sector] = dist_cm;
            }
        }
    }
};
