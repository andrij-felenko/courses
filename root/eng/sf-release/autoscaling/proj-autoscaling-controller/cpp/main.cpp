#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <chrono>
#include <cmath>
#include <iomanip>
#include <algorithm>

namespace ops {

using namespace std::chrono_literals;

struct AutoscalerConfig {
    int min_replicas{2};
    int max_replicas{10};
    double target_metric{70.0};              // Цільовий CPU % або RPS
    double tolerance{0.10};                  // Deadband ±10% [63% .. 77%]
    double ema_alpha{0.40};                  // Вага свіжого значення в EMA
    std::chrono::seconds scale_up_cooldown{15s};
    std::chrono::seconds scale_down_window{60s};
    int max_scale_down_step{2};
};

struct AutoscalerDecision {
    int new_replicas;
    bool action_taken;
    std::string reason;
};

class AutoscalerController {
public:
    explicit AutoscalerController(AutoscalerConfig config, int initial_replicas = 2)
        : config_(config), current_replicas_(initial_replicas) {}

    AutoscalerDecision evaluate(double raw_metric, std::chrono::steady_clock::time_point now) {
        // 1. Оновлення експоненційного середнього
        if (!ema_initialized_) {
            smoothed_metric_ = raw_metric;
            ema_initialized_ = true;
        } else {
            smoothed_metric_ = config_.ema_alpha * raw_metric + (1.0 - config_.ema_alpha) * smoothed_metric_;
        }

        // 2. Перевірка зони нечутливості (Deadband)
        const double ratio = smoothed_metric_ / config_.target_metric;
        const double deviation = std::abs(ratio - 1.0);

        if (deviation <= config_.tolerance) {
            scale_down_candidate_time_.reset();
            return {current_replicas_, false, "Метрика всередині зони нечутливості (deadband)"};
        }

        // 3. Розрахунок бажаної кількості з округленням угору
        int desired = static_cast<int>(std::ceil(current_replicas_ * ratio));
        desired = std::clamp(desired, config_.min_replicas, config_.max_replicas);

        // 4. Гілка збільшення (Scale-up)
        if (desired > current_replicas_) {
            scale_down_candidate_time_.reset();

            if (last_scale_up_time_ && (now - *last_scale_up_time_ < config_.scale_up_cooldown)) {
                return {current_replicas_, false, "Scale-up заблоковано таймером охолодження (cooldown)"};
            }

            current_replicas_ = desired;
            last_scale_up_time_ = now;
            return {current_replicas_, true, "Виконано Scale-up (збільшення навантаження)"};
        }

        // 5. Гілка зменшення (Scale-down)
        if (desired < current_replicas_) {
            if (!scale_down_candidate_time_) {
                scale_down_candidate_time_ = now;
                return {current_replicas_, false, "Фіксація спаду метрики: запущено вікно стабілізації"};
            }

            if (now - *scale_down_candidate_time_ < config_.scale_down_window) {
                return {current_replicas_, false, "Очікування стабілізації перед Scale-down"};
            }

            const int allowed_drop = current_replicas_ - desired;
            if (allowed_drop > config_.max_scale_down_step) {
                desired = current_replicas_ - config_.max_scale_down_step;
            }

            current_replicas_ = desired;
            scale_down_candidate_time_ = now;
            return {current_replicas_, true, "Виконано безпечний Scale-down після стабілізації"};
        }

        return {current_replicas_, false, "Стан стабільний (у межах норми)"};
    }

    [[nodiscard]] double smoothed_metric() const noexcept { return smoothed_metric_; }
    [[nodiscard]] int current_replicas() const noexcept { return current_replicas_; }

private:
    AutoscalerConfig config_;
    int current_replicas_;
    double smoothed_metric_{0.0};
    bool ema_initialized_{false};
    std::optional<std::chrono::steady_clock::time_point> last_scale_up_time_;
    std::optional<std::chrono::steady_clock::time_point> scale_down_candidate_time_;
};

} // namespace ops

int main() {
    ops::AutoscalerConfig config{
        .min_replicas = 2,
        .max_replicas = 10,
        .target_metric = 70.0,
        .tolerance = 0.10,
        .ema_alpha = 0.40,
        .scale_up_cooldown = 15s,
        .scale_down_window = 60s,
        .max_scale_down_step = 2
    };

    ops::AutoscalerController controller(config, 2);

    const std::vector<double> load_profile{
        68.0, 72.0, 95.0, 110.0, 85.0, 75.0, 40.0, 35.0, 30.0, 32.0, 30.0, 30.0
    };

    std::cout << "=== Симуляція роботи контролера автоскейлу (C++) ===\n";
    std::cout << std::left << std::setw(6) << "Час"
              << " | " << std::setw(9) << "Сирий CPU"
              << " | " << std::setw(9) << "EMA CPU"
              << " | " << std::setw(8) << "Репліки"
              << " | " << "Рішення\n";
    std::cout << std::string(88, '-') << "\n";

    auto virtual_now = std::chrono::steady_clock::now();
    const auto start_time = virtual_now;

    for (double raw : load_profile) {
        auto decision = controller.evaluate(raw, virtual_now);
        auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(virtual_now - start_time).count();

        std::cout << std::right << std::setw(4) << elapsed << "s  | "
                  << std::setw(7) << std::fixed << std::setprecision(1) << raw << "% | "
                  << std::setw(7) << controller.smoothed_metric() << "% | "
                  << std::setw(8) << controller.current_replicas() << " | "
                  << decision.reason << "\n";

        virtual_now += 15s;
    }

    return 0;
}
