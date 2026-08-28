#include <array>
#include <cstdint>
#include <cmath>
#include <optional>
#include <span>

namespace obstacle_fusion {

constexpr size_t MaxTracks = 8;
constexpr uint8_t ConfirmationThresholdM = 3;
constexpr uint8_t HistoryWindowN = 4;
constexpr uint8_t MaxLostFrames = 5;

enum class ArbitrationState : uint8_t {
    Tentative = 0,
    Validating,
    Confirmed,
    Coasting,
    Rejected
};

enum class ObjectClass : uint8_t {
    Person = 0,
    Vehicle,
    ObstacleBox,
    Count
};

struct ClassPhysicsLimits {
    float h_min;
    float h_max;
    float v_max;
    float a_max;
};

constexpr std::array<ClassPhysicsLimits, static_cast<size_t>(ObjectClass::Count)> Limits = {{
    { 0.6f, 2.0f, 8.0f,  12.0f }, // Person
    { 1.2f, 3.5f, 40.0f, 15.0f }, // Vehicle
    { 0.2f, 2.5f, 2.0f,  5.0f  }  // ObstacleBox
}};

struct CameraIntrinsics {
    float fx;
    float fy;
    float cx;
    float cy;
};

struct BoundingBoxDetection {
    float u_min;
    float v_min;
    float u_max;
    float v_max;
    float score;
    ObjectClass cls;
};

struct RangeSensorData {
    float distance_m{0.0f};
    float offset_x{0.0f};
    float offset_y{0.0f};
    float offset_z{0.0f};
    bool valid{false};
};

struct Vector3D {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    constexpr Vector3D operator+(const Vector3D& o) const noexcept {
        return { x + o.x, y + o.y, z + o.z };
    }
    constexpr Vector3D operator-(const Vector3D& o) const noexcept {
        return { x - o.x, y - o.y, z - o.z };
    }
    constexpr float length_squared() const noexcept {
        return x * x + y * y + z * z;
    }
};

class ObjectTrack {
public:
    uint32_t track_id{0};
    ArbitrationState state{ArbitrationState::Tentative};
    ObjectClass cls{ObjectClass::ObstacleBox};
    Vector3D position;
    Vector3D velocity;
    uint8_t hit_history{0};
    uint8_t lost_counter{0};
    bool is_active{false};

    [[nodiscard]] uint8_t hit_count() const noexcept {
        uint8_t count = 0;
        for (uint8_t b = 0; b < HistoryWindowN; ++b) {
            if ((hit_history >> b) & 1U) ++count;
        }
        return count;
    }
};

class ObstacleVerifier {
public:
    constexpr explicit ObstacleVerifier(CameraIntrinsics cam) noexcept
        : cam_(cam) {}

    [[nodiscard]] bool verify_geometry(const BoundingBoxDetection& det, float distance_m) const noexcept {
        if (distance_m < 0.1f) return false;
        
        const float h_measured = det.v_max - det.v_min;
        if (h_measured <= 1.0f) return false;

        const auto& lim = Limits[static_cast<size_t>(det.cls)];
        const float h_exp_min = (cam_.fy * lim.h_min) / distance_m;
        const float h_exp_max = (cam_.fy * lim.h_max) / distance_m;

        constexpr float Tolerance = 0.30f;
        return (h_measured >= h_exp_min * (1.0f - Tolerance) &&
                h_measured <= h_exp_max * (1.0f + Tolerance));
    }

    [[nodiscard]] bool verify_sensor_cross_check(const BoundingBoxDetection& det,
                                                 const RangeSensorData& rng) const noexcept {
        if (!rng.valid || rng.distance_m <= 0.05f) return false;

        const float z_cam = rng.distance_m + rng.offset_z;
        if (z_cam <= 0.05f) return false;

        const float u_proj = cam_.cx + cam_.fx * (rng.offset_x / z_cam);
        const float v_proj = cam_.cy + cam_.fy * (rng.offset_y / z_cam);

        return (u_proj >= det.u_min && u_proj <= det.u_max &&
                v_proj >= det.v_min && v_proj <= det.v_max);
    }

    [[nodiscard]] bool verify_kinematics(const ObjectTrack& trk, const Vector3D& meas_pos,
                                         float dt_sec) const noexcept {
        if (dt_sec <= 0.0f) return false;

        const Vector3D pred_pos = trk.position + Vector3D{ trk.velocity.x * dt_sec,
                                                           trk.velocity.y * dt_sec,
                                                           trk.velocity.z * dt_sec };
        const float dist_sq = (meas_pos - pred_pos).length_squared();

        const auto& lim = Limits[static_cast<size_t>(trk.cls)];
        const float r_gate = 0.5f * lim.a_max * dt_sec * dt_sec + 0.35f;

        return dist_sq <= (r_gate * r_gate);
    }

