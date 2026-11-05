#include <cstdint>
#include <array>
#include <atomic>

template <size_t Capacity = 16>
class DdaMotionController {
public:
    struct MotionBlock {
        std::uint32_t step_count{0};
        std::uint32_t phase_inc_start{0};
        std::int32_t  phase_accel{0};
        std::uint32_t dir_mask{0};
        std::uint32_t follower_ratio{0};
    };

    bool pushBlock(const MotionBlock& block) noexcept {
        const size_t current_tail = tail_.load(std::memory_order_relaxed);
        const size_t next_tail = (current_tail + 1) % Capacity;

        if (next_tail == head_.load(std::memory_order_acquire)) {
            return false; // Кільцевий буфер переповнений
        }

        buffer_[current_tail] = block;
        tail_.store(next_tail, std::memory_order_release);
        return true;
    }

    void onTimerInterrupt() noexcept {
        const size_t current_head = head_.load(std::memory_order_relaxed);
        const size_t current_tail = tail_.load(std::memory_order_acquire);

        if (current_head == current_tail && current_step_ == 0) {
            return; // Черга порожня, рух відсутній
        }

        const auto& active_block = buffer_[current_head];

        if (current_step_ == 0 && current_phase_inc_ == 0) {
            current_phase_inc_ = active_block.phase_inc_start;
        }

        const std::uint32_t prev_accum = dda_accumulator_lead_;
        dda_accumulator_lead_ += current_phase_inc_;
        current_phase_inc_ += active_block.phase_accel;

        if (dda_accumulator_lead_ < prev_accum) { // Переповнення цілочисельного акумулятора
            current_step_++;
            dda_accumulator_follow_ += active_block.follower_ratio;

            if (current_step_ >= active_block.step_count) {
                current_step_ = 0;
                current_phase_inc_ = 0;
                dda_accumulator_lead_ = 0;
                dda_accumulator_follow_ = 0;
                head_.store((current_head + 1) % Capacity, std::memory_order_release);
            }
        }
    }

private:
    std::array<MotionBlock, Capacity> buffer_{};
    std::atomic<size_t> head_{0};
    std::atomic<size_t> tail_{0};

    std::uint32_t dda_accumulator_lead_{0};
    std::uint32_t dda_accumulator_follow_{0};
    std::uint32_t current_step_{0};
    std::uint32_t current_phase_inc_{0};
};
