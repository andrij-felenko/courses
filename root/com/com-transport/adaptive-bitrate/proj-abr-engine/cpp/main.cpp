#include <iostream>
#include <vector>
#include <deque>
#include <numeric>
#include <algorithm>
#include <cstdint>

struct VideoProfile {
    double bitrate_bps;
    int width;
    int height;
};

struct NetworkSample {
    double bytes;
    double duration_sec;
};

class AbrEngine {
public:
    AbrEngine(std::vector<VideoProfile> profiles,
              double reservoir_sec = 8.0,
              double cushion_sec = 16.0,
              double max_buffer_sec = 40.0)
        : profiles_(std::move(profiles)),
          reservoir_sec_(reservoir_sec),
          cushion_sec_(cushion_sec),
          max_buffer_sec_(max_buffer_sec),
          smoothed_throughput_bps_(profiles_.empty() ? 0.0 : profiles_.front().bitrate_bps) {
        std::sort(profiles_.begin(), profiles_.end(), [](const auto& a, const auto& b) {
            return a.bitrate_bps < b.bitrate_bps;
        });
    }

    void add_sample(double bytes, double duration_sec) noexcept {
        if (duration_sec <= 0.001 || bytes <= 0.0) return;

        window_.push_back({bytes, duration_sec});
        if (window_.size() > kWindowSize) {
            window_.pop_front();
        }

        // Гармонійне середнє: сумарні байти / сумарний час
        double total_bytes = 0.0;
        double total_time = 0.0;
        for (const auto& sample : window_) {
            total_bytes += sample.bytes;
            total_time += sample.duration_sec;
        }
        const double inst_throughput = (total_bytes * 8.0) / total_time;

        // EWMA згладжування (α = 0.85)
        constexpr double kAlpha = 0.85;
        if (window_.size() == 1) {
            smoothed_throughput_bps_ = inst_throughput;
        } else {
            smoothed_throughput_bps_ = kAlpha * inst_throughput + (1.0 - kAlpha) * smoothed_throughput_bps_;
        }
    }

    [[nodiscard]] size_t select_profile(double current_buffer_sec) noexcept {
        if (profiles_.empty()) return 0;

        const double min_rate = profiles_.front().bitrate_bps;
        const double max_rate = profiles_.back().bitrate_bps;

        // 1. Фаза швидкого старту
        if (in_startup_) {
            if (current_buffer_sec >= (reservoir_sec_ + cushion_sec_ * 0.5)) {
                in_startup_ = false;
            } else {
                const double safe_tp = smoothed_throughput_bps_ * 0.75;
                size_t best = 0;
                for (size_t i = 0; i < profiles_.size(); ++i) {
                    if (profiles_[i].bitrate_bps <= safe_tp) {
                        best = i;
                    }
                }
                current_profile_idx_ = best;
                return best;
            }
        }

        // 2. Стаціонарна функція BBA f(B)
        double target_bitrate = min_rate;
        if (current_buffer_sec <= reservoir_sec_) {
            target_bitrate = min_rate;
        } else if (current_buffer_sec >= (reservoir_sec_ + cushion_sec_)) {
            target_bitrate = max_rate;
        } else {
            const double factor = (current_buffer_sec - reservoir_sec_) / cushion_sec_;
            target_bitrate = min_rate + factor * (max_rate - min_rate);
        }

        // 3. Захисний обмежувач за смугою (Throughput Safety Clamp 85%)
        const double throughput_cap = smoothed_throughput_bps_ * 0.85;
        target_bitrate = std::min(target_bitrate, throughput_cap);

        // 4. Пошук найближчого профілю
        size_t candidate_idx = 0;
        for (size_t i = 0; i < profiles_.size(); ++i) {
            if (profiles_[i].bitrate_bps <= target_bitrate) {
                candidate_idx = i;
            }
        }

        // Обмеження швидкості підвищення якості (не більше +1 щабля)
        if (candidate_idx > current_profile_idx_ + 1) {
            candidate_idx = current_profile_idx_ + 1;
        }

        current_profile_idx_ = candidate_idx;
        return candidate_idx;
    }

    [[nodiscard]] double smoothed_throughput() const noexcept {
        return smoothed_throughput_bps_;
    }

private:
    static constexpr size_t kWindowSize = 5;
    std::vector<VideoProfile> profiles_;
    double reservoir_sec_;
    double cushion_sec_;
    double max_buffer_sec_;

    std::deque<NetworkSample> window_;
    double smoothed_throughput_bps_{0.0};
    size_t current_profile_idx_{0};
    bool in_startup_{true};
};
