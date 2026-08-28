#include <cstdint>
#include <array>
#include <string_view>
#include <span>
#include <optional>
#include <chrono>

using namespace std::chrono_literals;

enum class EscalationTrigger : uint8_t {
    None = 0,
    SceneAmbiguity,         // Висока ентропія softmax / близькі класи
    PathExhausted,          // Усі гілки costmap заблоковані
    BorderlineCritical,     // Критичний об'єкт у діапазоні [0.4..0.7]
    OddExcursion            // Порушення робочого домену (вітер, EKF)
};

enum class EscalationState : uint8_t {
    Autonomous = 0,
    EscalationRequested,
    AwaitingOperator,
    ApplyingOverride,
    FailsafeHold,
    FailsafeBacktrack,
    FailsafeSafeAbort
};

struct EscalationOption {
    uint8_t option_id{0};
    std::string_view description{};
    float estimated_cost_detour_m{0.0f};
    float risk_score{0.0f};
};

struct BreadcrumbPoint {
    float x{0.0f}, y{0.0f}, z{0.0f};
    float yaw{0.0f};
    std::chrono::milliseconds timestamp{0ms};
    int8_t rssi_dbm{0};
};

class BreadcrumbTrail {
public:
    static constexpr size_t Capacity = 64;

    void push(const BreadcrumbPoint& pt) noexcept {
        buffer_[head_] = pt;
        head_ = (head_ + 1) % Capacity;
        if (count_ < Capacity) {
            count_++;
        }
    }

    [[nodiscard]] std::optional<BreadcrumbPoint> pop_reverse() noexcept {
        if (count_ == 0) {
            return std::nullopt;
        }
        head_ = (head_ == 0) ? (Capacity - 1) : (head_ - 1);
        count_--;
        return buffer_[head_];
    }

    [[nodiscard]] size_t size() const noexcept { return count_; }
    void clear() noexcept { head_ = 0; count_ = 0; }

private:
    std::array<BreadcrumbPoint, Capacity> buffer_{};
    size_t head_{0};
    size_t count_{0};
};
