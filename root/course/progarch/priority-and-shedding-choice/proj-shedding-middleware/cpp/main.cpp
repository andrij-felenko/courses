#include <iostream>
#include <atomic>
#include <string_view>
#include <expected>
#include <chrono>

enum class RequestPriority : uint8_t {
    P0_Critical   = 0,
    P1_High       = 1,
    P2_Medium     = 2,
    P3_Low        = 3,
    P4_Background = 4
};

enum class BrownoutLevel : uint8_t {
    L0_Normal    = 0,
    L1_ShedP4    = 1,
    L2_ShedP3    = 2,
    L3_ShedP2    = 3,
    L4_Emergency = 4
};

struct SheddingError {
    int http_status{503};
    std::chrono::seconds retry_after{15};
    std::string_view reason;
    BrownoutLevel active_level;
};

// RAII контролер для обліку паралельності та автоматичного зниження тиску
class AdaptiveSheddingController {
public:
    explicit AdaptiveSheddingController(size_t max_capacity)
        : capacity_(max_capacity) {}

    // RAII обгортка: інкрементує активні запити при створенні, декрементує у деструкторі
    class RequestGuard {
    public:
        explicit RequestGuard(AdaptiveSheddingController& ctrl) : controller_(ctrl) {}
        ~RequestGuard() {
            if (active_) {
                controller_.release();
            }
        }

        RequestGuard(const RequestGuard&) = delete;
        RequestGuard& operator=(const RequestGuard&) = delete;

        RequestGuard(RequestGuard&& o) noexcept 
            : controller_(o.controller_), active_(o.active_) {
            o.active_ = false;
        }

        RequestGuard& operator=(RequestGuard&& o) noexcept {
            if (this != &o) {
                if (active_) controller_.release();
                active_ = o.active_;
                o.active_ = false;
            }
            return *this;
        }

    private:
        AdaptiveSheddingController& controller_;
        bool active_{true};
    };

    [[nodiscard]] std::expected<RequestGuard, SheddingError> try_admit(RequestPriority priority) {
        const auto level = update_and_get_level();

        if (should_drop(level, priority)) {
            const auto retry_sec = std::chrono::seconds(10 + static_cast<int>(priority) * 5);
            return std::unexpected(SheddingError{
                .http_status = 503,
                .retry_after = retry_sec,
                .reason = "Request shedded by adaptive load shedding controller",
                .active_level = level
            });
        }

        active_requests_.fetch_add(1, std::memory_order_relaxed);
        return RequestGuard(*this);
    }

    [[nodiscard]] size_t active_count() const noexcept {
        return active_requests_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] BrownoutLevel current_level() const noexcept {
        return current_level_.load(std::memory_order_relaxed);
    }

private:
    void release() noexcept {
        active_requests_.fetch_sub(1, std::memory_order_relaxed);
        update_and_get_level();
    }

    static bool should_drop(BrownoutLevel level, RequestPriority prio) noexcept {
        switch (level) {
            case BrownoutLevel::L4_Emergency: return prio > RequestPriority::P0_Critical;
            case BrownoutLevel::L3_ShedP2:    return prio >= RequestPriority::P2_Medium;
            case BrownoutLevel::L2_ShedP3:    return prio >= RequestPriority::P3_Low;
            case BrownoutLevel::L1_ShedP4:    return prio >= RequestPriority::P4_Background;
            case BrownoutLevel::L0_Normal:
            default:                          return false;
        }
    }

    BrownoutLevel update_and_get_level() noexcept {
        const size_t active = active_requests_.load(std::memory_order_relaxed);
        BrownoutLevel current = current_level_.load(std::memory_order_relaxed);
        BrownoutLevel next = current;

        // Пороги наростання тиску
        if (active >= 95) next = BrownoutLevel::L4_Emergency;
        else if (active >= 85) next = BrownoutLevel::L3_ShedP2;
        else if (active >= 70) next = BrownoutLevel::L2_ShedP3;
        else if (active >= 50) next = BrownoutLevel::L1_ShedP4;

        // Гістерезис при спаданні тиску
        else if (current == BrownoutLevel::L4_Emergency && active < 90) next = BrownoutLevel::L3_ShedP2;
        else if (current == BrownoutLevel::L3_ShedP2 && active < 80)    next = BrownoutLevel::L2_ShedP3;
        else if (current == BrownoutLevel::L2_ShedP3 && active < 65)    next = BrownoutLevel::L1_ShedP4;
        else if (current == BrownoutLevel::L1_ShedP4 && active < 45)    next = BrownoutLevel::L0_Normal;

        if (next != current) {
            current_level_.store(next, std::memory_order_relaxed);
        }
        return next;
    }

    size_t capacity_;
    std::atomic<size_t> active_requests_{0};
    std::atomic<BrownoutLevel> current_level_{BrownoutLevel::L0_Normal};
};

int main() {
    AdaptiveSheddingController controller(100);

    // Спроба обробити P4 під низьким навантаженням
    auto res1 = controller.try_admit(RequestPriority::P4_Background);
    if (res1) {
        std::cout << "P4 request admitted! Active requests: " << controller.active_count() << "\n";
    }

    // При виході res1 з області видимості деструктор RequestGuard автоматично декрементує активний лічильник
    std::cout << "After guard scope exit, active requests: " << controller.active_count() << "\n";

    return 0;
}
