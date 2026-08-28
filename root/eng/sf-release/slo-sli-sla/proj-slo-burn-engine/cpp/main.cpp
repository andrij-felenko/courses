#include <iostream>
#include <vector>
#include <chrono>
#include <shared_mutex>
#include <memory>
#include <string_view>
#include <expected>
#include <span>
#include <cmath>

namespace slo {

using Clock = std::chrono::steady_clock;
using TimePoint = std::chrono::time_point<Clock>;
using Seconds = std::chrono::seconds;

// Статус вердикту шлюзу допуску
enum class GateVerdict {
    AllowDeployment,        // Бюджет у нормі, релізи дозволено
    ThrottleReleases,       // Помірне вигорання (Ticket level), уповільнити темп
    FreezeReleasesPageOncall // Критичне вигорання (Page level), негайне замороження
};

// Лічильники подій усередині одного часового кванта
struct EventBucket {
    uint64_t total_requests{0};
    uint64_t good_requests{0};
    uint64_t bad_requests{0};

    void reset() noexcept {
        total_requests = 0;
        good_requests = 0;
        bad_requests = 0;
    }
};

// Конфігурація цільового SLO
struct SloTarget {
    std::string_view name;
    double target_sli{0.999};              // 99.9%
    Seconds long_window{std::chrono::hours(1)};  // 1 година
    Seconds short_window{std::chrono::minutes(5)}; // 5 хвилин
    double critical_burn_rate{14.4};       // Поріг критики (2% бюджету за 1 год)
    double warning_burn_rate{6.0};         // Поріг застереження
};

// Рушій оцінки SLO на базі кільцевого буфера
class SloEvaluationEngine {
public:
    SloEvaluationEngine(SloTarget target, Seconds bucket_size)
        : target_(target), bucket_size_(bucket_size) {
        
        size_t total_buckets = static_cast<size_t>(target_.long_window.count() / bucket_size_.count()) + 1;
        buckets_.resize(total_buckets);
        short_window_buckets_count_ = static_cast<size_t>(target_.short_window.count() / bucket_size_.count());
        long_window_buckets_count_ = static_cast<size_t>(target_.long_window.count() / bucket_size_.count());
        
        last_bucket_time_ = std::chrono::duration_cast<Seconds>(Clock::now().time_since_epoch());
    }

    // Реєстрація окремої події (O(1) на гарячому шляху)
    void record_event(bool is_good, uint64_t count = 1) noexcept {
        std::unique_lock lock(mutex_);
        advance_buckets_if_needed(Clock::now());

        auto& current = buckets_[head_index_];
        current.total_requests += count;
        if (is_good) {
            current.good_requests += count;
        } else {
            current.bad_requests += count;
        }
    }

    // Отримання поточної швидкості вигорання для вікна заданої глибини
    [[nodiscard]] double calculate_burn_rate(size_t window_buckets) const noexcept {
        uint64_t total = 0;
        uint64_t bad = 0;

        size_t count = std::min(window_buckets, buckets_.size());
        for (size_t i = 0; i < count; ++i) {
            size_t idx = (head_index_ + buckets_.size() - i) % buckets_.size();
            total += buckets_[idx].total_requests;
            bad += buckets_[idx].bad_requests;
        }

        if (total == 0) {
            return 0.0; // Немає трафіку — немає вигорання
        }

        double actual_error_rate = static_cast<double>(bad) / static_cast<double>(total);
        double allowed_error_rate = 1.0 - target_.target_sli;

        if (allowed_error_rate <= 0.0) {
            return 0.0;
        }

        return actual_error_rate / allowed_error_rate;
    }

    // Оцінка стану шлюзу на базі алгоритму MWMBR (Multi-Window Multi-Burn-Rate)
    [[nodiscard]] GateVerdict evaluate_gate() const noexcept {
        std::shared_lock lock(mutex_);

        double short_burn = calculate_burn_rate(short_window_buckets_count_);
        double long_burn = calculate_burn_rate(long_window_buckets_count_);

        // Критичний рівень: одночасне перевищення 14.4x у короткому (5хв) та довгому (1год) вікнах
        if (short_burn >= target_.critical_burn_rate && long_burn >= target_.critical_burn_rate) {
            return GateVerdict::FreezeReleasesPageOncall;
        }

        // Рівень застереження: перевищення 6.0x
        if (short_burn >= target_.warning_burn_rate && long_burn >= target_.warning_burn_rate) {
            return GateVerdict::ThrottleReleases;
        }

        return GateVerdict::AllowDeployment;
    }

private:
    void advance_buckets_if_needed(TimePoint now) noexcept {
        auto current_time_sec = std::chrono::duration_cast<Seconds>(now.time_since_epoch());
        auto elapsed = current_time_sec - last_bucket_time_;
        
        if (elapsed < bucket_size_) {
            return;
        }

        size_t steps = static_cast<size_t>(elapsed.count() / bucket_size_.count());
        steps = std::min(steps, buckets_.size());

        for (size_t s = 0; s < steps; ++s) {
            head_index_ = (head_index_ + 1) % buckets_.size();
            buckets_[head_index_].reset();
        }

        last_bucket_time_ = current_time_sec;
    }

    SloTarget target_;
    Seconds bucket_size_;
    std::vector<EventBucket> buckets_;
    size_t head_index_{0};
    size_t short_window_buckets_count_{0};
    size_t long_window_buckets_count_{0};
    Seconds last_bucket_time_{0};
    mutable std::shared_mutex mutex_;
};

} // namespace slo

int main() {
    using namespace std::chrono_literals;

    slo::SloTarget api_slo{
        .name = "CheckoutAPI_Availability",
        .target_sli = 0.999, // 99.9%
        .long_window = 3600s, // 1 година
        .short_window = 300s, // 5 хвилин
        .critical_burn_rate = 14.4,
        .warning_burn_rate = 6.0
    };

    slo::SloEvaluationEngine engine(api_slo, 10s);

    // Імітація стабільного потоку трафіку (1000 успішних запитів, 1 помилка)
    for (int i = 0; i < 999; ++i) {
        engine.record_event(true);
    }
    engine.record_event(false);

    auto verdict1 = engine.evaluate_gate();
    std::cout << "Стан 1 (Стабільний трафік): " 
              << (verdict1 == slo::GateVerdict::AllowDeployment ? "ALLOW" : "BLOCKED") << "\n";

    // Імітація важкої аварії (100 помилок поспіль)
    for (int i = 0; i < 100; ++i) {
        engine.record_event(false);
    }

    auto verdict2 = engine.evaluate_gate();
    std::cout << "Стан 2 (Під час аварії): " 
              << (verdict2 == slo::GateVerdict::FreezeReleasesPageOncall ? "FREEZE_AND_PAGE" : "NORMAL") << "\n";

    return 0;
}
