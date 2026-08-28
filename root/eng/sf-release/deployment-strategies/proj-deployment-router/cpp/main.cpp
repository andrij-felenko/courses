#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <chrono>
#include <random>
#include <cstdint>
#include <numeric>
#include <format>
#include <algorithm>

enum class CanaryState {
    Inactive,
    Active,
    RolledBack,
    Promoted
};

enum class RoutingTarget {
    Baseline,
    Canary
};

struct MetricSlot {
    std::chrono::steady_clock::time_point timestamp{};
    uint32_t total_requests{0};
    uint32_t error_requests{0};
};

class DeploymentRouter {
public:
    DeploymentRouter(std::string baseline_addr, std::string canary_addr,
                     uint32_t initial_weight_pct, double max_err_rate,
                     uint32_t min_samples)
        : baseline_addr_(std::move(baseline_addr)),
          canary_addr_(std::move(canary_addr)),
          canary_weight_pct_(std::min(initial_weight_pct, 100u)),
          max_allowed_error_rate_(max_err_rate),
          min_sample_size_(min_samples),
          state_(initial_weight_pct_ > 0 ? CanaryState::Active : CanaryState::Inactive),
          last_rotation_(std::chrono::steady_clock::now()),
          rng_(std::random_device{}()),
          dist_(0, 99) {
        slots_.fill(MetricSlot{last_rotation_, 0, 0});
    }

    [[nodiscard]] RoutingTarget select_target() {
        if (state_ != CanaryState::Active || canary_weight_pct_ == 0) {
            return RoutingTarget::Baseline;
        }
        return (static_cast<uint32_t>(dist_(rng_)) < canary_weight_pct_)
                   ? RoutingTarget::Canary
                   : RoutingTarget::Baseline;
    }

    void record_result(RoutingTarget target, bool is_error) {
        if (target != RoutingTarget::Canary || state_ != CanaryState::Active) {
            return;
        }

        const auto now = std::chrono::steady_clock::now();
        rotate_slots_if_needed(now);

        auto& current_slot = slots_[current_slot_idx_];
        current_slot.total_requests++;
        if (is_error) {
            current_slot.error_requests++;
        }

        evaluate_health(now);
    }

    void set_weight(uint32_t new_weight) {
        if (state_ == CanaryState::RolledBack) {
            std::cerr << "[ПОПЕРЕДЖЕННЯ] Неможливо змінити вагу: канарка у стані відкочування.\n";
            return;
        }
        canary_weight_pct_ = std::min(new_weight, 100u);
        state_ = (canary_weight_pct_ > 0) ? CanaryState::Active : CanaryState::Inactive;
        std::cout << std::format("[ІНФО] Встановлено нову вагу канарки: {}%\n", canary_weight_pct_);
    }

    void promote() noexcept {
        state_ = CanaryState::Promoted;
        canary_weight_pct_ = 100;
        std::cout << "[ІНФО] Канарку успішно підвищено до 100% основного трафіку.\n";
    }

    [[nodiscard]] CanaryState state() const noexcept { return state_; }
    [[nodiscard]] uint32_t canary_weight() const noexcept { return canary_weight_pct_; }
    [[nodiscard]] std::string_view baseline_address() const noexcept { return baseline_addr_; }
    [[nodiscard]] std::string_view canary_address() const noexcept { return canary_addr_; }

private:
    static constexpr size_t kSlotCount = 10;
    static constexpr auto kSlotDuration = std::chrono::seconds(1);
    static constexpr auto kWindowDuration = kSlotCount * kSlotDuration;

    void rotate_slots_if_needed(std::chrono::steady_clock::time_point now) {
        const auto elapsed = now - last_rotation_;
        if (elapsed >= kSlotDuration) {
            const auto steps = std::min(
                static_cast<size_t>(elapsed / kSlotDuration),
                kSlotCount
            );
            for (size_t i = 0; i < steps; ++i) {
                current_slot_idx_ = (current_slot_idx_ + 1) % kSlotCount;
                slots_[current_slot_idx_] = MetricSlot{now, 0, 0};
            }
            last_rotation_ = now;
        }
    }

    void evaluate_health(std::chrono::steady_clock::time_point now) {
        uint32_t window_total = 0;
        uint32_t window_errors = 0;

        for (const auto& slot : slots_) {
            if (now - slot.timestamp <= kWindowDuration) {
                window_total += slot.total_requests;
                window_errors += slot.error_requests;
            }
        }

        if (window_total >= min_sample_size_) {
            const double current_error_rate = static_cast<double>(window_errors) / window_total;
            if (current_error_rate > max_allowed_error_rate_) {
                trigger_rollback(current_error_rate, window_total);
            }
        }
    }

    void trigger_rollback(double err_rate, uint32_t sample_size) {
        state_ = CanaryState::RolledBack;
        canary_weight_pct_ = 0;
        std::cerr << std::format(
            "[АЛЕРТ] Аварійний відкіт канарки! Помилки: {:.2f}% (поріг {:.2f}%, вибірка {})\n",
            err_rate * 100.0, max_allowed_error_rate_ * 100.0, sample_size
        );
    }

    std::string baseline_addr_;
    std::string canary_addr_;
    uint32_t canary_weight_pct_;
    double max_allowed_error_rate_;
    uint32_t min_sample_size_;
    CanaryState state_;

    std::array<MetricSlot, kSlotCount> slots_{};
    size_t current_slot_idx_{0};
    std::chrono::steady_clock::time_point last_rotation_;

    std::mt19937 rng_;
    std::uniform_int_distribution<int> dist_;
};

int main() {
    DeploymentRouter router("10.0.0.1:8080", "10.0.0.2:8080", 20, 0.05, 50);

    std::cout << std::format("Ініціалізація: Baseline={}, Canary={} (Вага={}%)\n",
                             router.baseline_address(), router.canary_address(),
                             router.canary_weight());

    std::mt19937 gen(1337);
    std::uniform_int_distribution<int> error_dist(0, 99);

    for (int i = 1; i <= 200; ++i) {
        const auto target = router.select_target();
        bool is_error = false;

        if (target == RoutingTarget::Canary) {
            if (i > 30 && error_dist(gen) < 25) {
                is_error = true;
            }
            router.record_result(target, is_error);
        }

        if (router.state() == CanaryState::RolledBack) {
            std::cout << std::format("Запит #{}: Трафік на канарку повністю перекрито.\n", i);
            break;
        }
    }

    return 0;
}
