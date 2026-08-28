#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <span>
#include <unordered_map>
#include <optional>
#include <chrono>

struct Point3D {
    float x{0.0f}, y{0.0f}, z{0.0f};
    float intensity{0.0f};
};

struct Quaternion {
    float w{1.0f}, x{0.0f}, y{0.0f}, z{0.0f};

    [[nodiscard]] Point3D rotate(const Point3D& v) const noexcept {
        const float tx = 2.0f * (y * v.z - z * v.y);
        const float ty = 2.0f * (z * v.x - x * v.z);
        const float tz = 2.0f * (x * v.y - y * v.x);

        return Point3D{
            v.x + w * tx + (y * tz - z * ty),
            v.y + w * ty + (z * tx - x * tz),
            v.z + w * tz + (x * ty - y * tx),
            v.intensity
        };
    }
};

struct VehicleKinematics {
    float x{0.0f}, y{0.0f}, z{0.0f};
    float vx{0.0f}, vy{0.0f}, vz{0.0f};
    Quaternion orientation{};
    float pitch_rad{0.0f};

    [[nodiscard]] float speed() const noexcept {
        return std::sqrt(vx * vx + vy * vy + vz * vz);
    }
};

struct VoxelCoord {
    int32_t x{0}, y{0}, z{0};

    bool operator==(const VoxelCoord& o) const noexcept {
        return x == o.x && y == o.y && z == o.z;
    }
};

struct VoxelCoordHash {
    std::size_t operator()(const VoxelCoord& v) const noexcept {
        return static_cast<std::size_t>(v.x * 73856093 ^ v.y * 19349663 ^ v.z * 83492791);
    }
};

struct VoxelData {
    float weight{0.0f};
    float last_time_sec{0.0f};
    bool is_occupied{false};
};

class ObstacleFilterPipeline {
public:
    struct Config {
        int k_neighbors{8};
        float alpha_factor{1.5f};
        float hash_cell_size{0.40f};
        float voxel_size{0.20f};
        float decay_rate{2.5f};
        float max_weight{10.0f};
        float occ_threshold{3.0f};
        float max_brake_accel{4.0f};
        float sensor_vfov_rad{58.0f * 0.0174532925f};
        float safety_margin_m{1.2f};
    };

    explicit ObstacleFilterPipeline(Config cfg = {}) : cfg_(cfg) {}

    struct ProcessResult {
        std::vector<Point3D> filtered_points;
        float max_safe_speed{15.0f};
        bool braking_threat{false};
    };

    [[nodiscard]] ProcessResult process(std::span<const Point3D> raw_points, 
                                        const VehicleKinematics& kin, 
                                        float current_time_sec) {
        ProcessResult result;

        // 1. Трансформація у світову систему координат ENU
        std::vector<Point3D> world_points;
        world_points.reserve(raw_points.size());
        for (const auto& pt : raw_points) {
            const float r_sq = pt.x * pt.x + pt.y * pt.y + pt.z * pt.z;
            if (r_sq < 0.09f || r_sq > 400.0f) continue;

            Point3D rotated = kin.orientation.rotate(pt);
            world_points.push_back(Point3D{
                rotated.x + kin.x,
                rotated.y + kin.y,
                rotated.z + kin.z,
                pt.intensity
            });
        }

        // 2. Статистичний фільтр викидів (Spatial Hash SOR)
        result.filtered_points = remove_statistical_outliers(world_points);

        // 3. Оновлення воксельної сітки часової персистентності
        update_persistence(result.filtered_points, current_time_sec);

        // 4. Оцінка безпеки та компенсація сліпих зон
        result.max_safe_speed = calculate_safe_speed(kin);
        result.braking_threat = evaluate_braking_threat(kin);

        return result;
    }

private:
    Config cfg_;
    std::unordered_map<VoxelCoord, VoxelData, VoxelCoordHash> voxel_map_;

