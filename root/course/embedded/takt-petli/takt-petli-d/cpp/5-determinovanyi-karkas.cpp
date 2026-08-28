#include <cstdint>
#include <array>
#include <atomic>
#include <algorithm>
#include <span>

namespace embedded::control {

constexpr float kLoopFrequencyHz = 20000.0f;
constexpr float kLoopDtSeconds   = 1.0f / kLoopFrequencyHz;
constexpr size_t kQueueCapacity  = 64;

struct TelemetrySnapshot {
    float target{0.0f};
    float measured{0.0f};
    float duty_cycle{0.0f};
    uint32_t timestamp_ticks{0};
};

/* Lock-free Single-Producer Single-Consumer кільцевий буфер */
template <typename T, size_t Capacity>
class LockFreeSpscRing {
    static_assert((Capacity & (Capacity - 1)) == 0, "Місткість буфера має бути степенем двійки!");
public:
    constexpr LockFreeSpscRing() noexcept = default;

    bool try_push(const T& item) noexcept {
        const size_t head = head_.load(std::memory_order_relaxed);
        const size_t next_head = (head + 1) & (Capacity - 1);
        if (next_head == tail_.load(std::memory_order_acquire)) {
            return false; /* Буфер переповнений — викидаємо зразок, не блокуючи ISR */
        }
        storage_[head] = item;
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    bool try_pop(T& out_item) noexcept {
        const size_t tail = tail_.load(std::memory_order_relaxed);
        if (tail == head_.load(std::memory_order_acquire)) {
            return false; /* Черга порожня */
        }
        out_item = storage_[tail];
        tail_.store((tail + 1) & (Capacity - 1), std::memory_order_release);
        return true;
    }

private:
    std::array<T, Capacity> storage_{};
    std::atomic<size_t> head_{0};
    std::atomic<size_t> tail_{0};
};

/* Клас детермінованого ПІД-регулятора без динамічної пам'яті */
class DeterministicCurrentPid {
public:
    struct Parameters {
        float kp{1.2f};
        float ki{350.0f};
        float kd{0.0008f};
        float d_filter_time_const{0.0001f}; /* Постійна часу фільтра D-складової */
        float out_min{0.0f};
        float out_max{0.95f};               /* Захисний запас шпаруватості для заряджання бутстрепних ємностей */
    };

    explicit constexpr DeterministicCurrentPid(const Parameters& params) noexcept
        : p_(params) {}

    void reset() noexcept {
        integrator_ = 0.0f;
        prev_measured_ = 0.0f;
        d_filtered_ = 0.0f;
    }

    [[nodiscard]] float update(float target, float measured, float dt) noexcept {
        const float error = target - measured;

        /* Пропорційна дія */
        const float p_action = p_.kp * error;

        /* Диференційна дія за вимірюванням з інтегрованим ФНЧ першого порядку */
        const float d_raw = (measured - prev_measured_) / dt;
        prev_measured_ = measured;

        const float alpha = dt / (p_.d_filter_time_const + dt);
        d_filtered_ += alpha * (d_raw - d_filtered_);
        const float d_action = -p_.kd * d_filtered_;

        /* Сумарний ненасичений вплив */
        const float raw_output = p_action + integrator_ + d_action;
        const float saturated_output = std::clamp(raw_output, p_.out_min, p_.out_max);

        /* Умовне інтегрування (Anti-Windup Clamping) */
        const bool is_saturated = (raw_output != saturated_output);
        const bool error_worsens_saturation = ((error > 0.0f && raw_output > p_.out_max) ||
                                               (error < 0.0f && raw_output < p_.out_min));

        if (!is_saturated || !error_worsens_saturation) {
            integrator_ += p_.ki * error * dt;
        }

        return saturated_output;
    }

private:
    Parameters p_;
    float integrator_{0.0f};
    float prev_measured_{0.0f};
    float d_filtered_{0.0f};
};

} // namespace embedded::control

/* Статичні екземпляри об'єктів контуру */
static embedded::control::DeterministicCurrentPid g_current_loop({
    .kp = 0.85f,
    .ki = 420.0f,
    .kd = 0.0005f,
    .d_filter_time_const = 0.00008f,
    .out_min = 0.0f,
    .out_max = 0.95f
});

static embedded::control::LockFreeSpscRing<embedded::control::TelemetrySnapshot, embedded::control::kQueueCapacity> g_telemetry_buffer;

/* Вхідна точка апаратного переривання */
extern "C" void HardRealTime_ADC_ISR() {
    volatile auto* const tim1_ccr1 = reinterpret_cast<volatile uint32_t*>(0x40012C34);
    volatile auto* const tim1_arr  = reinterpret_cast<volatile uint32_t*>(0x40012C2C);
    volatile auto* const tim1_cnt  = reinterpret_cast<volatile uint32_t*>(0x40012C24);
    volatile auto* const adc1_sr   = reinterpret_cast<volatile uint32_t*>(0x40012000);
    volatile auto* const adc1_dr   = reinterpret_cast<volatile uint32_t*>(0x4001204C);

    *adc1_sr &= ~0x02; /* Очищення прапорця EOC */

    const uint16_t raw_code = static_cast<uint16_t>(*adc1_dr & 0x0FFF);
    const float measured_i = (static_cast<float>(raw_code) - 2048.0f) * (3.3f / 4096.0f) * 10.0f;
    constexpr float target_i = 3.0f;

    const float duty = g_current_loop.update(target_i, measured_i, embedded::control::kLoopDtSeconds);

    const uint32_t arr = *tim1_arr;
    *tim1_ccr1 = std::min(static_cast<uint32_t>(duty * static_cast<float>(arr)), arr);

    g_telemetry_buffer.try_push({
        .target = target_i,
        .measured = measured_i,
        .duty_cycle = duty,
        .timestamp_ticks = *tim1_cnt
    });
}
