#include <iostream>
#include <vector>
#include <deque>
#include <span>
#include <memory>
#include <shared_mutex>
#include <mutex>
#include <cmath>
#include <algorithm>
#include <chrono>
#include <expected>
#include <string_view>
#include <string>
#include <format>
#include <cstdint>

namespace mixed_fleet::controller {

enum class RolloutState : uint8_t {
    Idle,
    Initializing,
    PromotingCohort,
    Soaking,
    EvaluatingAca,
    EmergencyKillSwitch,
    QuarantineDraining,
    RolledBack,
    PromotedFull
};

struct alignas(64) ClusterNode {
    uint32_t node_id{0};
    uint32_t major_version{1};
    bool is_canary{false};
    bool is_healthy{true};
    bool is_draining{false};
    uint32_t active_connections{0};
};

struct MannWhitneyVerdict {
    double u_statistic{0.0};
    double z_score{0.0};
    double p_value{1.0};
    bool is_significant_regression{false};
};

class alignas(64) TelemetryRingBuffer {
public:
    explicit TelemetryRingBuffer(size_t capacity = 1024) noexcept
        : capacity_(capacity), storage_(capacity, 0.0) {}

    void push(double latency_ms) noexcept {
        std::lock_guard lock(mutex_);
        storage_[head_] = latency_ms;
        head_ = (head_ + 1) % capacity_;
        if (count_ < capacity_) {
            ++count_;
        }
    }

    void clear() noexcept {
        std::lock_guard lock(mutex_);
        head_ = 0;
        count_ = 0;
    }

    [[nodiscard]] std::vector<double> snapshot() const {
        std::lock_guard lock(mutex_);
        std::vector<double> out;
        out.reserve(count_);
        for (size_t i = 0; i < count_; ++i) {
            size_t idx = (head_ + capacity_ - count_ + i) % capacity_;
            out.push_back(storage_[idx]);
        }
        return out;
    }

private:
    size_t capacity_{1024};
    size_t head_{0};
    size_t count_{0};
    std::vector<double> storage_;
    mutable std::mutex mutex_;
};

class StatisticalEngine {
public:
    static std::expected<MannWhitneyVerdict, std::string_view>
    evaluate(std::span<const double> baseline,
             std::span<const double> canary,
             double alpha_critical = 0.01) noexcept {
        if (baseline.empty() || canary.empty()) {
            return std::unexpected("Cohorts must contain at least one sample");
        }

        struct Node {
            double val;
            bool is_canary;
            double rank{0.0};
        };

        std::vector<Node> combined;
        combined.reserve(baseline.size() + canary.size());

        for (double v : baseline) combined.push_back({v, false, 0.0});
        for (double v : canary)   combined.push_back({v, true, 0.0});

        std::sort(combined.begin(), combined.end(), [](const auto& a, const auto& b) noexcept {
            return a.val < b.val;
        });

        // Обчислення рангів із корекцією однакових значень
        size_t idx = 0;
        const size_t n_total = combined.size();
        while (idx < n_total) {
            size_t end_idx = idx;
            while (end_idx + 1 < n_total && combined[end_idx + 1].val == combined[idx].val) {
                ++end_idx;
            }
            const double mean_rank = 1.0 + static_cast<double>(idx + end_idx) / 2.0;
            for (size_t size_k = idx; size_k <= end_idx; ++size_k) {
                combined[size_k].rank = mean_rank;
            }
            idx = end_idx + 1;
        }

        double sum_r1 = 0.0;
        for (const auto& item : combined) {
            if (!item.is_canary) sum_r1 += item.rank;
        }

        const double n1 = static_cast<double>(baseline.size());
        const double n2 = static_cast<double>(canary.size());

        const double u1 = n1 * n2 + (n1 * (n1 + 1.0)) / 2.0 - sum_r1;
        const double u2 = n1 * n2 - u1;
        const double u_min = std::min(u1, u2);

        const double mean_u = (n1 * n2) / 2.0;
        const double std_u = std::sqrt((n1 * n2 * (n1 + n2 + 1.0)) / 12.0);

        MannWhitneyVerdict res;
        res.u_statistic = u_min;
        res.z_score = (std_u > 1e-7) ? (u_min - mean_u) / std_u : 0.0;
        res.p_value = std::erfc(std::abs(res.z_score) / std::sqrt(2.0));
        res.is_significant_regression = (res.p_value < alpha_critical && res.z_score < 0.0);

        return res;
    }
};

class ProductionCanaryRolloutController {
public:
    explicit ProductionCanaryRolloutController(double critical_z = -2.58) noexcept
        : critical_z_score_(critical_z) {}

    void registerNode(ClusterNode node) {
        std::unique_lock lock(state_rwlock_);
        nodes_.push_back(node);
    }

    void startRollout() {
        std::unique_lock lock(state_rwlock_);
        if (state_ == RolloutState::Idle) {
            state_ = RolloutState::Initializing;
            state_entered_time_ = std::chrono::steady_clock::now();
        }
    }

