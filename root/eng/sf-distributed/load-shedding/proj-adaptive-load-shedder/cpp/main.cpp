#include <iostream>
#include <chrono>
#include <atomic>
#include <optional>
#include <cstdint>
#include <string_view>
#include <algorithm>

// Рівні пріоритетності операцій
enum class RequestTier : uint8_t {
    Tier0_System = 0,     // Health-checks, Raft heartbeats, distributed locks
    Tier1_Critical = 1,   // Платежі, оформлення замовлення, аутентифікація
    Tier2_Interactive = 2,// Пошук товарів, каталог, навігація
    Tier3_Background = 3  // Аналітика, фонові задачі, аудит
};

// Результат перевірки допуску
enum class AdmissionStatus : uint8_t {
    Admitted,
    DroppedDeadlineExpired,
    DroppedQueueDelayHigh,
    DroppedPriorityShed,
    DroppedCapacityExhausted
};

// Контекст вхідного виклику
struct RequestContext {
    uint64_t request_id;
    RequestTier tier;
    std::chrono::steady_clock::time_point entry_time;
    std::chrono::steady_clock::time_point deadline;
    std::chrono::nanoseconds min_execution_time;
};

// Адаптивний шеддер на базі CoDel та пріоритетних кошиків
class LoadShedder {
public:
    struct Config {
        std::chrono::nanoseconds target_sojourn_time{std::chrono::milliseconds(20)};
        std::chrono::nanoseconds codel_interval{std::chrono::milliseconds(100)};
        uint32_t max_capacity{1000};
        uint32_t min_capacity{50};
    };

    explicit LoadShedder(Config cfg)
        : config_(cfg),
          inflight_requests_(0),
          dynamic_capacity_limit_(cfg.max_capacity),
          interval_start_ns_(get_now_ns()),
          min_sojourn_in_interval_ns_(UINT64_MAX),
          in_dropping_state_(false),
          drop_count_(0) {}

    // RAII-обгортка для автоматичного звільнення слота після завершення
    class AdmissionGuard {
    public:
        AdmissionGuard(LoadShedder& shedder, bool admitted, AdmissionStatus status)
            : shedder_(&shedder), admitted_(admitted), status_(status) {}

        ~AdmissionGuard() {
            if (admitted_ && shedder_) {
                shedder_->release();
            }
        }

        AdmissionGuard(const AdmissionGuard&) = delete;
        AdmissionGuard& operator=(const AdmissionGuard&) = delete;

        AdmissionGuard(AdmissionGuard&& other) noexcept
            : shedder_(other.shedder_), admitted_(other.admitted_), status_(other.status_) {
            other.shedder_ = nullptr;
            other.admitted_ = false;
        }

        [[nodiscard]] bool is_admitted() const noexcept { return admitted_; }
        [[nodiscard]] AdmissionStatus status() const noexcept { return status_; }

    private:
        LoadShedder* shedder_;
        bool admitted_;
        AdmissionStatus status_;
    };

    // Головний метод перевірки допуску
    [[nodiscard]] AdmissionGuard try_admit(const RequestContext& req) noexcept {
        const auto now = std::chrono::steady_clock::now();
        const auto now_ns = static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::nanoseconds>(now.time_since_epoch()).count()
        );

        // Рубіж 1: Перевірка залишкового дедлайну
        if (req.deadline < now + req.min_execution_time) {
            return AdmissionGuard(*this, false, AdmissionStatus::DroppedDeadlineExpired);
        }

