#include <cstdint>
#include <array>
#include <vector>
#include <span>
#include <optional>
#include <algorithm>
#include <chrono>

namespace embedded::diagnostics {

inline constexpr size_t MaxNodes = 4;
inline constexpr size_t LogBufferSize = 64;

// Строго типізовані події
enum class EventType : uint8_t {
    None = 0,
    FlashEraseStart,
    FlashEraseDone,
    MotorStart,
    MotorOvercurrent,
    SupplyVoltageDrop,
    EmergencyShutdown
};

// Результат причинно-наслідкового порівняння
enum class Causality : uint8_t {
    Before,     // A причинно передувало B (A -> B)
    After,      // B причинно передувало A (B -> A)
    Concurrent  // Незалежні конкурентні події (A || B)
};

// Векторний логічний годинник
template <size_t N = MaxNodes>
class VectorClock {
public:
    constexpr VectorClock() noexcept { values_.fill(0); }

    constexpr void increment(size_t node_id) noexcept {
        if (node_id < N) {
            ++values_[node_id];
        }
    }

    constexpr void merge(const VectorClock<N>& other) noexcept {
        for (size_t i = 0; i < N; ++i) {
            values_[i] = std::max(values_[i], other.values_[i]);
        }
    }

    [[nodiscard]] constexpr uint32_t get(size_t node_id) const noexcept {
        return (node_id < N) ? values_[node_id] : 0;
    }

    [[nodiscard]] constexpr Causality compare(const VectorClock<N>& other) const noexcept {
        bool self_has_less = false;
        bool other_has_less = false;

        for (size_t i = 0; i < N; ++i) {
            if (values_[i] < other.values_[i]) {
                self_has_less = true;
            } else if (values_[i] > other.values_[i]) {
                other_has_less = true;
            }
        }

        if (self_has_less && !other_has_less) return Causality::Before;
        if (other_has_less && !self_has_less) return Causality::After;
        return Causality::Concurrent;
    }

    [[nodiscard]] constexpr const std::array<uint32_t, N>& raw() const noexcept {
        return values_;
    }

private:
    std::array<uint32_t, N> values_{};
};

// Запис журналу подій
template <size_t N = MaxNodes>
struct LogEntry {
    uint8_t                         node_id{0};
    std::chrono::microseconds       phys_time{0};
    VectorClock<N>                  vclock{};
    EventType                       type{EventType::None};
    int32_t                         payload{0};
};

// Керуючий клас вузла
template <size_t N = MaxNodes, size_t BufSize = LogBufferSize>
class DiagnosticNode {
public:
    explicit constexpr DiagnosticNode(uint8_t node_id) noexcept : node_id_(node_id) {}

    void log_event(std::chrono::microseconds now, EventType type, int32_t payload = 0) noexcept {
        clock_.increment(node_id_);

        LogEntry<N> entry{
            .node_id = node_id_,
            .phys_time = now,
            .vclock = clock_,
            .type = type,
            .payload = payload
        };

        if (entries_.size() >= BufSize) {
            entries_.erase(entries_.begin());
        }
        entries_.push_back(entry);
    }

    void receive_message_clock(const VectorClock<N>& msg_clock) noexcept {
        clock_.merge(msg_clock);
        clock_.increment(node_id_);
    }

    [[nodiscard]] const VectorClock<N>& current_clock() const noexcept { return clock_; }
    [[nodiscard]] std::span<const LogEntry<N>> entries() const noexcept { return entries_; }

private:
    uint8_t                   node_id_{0};
    VectorClock<N>            clock_{};
    std::vector<LogEntry<N>>  entries_{};
};

// Результат кореляційного аналізу живлення
struct CorrelationResult {
    bool                      is_correlated{false};
    std::chrono::microseconds latency{0};
    uint16_t                  min_voltage_mv{0};
};

// Крос-доменний аналізатор взаємозв'язку між програмою та аналоговою напругою
template <size_t N = MaxNodes>
[[nodiscard]] CorrelationResult analyze_power_drop(
    const LogEntry<N>& prog_event,
    std::span<const uint16_t> voltage_samples_mv,
    std::chrono::microseconds sample_start,
    std::chrono::microseconds sample_period,
    uint16_t threshold_drop_mv) noexcept
{
    if (voltage_samples_mv.empty()) return {};

    auto min_it = std::min_element(voltage_samples_mv.begin(), voltage_samples_mv.end());
    size_t min_idx = std::distance(voltage_samples_mv.begin(), min_it);
    uint16_t min_val = *min_it;

    auto drop_phys_time = sample_start + (sample_period * min_idx);
    auto latency = std::chrono::duration_cast<std::chrono::microseconds>(drop_phys_time - prog_event.phys_time);

    bool correlated = (latency >= std::chrono::microseconds{0}) &&
                      (latency <= std::chrono::microseconds{5000}) &&
                      (min_val <= threshold_drop_mv);

    return CorrelationResult{
        .is_correlated = correlated,
        .latency = latency,
        .min_voltage_mv = min_val
    };
}

} // namespace embedded::diagnostics