    void recordLatency(bool is_canary, double latency_ms) {
        if (is_canary) {
            canary_buffer_.push(latency_ms);
        } else {
            baseline_buffer_.push(latency_ms);
        }
    }

    [[nodiscard]] std::expected<int32_t, std::string_view>
    routeRequest(uint32_t user_hash) const noexcept {
        std::shared_lock lock(state_rwlock_);

        if (state_ == RolloutState::EmergencyKillSwitch ||
            state_ == RolloutState::QuarantineDraining ||
            state_ == RolloutState::RolledBack) {
            for (const auto& node : nodes_) {
                if (!node.is_canary && node.is_healthy && !node.is_draining) {
                    return static_cast<int32_t>(node.node_id);
                }
            }
            return std::unexpected("No healthy baseline nodes available");
        }

        const double bucket = static_cast<double>(user_hash % 10000) / 100.0;
        const bool select_canary = (bucket < current_weight_percent_);

        for (const auto& node : nodes_) {
            if (node.is_canary == select_canary && node.is_healthy && !node.is_draining) {
                return static_cast<int32_t>(node.node_id);
            }
        }

        return std::unexpected("No matching cluster node found for routing bucket");
    }

    void triggerEmergencyKillSwitch(std::string_view reason) {
        std::unique_lock lock(state_rwlock_);
        state_ = RolloutState::EmergencyKillSwitch;
        current_weight_percent_ = 0.0;
        ++active_epoch_token_;
        state_entered_time_ = std::chrono::steady_clock::now();

        for (auto& node : nodes_) {
            if (node.is_canary) {
                node.is_draining = true;
            }
        }

        std::cout << std::format("[KILL_SWITCH] Аварійне переривання! Причина: {}. Епоха: {}\n",
                                 reason, active_epoch_token_);
    }

    void tick() {
        std::unique_lock lock(state_rwlock_);
        const auto now = std::chrono::steady_clock::now();
        const auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(now - state_entered_time_).count();

        switch (state_) {
            case RolloutState::Idle:
                break;

            case RolloutState::Initializing:
                state_ = RolloutState::PromotingCohort;
                current_weight_percent_ = 1.0; // 1% когорта
                state_entered_time_ = now;
                baseline_buffer_.clear();
                canary_buffer_.clear();
                break;

            case RolloutState::PromotingCohort:
                state_ = RolloutState::Soaking;
                state_entered_time_ = now;
                break;

            case RolloutState::Soaking:
                if (elapsed >= 5) { // 5 сек вікно вистоювання
                    state_ = RolloutState::EvaluatingAca;
                    state_entered_time_ = now;
                }
                break;

            case RolloutState::EvaluatingAca: {
                const auto base_snap = baseline_buffer_.snapshot();
                const auto can_snap = canary_buffer_.snapshot();

                if (base_snap.size() >= 10 && can_snap.size() >= 10) {
                    const auto res = StatisticalEngine::evaluate(base_snap, can_snap);
                    if (res && res->is_significant_regression) {
                        lock.unlock();
                        triggerEmergencyKillSwitch("ACA statistical regression detected (p < 0.01)");
                        return;
                    }
                }

                if (current_weight_percent_ >= 50.0) {
                    current_weight_percent_ = 100.0;
                    state_ = RolloutState::PromotedFull;
                } else if (current_weight_percent_ >= 25.0) {
                    current_weight_percent_ = 50.0;
                    state_ = RolloutState::PromotingCohort;
                } else if (current_weight_percent_ >= 5.0) {
                    current_weight_percent_ = 25.0;
                    state_ = RolloutState::PromotingCohort;
                } else {
                    current_weight_percent_ = 5.0;
                    state_ = RolloutState::PromotingCohort;
                }

                state_entered_time_ = now;
                baseline_buffer_.clear();
                canary_buffer_.clear();
                break;
            }

            case RolloutState::EmergencyKillSwitch:
                state_ = RolloutState::QuarantineDraining;
                state_entered_time_ = now;
                break;

            case RolloutState::QuarantineDraining:
                if (elapsed >= 3) {
                    state_ = RolloutState::RolledBack;
                    state_entered_time_ = now;
                }
                break;

            case RolloutState::RolledBack:
            case RolloutState::PromotedFull:
                break;
        }
    }

    [[nodiscard]] RolloutState getState() const noexcept {
        std::shared_lock lock(state_rwlock_);
        return state_;
    }

    [[nodiscard]] uint64_t getActiveEpoch() const noexcept {
        std::shared_lock lock(state_rwlock_);
        return active_epoch_token_;
    }

private:
    RolloutState state_{RolloutState::Idle};
    double current_weight_percent_{0.0};
    uint64_t active_epoch_token_{1000};
    double critical_z_score_{-2.58};
    std::chrono::steady_clock::time_point state_entered_time_{};

    std::vector<ClusterNode> nodes_;
    TelemetryRingBuffer baseline_buffer_;
    TelemetryRingBuffer canary_buffer_;
    mutable std::shared_mutex state_rwlock_;
};

} // namespace mixed_fleet::controller
