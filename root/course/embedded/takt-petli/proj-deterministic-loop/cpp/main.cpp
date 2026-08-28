#include <cstdint>
#include <array>
#include <atomic>
#include <algorithm>
#include <span>

namespace control {

constexpr float kLoopFreqHz = 20000.0f;
constexpr float kLoopDtSec  = 1.0f / kLoopFreqHz;
constexpr size_t kQueueSize = 64;

struct TelemetryItem {
    float target{0.0f};
    float measured{0.0f};
    float output{0.0f};
    uint32_t timestamp_cnt{0};
};

template <typename T, size_t Size>
class SpscRingBuffer {
    static_assert((Size & (Size - 1)) == 0, "Розмір буфера мусить бути степенем двійки!");
public:
    constexpr SpscRingBuffer() noexcept : head_(0), tail_(0) {}

    bool push(const T& item) noexcept {
        const size_t current_head = head_.load(std::memory_order_relaxed);
        const size_t next_head = (current_head + 1) & (Size - 1);
        if (next_head == tail_.load(std::memory_order_acquire)) {
            return false; /* Буфер переповнений */
        }
        buffer_[current_head] = item;
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    bool pop(T& item) noexcept {
        const size_t current_tail = tail_.load(std::memory_order_relaxed);
        if (current_tail == head_.load(std::memory_order_acquire)) {
            return false; /* Черга порожня */
        }
        item = buffer_[current_tail];
        tail_.store((current_tail + 1) & (Size - 1), std::memory_order_release);
        return true;
    }

private:
    std::array<T, Size> buffer_{};
    std::atomic<size_t> head_{0};
    std::atomic<size_t> tail_{0};
};

class DeterministicPidController {
public:
    struct Config {
        float kp{1.0f};
        float ki{0.0f};
        float kd{0.0f};
        float filter_time_const{0.0005f};
        float out_min{0.0f};
        float out_max{1.0f};
    };

    explicit constexpr DeterministicPidController(const Config& cfg) noexcept
        : cfg_(cfg) {}

    void reset() noexcept {
        integrator_ = 0.0f;
        prev_meas_ = 0.0f;
        d_filtered_ = 0.0f;
    }

    [[nodiscard]] float update(float setpoint, float measured, float dt) noexcept {
        const float error = setpoint - measured;

        /* Пропорційна ланка */
        const float p_term = cfg_.kp * error;

        /* Диференційна ланка від виміру (Derivative on Measurement) */
        const float d_meas = (measured - prev_meas_) / dt;
        prev_meas_ = measured;

        const float alpha = dt / (cfg_.filter_time_const + dt);
        d_filtered_ += alpha * (d_meas - d_filtered_);
        const float d_term = -cfg_.kd * d_filtered_;

        const float unsaturated_output = p_term + integrator_ + d_term;
        const float output = std::clamp(unsaturated_output, cfg_.out_min, cfg_.out_max);

        /* Anti-windup clamping */
        const bool is_saturated = (unsaturated_output != output);
        const bool same_direction = ((error > 0.0f && unsaturated_output > cfg_.out_max) ||
                                     (error < 0.0f && unsaturated_output < cfg_.out_min));

        if (!is_saturated || !same_direction) {
            integrator_ += cfg_.ki * error * dt;
        }

        return output;
    }

private:
    Config cfg_;
    float integrator_{0.0f};
    float prev_meas_{0.0f};
    float d_filtered_{0.0f};
};

} // namespace control

/* Статичні екземпляри без динамічної пам'яті */
static control::DeterministicPidController g_current_controller({
    .kp = 0.45f,
    .ki = 120.0f,
    .kd = 0.0015f,
    .filter_time_const = 0.0002f,
    .out_min = 0.0f,
    .out_max = 0.98f
});

static control::SpscRingBuffer<control::TelemetryItem, control::kQueueSize> g_telem_queue;

extern "C" void ADC1_2_IRQHandler() {
    volatile auto* const tim1_ccr1 = reinterpret_cast<volatile uint32_t*>(0x40012C34);
    volatile auto* const tim1_arr  = reinterpret_cast<volatile uint32_t*>(0x40012C2C);
    volatile auto* const tim1_cnt  = reinterpret_cast<volatile uint32_t*>(0x40012C24);
    volatile auto* const adc1_sr   = reinterpret_cast<volatile uint32_t*>(0x40012000);
    volatile auto* const adc1_dr   = reinterpret_cast<volatile uint32_t*>(0x4001204C);

    *adc1_sr &= ~0x02; /* Очищення прапорця EOC */

    const uint16_t raw_adc = static_cast<uint16_t>(*adc1_dr & 0x0FFF);
    const float current_amps = (static_cast<float>(raw_adc) - 2048.0f) * (3.3f / 4096.0f) * 10.0f;
    constexpr float target_amps = 2.5f;

    const float duty = g_current_controller.update(target_amps, current_amps, control::kLoopDtSec);

    const uint32_t arr = *tim1_arr;
    *tim1_ccr1 = std::min(static_cast<uint32_t>(duty * static_cast<float>(arr)), arr);

    g_telem_queue.push({
        .target = target_amps,
        .measured = current_amps,
        .output = duty,
        .timestamp_cnt = *tim1_cnt
    });
}