        // Рубіж 2: Вимірювання часу перебування (Sojourn Time)
        const auto sojourn_time = now - req.entry_time;
        const auto sojourn_ns = static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::nanoseconds>(sojourn_time).count()
        );

        update_codel_state(now_ns, sojourn_ns);

        // Рубіж 3: Скидання за станом черги CoDel та пріоритетом
        const bool dropping = in_dropping_state_.load(std::memory_order_relaxed);
        if (dropping) {
            if (req.tier == RequestTier::Tier3_Background) {
                return AdmissionGuard(*this, false, AdmissionStatus::DroppedPriorityShed);
            }
            if (req.tier == RequestTier::Tier2_Interactive && (sojourn_time > config_.target_sojourn_time)) {
                return AdmissionGuard(*this, false, AdmissionStatus::DroppedQueueDelayHigh);
            }
        }

        // Рубіж 4: Перевірка ліміту активної конкурентності (Inflight limit)
        const uint32_t current_limit = dynamic_capacity_limit_.load(std::memory_order_relaxed);
        uint32_t current_inflight = inflight_requests_.load(std::memory_order_relaxed);

        while (current_inflight < current_limit) {
            if (inflight_requests_.compare_exchange_weak(
                    current_inflight, current_inflight + 1,
                    std::memory_order_acquire, std::memory_order_relaxed)) {
                return AdmissionGuard(*this, true, AdmissionStatus::Admitted);
            }
        }

        // Якщо місця немає, але запит критичний (Tier 0) — допускаємо понад ліміт з резерву
        if (req.tier == RequestTier::Tier0_System) {
            inflight_requests_.fetch_add(1, std::memory_order_acquire);
            return AdmissionGuard(*this, true, AdmissionStatus::Admitted);
        }

        return AdmissionGuard(*this, false, AdmissionStatus::DroppedCapacityExhausted);
    }

private:
    void release() noexcept {
        inflight_requests_.fetch_sub(1, std::memory_order_release);
    }

    static uint64_t get_now_ns() noexcept {
        return static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::nanoseconds>(
                std::chrono::steady_clock::now().time_since_epoch()
            ).count()
        );
    }

    void update_codel_state(uint64_t now_ns, uint64_t sojourn_ns) noexcept {
        uint64_t current_min = min_sojourn_in_interval_ns_.load(std::memory_order_relaxed);
        while (sojourn_ns < current_min) {
            if (min_sojourn_in_interval_ns_.compare_exchange_weak(
                    current_min, sojourn_ns,
                    std::memory_order_relaxed, std::memory_order_relaxed)) {
                break;
            }
        }

        const uint64_t interval_start = interval_start_ns_.load(std::memory_order_relaxed);
        const uint64_t target_ns = static_cast<uint64_t>(config_.target_sojourn_time.count());
        const uint64_t interval_dur_ns = static_cast<uint64_t>(config_.codel_interval.count());

        if (now_ns - interval_start > interval_dur_ns) {
            const uint64_t min_sojourn = min_sojourn_in_interval_ns_.exchange(sojourn_ns, std::memory_order_relaxed);
            interval_start_ns_.store(now_ns, std::memory_order_relaxed);

            if (min_sojourn > target_ns) {
                in_dropping_state_.store(true, std::memory_order_relaxed);
                drop_count_.fetch_add(1, std::memory_order_relaxed);

                // Мультиплікативне зменшення ліміту ємності
                uint32_t current_cap = dynamic_capacity_limit_.load(std::memory_order_relaxed);
                uint32_t new_cap = std::max(config_.min_capacity, static_cast<uint32_t>(current_cap * 0.85));
                dynamic_capacity_limit_.store(new_cap, std::memory_order_relaxed);
            } else {
                in_dropping_state_.store(false, std::memory_order_relaxed);
                // Адитивне відновлення ліміту ємності
                uint32_t current_cap = dynamic_capacity_limit_.load(std::memory_order_relaxed);
                uint32_t new_cap = std::min(config_.max_capacity, current_cap + 10);
                dynamic_capacity_limit_.store(new_cap, std::memory_order_relaxed);
            }
        }
    }

    const Config config_;

    alignas(64) std::atomic<uint32_t> inflight_requests_;
    alignas(64) std::atomic<uint32_t> dynamic_capacity_limit_;
    alignas(64) std::atomic<uint64_t> interval_start_ns_;
    alignas(64) std::atomic<uint64_t> min_sojourn_in_interval_ns_;
    alignas(64) std::atomic<bool> in_dropping_state_;
    alignas(64) std::atomic<uint64_t> drop_count_;
};