    [[nodiscard]] std::vector<Point3D> remove_statistical_outliers(std::span<const Point3D> points) const {
        if (points.size() < static_cast<size_t>(cfg_.k_neighbors)) return {};

        std::unordered_map<VoxelCoord, std::vector<size_t>, VoxelCoordHash> spatial_hash;
        const float inv_cell = 1.0f / cfg_.hash_cell_size;

        for (size_t i = 0; i < points.size(); ++i) {
            VoxelCoord key{
                static_cast<int32_t>(std::floor(points[i].x * inv_cell)),
                static_cast<int32_t>(std::floor(points[i].y * inv_cell)),
                static_cast<int32_t>(std::floor(points[i].z * inv_cell))
            };
            spatial_hash[key].push_back(i);
        }

        std::vector<float> mean_distances(points.size(), 999.0f);
        double sum_mean = 0.0;

        for (size_t i = 0; i < points.size(); ++i) {
            const int32_t ix = static_cast<int32_t>(std::floor(points[i].x * inv_cell));
            const int32_t iy = static_cast<int32_t>(std::floor(points[i].y * inv_cell));
            const int32_t iz = static_cast<int32_t>(std::floor(points[i].z * inv_cell));

            std::vector<float> dists;
            dists.reserve(64);

            for (int32_t dx = -1; dx <= 1; ++dx) {
                for (int32_t dy = -1; dy <= 1; ++dy) {
                    for (int32_t dz = -1; dz <= 1; ++dz) {
                        auto it = spatial_hash.find(VoxelCoord{ix + dx, iy + dy, iz + dz});
                        if (it == spatial_hash.end()) continue;

                        for (size_t idx : it->second) {
                            if (idx == i) continue;
                            const float ddx = points[i].x - points[idx].x;
                            const float ddy = points[i].y - points[idx].y;
                            const float ddz = points[i].z - points[idx].z;
                            dists.push_back(std::sqrt(ddx * ddx + ddy * ddy + ddz * ddz));
                        }
                    }
                }
            }

            if (dists.size() < static_cast<size_t>(cfg_.k_neighbors)) continue;

            std::nth_element(dists.begin(), dists.begin() + cfg_.k_neighbors, dists.end());
            float sum_k = 0.0f;
            for (int k = 0; k < cfg_.k_neighbors; ++k) sum_k += dists[k];

            mean_distances[i] = sum_k / static_cast<float>(cfg_.k_neighbors);
            sum_mean += mean_distances[i];
        }

        const double mu = sum_mean / static_cast<double>(points.size());
        double sum_sq = 0.0;
        for (float d : mean_distances) {
            if (d < 900.0f) sum_sq += (d - mu) * (d - mu);
        }
        const double sigma = std::sqrt(sum_sq / static_cast<double>(points.size()));
        const float threshold = static_cast<float>(mu + cfg_.alpha_factor * sigma);

        std::vector<Point3D> clean_pts;
        clean_pts.reserve(points.size());
        for (size_t i = 0; i < points.size(); ++i) {
            if (mean_distances[i] <= threshold) {
                clean_pts.push_back(points[i]);
            }
        }
        return clean_pts;
    }

    void update_persistence(std::span<const Point3D> points, float current_time_sec) {
        for (auto it = voxel_map_.begin(); it != voxel_map_.end();) {
            const float dt = current_time_sec - it->second.last_time_sec;
            if (dt > 0.02f) {
                it->second.weight -= cfg_.decay_rate * dt;
                it->second.last_time_sec = current_time_sec;
            }
            if (it->second.weight <= 0.0f) {
                it = voxel_map_.erase(it);
            } else {
                it->second.is_occupied = (it->second.weight >= cfg_.occ_threshold);
                ++it;
            }
        }

        const float inv_vox = 1.0f / cfg_.voxel_size;
        for (const auto& pt : points) {
            VoxelCoord idx{
                static_cast<int32_t>(std::floor(pt.x * inv_vox)),
                static_cast<int32_t>(std::floor(pt.y * inv_vox)),
                static_cast<int32_t>(std::floor(pt.z * inv_vox))
            };

            auto& v = voxel_map_[idx];
            v.weight = std::min(v.weight + 1.0f, cfg_.max_weight);
            v.last_time_sec = current_time_sec;
            v.is_occupied = (v.weight >= cfg_.occ_threshold);
        }
    }

    [[nodiscard]] float calculate_safe_speed(const VehicleKinematics& kin) const noexcept {
        const float upper_clearance = (cfg_.sensor_vfov_rad * 0.5f) + kin.pitch_rad;
        if (upper_clearance < 0.05f) {
            return 3.0f;
        }
        if (upper_clearance < 0.20f) {
            return 3.0f + (upper_clearance / 0.20f) * 7.0f;
        }
        return 15.0f;
    }

    [[nodiscard]] bool evaluate_braking_threat(const VehicleKinematics& kin) const noexcept {
        const float speed = kin.speed();
        if (speed < 0.15f) return false;

        const float stop_dist = (speed * speed) / (2.0f * cfg_.max_brake_accel) + speed * 0.15f + cfg_.safety_margin_m;
        const float dir_x = kin.vx / speed;
        const float dir_y = kin.vy / speed;
        const float dir_z = kin.vz / speed;

        for (const auto& [idx, data] : voxel_map_) {
            if (!data.is_occupied) continue;

            const float wx = (static_cast<float>(idx.x) + 0.5f) * cfg_.voxel_size;
            const float wy = (static_cast<float>(idx.y) + 0.5f) * cfg_.voxel_size;
            const float wz = (static_cast<float>(idx.z) + 0.5f) * cfg_.voxel_size;

            const float rx = wx - kin.x;
            const float ry = wy - kin.y;
            const float rz = wz - kin.z;

            const float proj = rx * dir_x + ry * dir_y + rz * dir_z;
            if (proj > 0.0f && proj <= stop_dist) {
                const float px = rx - proj * dir_x;
                const float py = ry - proj * dir_y;
                const float pz = rz - proj * dir_z;
                const float lateral = std::sqrt(px * px + py * py + pz * pz);

                if (lateral < 1.1f) {
                    return true;
                }
            }
        }
        return false;
    }
};
