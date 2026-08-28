#include <cstdint>
#include <cstddef>
#include <array>
#include <variant>
#include <optional>
#include <span>

/* --- 1. ТИПИ ПОДІЙ ТА ПОЛІМОРФНИЙ СТРУКТУРОВАНИЙ ПЕЙЛОАД --- */
enum class EventId : uint8_t {
    None = 0,
    Entry,
    Exit,
    Tick,
    StartMission,
    WaypointReached,
    ObstacleDetected,
    ObstacleCleared,
    GoalTimeout,
    BatteryLow,
    CriticalFault
};

struct Coords {
    int16_t x{0};
    int16_t y{0};
};

using EventPayload = std::variant<std::monostate, int32_t, float, Coords>;

struct Event {
    EventId id{EventId::None};
    uint32_t timestamp_ms{0};
    EventPayload payload{};
};

/* --- 2. КІЛЬЦЕВИЙ БУФЕР ПОДІЙ (ШАБЛОННИЙ І БЕЗПЕЧНИЙ) --- */
template <typename T, size_t Capacity>
class LockFreeRingQueue {
public:
    constexpr LockFreeRingQueue() = default;

    bool post(const T& item) noexcept {
        if (count_ >= Capacity) {
            dropped_++;
            return false;
        }
        buffer_[head_] = item;
        head_ = (head_ + 1) % Capacity;
        count_++;
        return true;
    }

    std::optional<T> pop() noexcept {
        if (count_ == 0) {
            return std::nullopt;
        }
        T item = buffer_[tail_];
        tail_ = (tail_ + 1) % Capacity;
        count_--;
        return item;
    }

    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] bool empty() const noexcept { return count_ == 0; }
    [[nodiscard]] uint32_t dropped() const noexcept { return dropped_; }

private:
    std::array<T, Capacity> buffer_{};
    volatile size_t head_{0};
    volatile size_t tail_{0};
    volatile size_t count_{0};
    uint32_t dropped_{0};
};

/* --- 3. ДИСЦИПЛІНА ІЄРАРХІЧНОГО АВТОМАТА СТАНІВ --- */
enum class HsmResult : uint8_t {
    Handled,
    Ignored,
    Super,
    Transition
};

class Hsm;
using StateHandler = HsmResult (*)(Hsm& context, const Event& event);

class Hsm {
public:
    explicit Hsm(StateHandler initial_state) noexcept
        : current_state_(initial_state), next_state_(nullptr) {}

    void transition_to(StateHandler target) noexcept {
        next_state_ = target;
    }

    void dispatch(const Event& event) noexcept {
        if (!current_state_) return;

        HsmResult res = current_state_(*this, event);
        if (res == HsmResult::Transition && next_state_ != nullptr) {
            Event exit_ev{EventId::Exit, event.timestamp_ms, {}};
            current_state_(*this, exit_ev);

            current_state_ = next_state_;
            next_state_ = nullptr;

            Event entry_ev{EventId::Entry, event.timestamp_ms, {}};
            current_state_(*this, entry_ev);
        }
    }

    [[nodiscard]] StateHandler current_state() const noexcept {
        return current_state_;
    }

private:
    StateHandler current_state_{nullptr};
    StateHandler next_state_{nullptr};
};

/* --- 4. ДЕКЛАРАТИВНІ ЦІЛІ ТА ДВИГУН МІСІЇ --- */
struct NavTarget { int16_t x; int16_t y; float speed_mps; };
struct HoldTarget { uint32_t duration_ms; };
struct SurveyTarget { uint8_t sensor_mask; };

using GoalParams = std::variant<std::monostate, NavTarget, HoldTarget, SurveyTarget>;

struct Goal {
    uint32_t timeout_ms{0};
    uint32_t start_time_ms{0};
    GoalParams params{};
};

template <size_t Capacity>
class GoalEngine {
public:
    bool push(const Goal& g) noexcept {
        return queue_.post(g);
    }

    std::optional<Goal> fetch_next() noexcept {
        active_goal_ = queue_.pop();
        return active_goal_;
    }

    void abort_all() noexcept {
        while (!queue_.empty()) {
            queue_.pop();
        }
        active_goal_.reset();
    }

    [[nodiscard]] bool has_active() const noexcept {
        return active_goal_.has_value();
    }

    [[nodiscard]] const std::optional<Goal>& active() const noexcept {
        return active_goal_;
    }

private:
    LockFreeRingQueue<Goal, Capacity> queue_{};
    std::optional<Goal> active_goal_{std::nullopt};
};