    void update(std::span<const BoundingBoxDetection> detections,
                const RangeSensorData& range, float dt_sec) noexcept {
        std::array<bool, MaxTracks> matched{};

        for (const auto& det : detections) {
            if (det.score < 0.40f) continue;

            const float est_dist = range.valid ? range.distance_m : 2.5f;
            if (!verify_geometry(det, est_dist)) continue;

            const float u_c = (det.u_min + det.u_max) * 0.5f;
            const float v_c = (det.v_min + det.v_max) * 0.5f;
            const Vector3D meas_pos{
                (u_c - cam_.cx) * est_dist / cam_.fx,
                (v_c - cam_.cy) * est_dist / cam_.fy,
                est_dist
            };

            std::optional<size_t> best_idx;
            float min_d_sq = 1e9f;

            for (size_t t = 0; t < MaxTracks; ++t) {
                if (!tracks_[t].is_active || matched[t]) continue;
                if (tracks_[t].cls != det.cls) continue;

                if (verify_kinematics(tracks_[t], meas_pos, dt_sec)) {
                    const float d_sq = (meas_pos - tracks_[t].position).length_squared();
                    if (d_sq < min_d_sq) {
                        min_d_sq = d_sq;
                        best_idx = t;
                    }
                }
            }

            if (best_idx.has_value()) {
                const size_t idx = *best_idx;
                auto& trk = tracks_[idx];
                matched[idx] = true;
                trk.lost_counter = 0;
                trk.hit_history = static_cast<uint8_t>(((trk.hit_history << 1) | 1U) & ((1U << HistoryWindowN) - 1U));

                trk.velocity.x = 0.7f * trk.velocity.x + 0.3f * ((meas_pos.x - trk.position.x) / dt_sec);
                trk.velocity.y = 0.7f * trk.velocity.y + 0.3f * ((meas_pos.y - trk.position.y) / dt_sec);
                trk.velocity.z = 0.7f * trk.velocity.z + 0.3f * ((meas_pos.z - trk.position.z) / dt_sec);
                trk.position = meas_pos;

                const uint8_t hits = trk.hit_count();
                if (trk.state == ArbitrationState::Tentative && hits >= 2) {
                    trk.state = ArbitrationState::Validating;
                }
                if (trk.state == ArbitrationState::Validating && hits >= ConfirmationThresholdM) {
                    trk.state = ArbitrationState::Confirmed;
                }
                if (trk.state == ArbitrationState::Coasting) {
                    trk.state = ArbitrationState::Confirmed;
                }
            } else {
                for (auto& trk : tracks_) {
                    if (!trk.is_active) {
                        trk.track_id = next_track_id_++;
                        trk.is_active = true;
                        trk.state = ArbitrationState::Tentative;
                        trk.cls = det.cls;
                        trk.position = meas_pos;
                        trk.velocity = { 0.0f, 0.0f, 0.0f };
                        trk.hit_history = 1;
                        trk.lost_counter = 0;
                        break;
                    }
                }
            }
        }

        for (size_t t = 0; t < MaxTracks; ++t) {
            if (!tracks_[t].is_active || matched[t]) continue;

            auto& trk = tracks_[t];
            trk.lost_counter++;
            trk.hit_history = static_cast<uint8_t>((trk.hit_history << 1) & ((1U << HistoryWindowN) - 1U));

            trk.position.x += trk.velocity.x * dt_sec;
            trk.position.y += trk.velocity.y * dt_sec;
            trk.position.z += trk.velocity.z * dt_sec;

            if (trk.state == ArbitrationState::Confirmed) {
                trk.state = ArbitrationState::Coasting;
            }

            if (trk.lost_counter >= MaxLostFrames || trk.state == ArbitrationState::Tentative) {
                trk.state = ArbitrationState::Rejected;
                trk.is_active = false;
            }
        }
    }

    [[nodiscard]] std::span<const ObjectTrack> tracks() const noexcept {
        return tracks_;
    }

private:
    CameraIntrinsics cam_;
    std::array<ObjectTrack, MaxTracks> tracks_{};
    uint32_t next_track_id_{1};
};

} // namespace obstacle_fusion
