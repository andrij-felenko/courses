#include <array>
#include <cmath>
#include <cstdint>
#include <numeric>
#include <span>
#include <algorithm>

namespace navigation {

enum class SpoofState : uint8_t {
    Clean = 0,
    Degraded = 1,
    ConfirmedSpoof = 2
};

struct Vec3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr double dot(const Vec3& o) const noexcept {
        return x * o.x + y * o.y + z * o.z;
    }

    [[nodiscard]] constexpr Vec3 operator-(const Vec3& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
};

struct SatObservation {
    uint8_t prn{0};
    double elevation_rad{0.0};
    double cno_dbhz{0.0};
    double doppler_mps{0.0};
    Vec3 los_vector{};
    Vec3 sat_velocity{};
    double pseudorange_m{0.0};
};

struct ImuStateSample {
    uint64_t timestamp_us{0};
    Vec3 velocity_ecef{};
    Vec3 accel_body{};
};

template <size_t BufferSize = 64>
class GnssSpoofingDetector {
public:
    constexpr GnssSpoofingDetector() noexcept = default;

    void push_imu_sample(uint64_t ts_us, const Vec3& vel, const Vec3& acc) noexcept {
        const size_t idx = imu_head_ % BufferSize;
        imu_history_[idx] = ImuStateSample{ts_us, vel, acc};
        imu_head_++;
    }

    [[nodiscard]] SpoofState update(uint64_t gnss_ts_us, std::span<const SatObservation> sats) noexcept {
        if (sats.size() < 4) {
            state_ = SpoofState::Degraded;
            return state_;
        }

        const auto synced_imu = find_synced_imu(gnss_ts_us);
        cno_anomaly_score_ = evaluate_cno(sats);

        double doppler_score = 0.0;
        if (synced_imu.has_value()) {
            doppler_score = evaluate_doppler(sats, *synced_imu);
        }

        const double instant_threat = 0.35 * cno_anomaly_score_ + 0.65 * doppler_score;
        threat_score_ = 0.75 * threat_score_ + 0.25 * instant_threat;

        if (threat_score_ > 0.65) {
            consecutive_alarms_++;
            state_ = (consecutive_alarms_ >= 3) ? SpoofState::ConfirmedSpoof : SpoofState::Degraded;
        } else if (threat_score_ < 0.25) {
            consecutive_alarms_ = 0;
            state_ = SpoofState::Clean;
        }

        return state_;
    }

    [[nodiscard]] double threat_score() const noexcept { return threat_score_; }
    [[nodiscard]] double cno_anomaly() const noexcept { return cno_anomaly_score_; }
    [[nodiscard]] double max_doppler_residual() const noexcept { return max_doppler_residual_; }
    [[nodiscard]] SpoofState current_state() const noexcept { return state_; }

private:
    [[nodiscard]] std::optional<Vec3> find_synced_imu(uint64_t gnss_ts_us) const noexcept {
        if (imu_head_ == 0) return std::nullopt;

        const size_t count = std::min(imu_head_, BufferSize);
        size_t best_idx = 0;
        int64_t min_dt = INT64_MAX;

        for (size_t i = 0; i < count; ++i) {
            const size_t idx = (imu_head_ - 1 - i) % BufferSize;
            const int64_t dt = std::abs(static_cast<int64_t>(imu_history_[idx].timestamp_us) -
                                        static_cast<int64_t>(gnss_ts_us));
            if (dt < min_dt) {
                min_dt = dt;
                best_idx = idx;
            }
        }

        if (min_dt > 50'000) return std::nullopt; // Максимальний допуск 50 мс
        return imu_history_[best_idx].velocity_ecef;
    }

    [[nodiscard]] static double evaluate_cno(std::span<const SatObservation> sats) noexcept {
        const double mean_cno = std::accumulate(sats.begin(), sats.end(), 0.0,
            [](double acc, const auto& s) { return acc + s.cno_dbhz; }) / static_cast<double>(sats.size());

        const double variance = std::accumulate(sats.begin(), sats.end(), 0.0,
            [mean_cno](double acc, const auto& s) {
                const double d = s.cno_dbhz - mean_cno;
                return acc + d * d;
            }) / static_cast<double>(sats.size());

        const size_t low_elev_hot = std::count_if(sats.begin(), sats.end(),
            [](const auto& s) {
                return s.elevation_rad < (20.0 * M_PI / 180.0) && s.cno_dbhz > 48.0;
            });

        double score = (variance < 0.45 && mean_cno > 46.0) ? 0.6 : 0.0;
        score += static_cast<double>(low_elev_hot) * 0.25;
        return std::min(score, 1.0);
    }

    [[nodiscard]] double evaluate_doppler(std::span<const SatObservation> sats, const Vec3& imu_vel) noexcept {
        double max_res = 0.0;
        double sum_sq = 0.0;

        for (const auto& sat : sats) {
            const Vec3 rel_vel = sat.sat_velocity - imu_vel;
            const double expected_mps = rel_vel.dot(sat.los_vector);
            const double res = std::abs(sat.doppler_mps - expected_mps);

            max_res = std::max(max_res, res);
            sum_sq += res * res;
        }

        max_doppler_residual_ = max_res;
        const double rms_res = std::sqrt(sum_sq / static_cast<double>(sats.size()));

        if (rms_res < 0.6) return 0.0;
        if (rms_res > 2.5) return 1.0;
        return (rms_res - 0.6) / (2.5 - 0.6);
    }

    std::array<ImuStateSample, BufferSize> imu_history_{};
    size_t imu_head_{0};
    double threat_score_{0.0};
    double cno_anomaly_score_{0.0};
    double max_doppler_residual_{0.0};
    uint32_t consecutive_alarms_{0};
    SpoofState state_{SpoofState::Clean};
};

} // namespace navigation
