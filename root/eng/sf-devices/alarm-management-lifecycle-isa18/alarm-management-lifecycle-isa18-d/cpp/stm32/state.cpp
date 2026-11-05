#include <cstdint>
#include <cstddef>
#include <atomic>
#include <array>

namespace EmbeddedAlarms {

enum class State : uint8_t {
    Normal = 0,
    Unacknowledged,
    Acknowledged,
    ReturnToNormalUnack,
    Suppressed,
    OutOfService
};

struct Event {
    uint32_t channel_id;
    State new_state;
    uint64_t timestamp_us;
    float raw_value;
};

template <size_t Capacity>
class LockFreeEventQueue {
public:
    LockFreeEventQueue() : head_(0), tail_(0) {}

    bool push_from_isr(const Event& event) noexcept {
        size_t current_head = head_.load(std::memory_order_relaxed);
        size_t next_head = (current_head + 1) % Capacity;
        if (next_head == tail_.load(std::memory_order_acquire)) {
            return false; /* Переповнення буфера */
        }
        buffer_[current_head] = event;
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    bool pop(Event& event) noexcept {
        size_t current_tail = tail_.load(std::memory_order_relaxed);
        if (current_tail == head_.load(std::memory_order_acquire)) {
            return false; /* Буфер порожній */
        }
        event = buffer_[current_tail];
        tail_.store((current_tail + 1) % Capacity, std::memory_order_release);
        return true;
    }

private:
    std::array<Event, Capacity> buffer_{};
    std::atomic<size_t> head_;
    std::atomic<size_t> tail_;
};

template <size_t ChannelCount, size_t QueueCapacity>
class AlarmManager {
public:
    struct ChannelConfig {
        float threshold_high{0.0f};
        float deadband{0.0f};
        uint16_t on_delay_samples{0};
        uint16_t off_delay_samples{0};
        uint16_t on_counter{0};
        uint16_t off_counter{0};
        State state{State::Normal};
        bool active{false};
    };

    constexpr AlarmManager() = default;

    void configure_channel(size_t id, float threshold, float deadband, uint16_t on_delay, uint16_t off_delay) noexcept {
        if (id < ChannelCount) {
            channels_[id].threshold_high = threshold;
            channels_[id].deadband = deadband;
            channels_[id].on_delay_samples = on_delay;
            channels_[id].off_delay_samples = off_delay;
        }
    }

    void process_adc_sample_isr(size_t channel_id, float sample_val, uint64_t timestamp_us) noexcept {
        if (channel_id >= ChannelCount) return;
        auto& ch = channels_[channel_id];
        if (ch.state == State::OutOfService || ch.state == State::Suppressed) return;

        bool exceeded = (sample_val >= ch.threshold_high);
        bool cleared = (sample_val < (ch.threshold_high - ch.deadband));

        if (exceeded) {
            ch.off_counter = 0;
            if (ch.on_counter < ch.on_delay_samples) ch.on_counter++;
        } else if (cleared) {
            ch.on_counter = 0;
            if (ch.off_counter < ch.off_delay_samples) ch.off_counter++;
        }

        if (ch.on_counter >= ch.on_delay_samples && !ch.active) {
            ch.active = true;
            active_bitmask_.fetch_or(1U << channel_id, std::memory_order_relaxed);
            queue_.push_from_isr({static_cast<uint32_t>(channel_id), State::Unacknowledged, timestamp_us, sample_val});
        } else if (ch.off_counter >= ch.off_delay_samples && ch.active) {
            ch.active = false;
            active_bitmask_.fetch_and(~(1U << channel_id), std::memory_order_relaxed);
            State next_st = (ch.state == State::Acknowledged) ? State::Normal : State::ReturnToNormalUnack;
            queue_.push_from_isr({static_cast<uint32_t>(channel_id), next_st, timestamp_us, sample_val});
        }
    }

    void process_events_task() noexcept {
        Event evt;
        while (queue_.pop(evt)) {
            if (evt.channel_id < ChannelCount) {
                channels_[evt.channel_id].state = evt.new_state;
            }
        }
    }

    [[nodiscard]] uint32_t get_active_bitmask() const noexcept {
        return active_bitmask_.load(std::memory_order_relaxed);
    }

private:
    std::array<ChannelConfig, ChannelCount> channels_{};
    std::atomic<uint32_t> active_bitmask_{0};
    LockFreeEventQueue<QueueCapacity> queue_{};
};

} /* namespace EmbeddedAlarms */
