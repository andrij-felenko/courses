#include <cstdint>
#include <array>
#include <atomic>

template <size_t BufferSize, size_t AxesCount>
class DdaMotionController {
public:
    struct Segment {
        uint32_t steps_major;
        std::array<uint32_t, AxesCount - 1> steps_minor;
        uint8_t dominant_axis_idx;
        uint8_t dir_mask;
        uint32_t initial_period_ticks;
        int32_t period_change_fp16;
    };

    DdaMotionController() : head_(0), tail_(0), is_busy_(false) {}

    bool pushSegment(const Segment& seg) {
        size_t head = head_.load(std::memory_order_relaxed);
        size_t next_head = (head + 1) % BufferSize;
        size_t tail = tail_.load(std::memory_order_acquire);

        if (next_head == tail) {
            return false;
        }

        buffer_[head] = seg;
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    void handleTimerInterrupt() {
        if (!is_busy_) {
            size_t head = head_.load(std::memory_order_acquire);
            size_t tail = tail_.load(std::memory_order_relaxed);

            if (head == tail) {
                return;
            }

            active_segment_ = buffer_[tail];
            current_step_ = 0;
            period_accumulator_fp16_ = active_segment_.initial_period_ticks << 16;

            for (size_t i = 0; i < AxesCount - 1; ++i) {
                dda_accumulators_[i] = active_segment_.steps_major / 2;
            }

            tail_.store((tail + 1) % BufferSize, std::memory_order_release);
            is_busy_ = true;
            // applyDirectionPins(active_segment_.dir_mask);
        }

        uint8_t step_mask = (1 << active_segment_.dominant_axis_idx);

        for (size_t i = 0; i < AxesCount - 1; ++i) {
            dda_accumulators_[i] += active_segment_.steps_minor[i];
            if (dda_accumulators_[i] >= active_segment_.steps_major) {
                dda_accumulators_[i] -= active_segment_.steps_major;
                step_mask |= (1 << ((active_segment_.dominant_axis_idx + 1 + i) % AxesCount));
            }
        }

        // triggerStepPins(step_mask);

        period_accumulator_fp16_ += active_segment_.period_change_fp16;
        uint32_t next_period = period_accumulator_fp16_ >> 16;
        // setHardwareTimerPeriod(next_period);

        current_step_++;
        if (current_step_ >= active_segment_.steps_major) {
            is_busy_ = false;
        }
    }

private:
    std::array<Segment, BufferSize> buffer_;
    std::atomic<size_t> head_;
    std::atomic<size_t> tail_;

    Segment active_segment_;
    uint32_t current_step_{0};
    std::array<uint32_t, AxesCount - 1> dda_accumulators_{};
    uint32_t period_accumulator_fp16_{0};
    bool is_busy_{false};
};
