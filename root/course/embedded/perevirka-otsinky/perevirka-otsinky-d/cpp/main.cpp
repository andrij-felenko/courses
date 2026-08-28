#include <cstdint>
#include <array>
#include <optional>
#include <span>

/* Упакований двійковий пакет телеметрії */
struct alignas(4) TelemetryFrame {
    std::uint32_t timestamp_us;   // Системний час (мкс)
    float gyro_z;                  // Сира швидкість обертання (рад/с)
    float accel_x;                 // Сире прискорення X (м/с²)
    float accel_y;                 // Сире прискорення Y (м/с²)
    float state_yaw;               // Оцінка кута курсу (рад)
    float state_bias;              // Оцінений дрейф нуля гіроскопа
    float cov_p_yaw;               // Коваріація похибки оцінки стану P
    float innov_yaw;               // Нев'язка виміру інновації y
    float innov_cov_s;             // Коваріація інновації S
    float ground_truth_yaw;        // Еталонний кут Ground Truth
};

template <std::size_t Capacity>
class LogRingBuffer {
public:
    constexpr LogRingBuffer() = default;

    [[nodiscard]] bool push(const TelemetryFrame& frame) noexcept {
        const auto next_head = (head_ + 1) % Capacity;
        if (next_head == tail_) {
            return false; // Буфер переповнений
        }
        buffer_[head_] = frame;
        head_ = next_head;
        return true;
    }

    std::size_t pop_batch(std::span<TelemetryFrame> destination) noexcept {
        std::size_t extracted = 0;
        while (tail_ != head_ && extracted < destination.size()) {
            destination[extracted++] = buffer_[tail_];
            tail_ = (tail_ + 1) % Capacity;
        }
        return extracted;
    }

    [[nodiscard]] bool empty() const noexcept { return head_ == tail_; }
    [[nodiscard]] std::size_t size() const noexcept {
        if (head_ >= tail_) return head_ - tail_;
        return Capacity - (tail_ - head_);
    }

private:
    std::array<TelemetryFrame, Capacity> buffer_{};
    volatile std::size_t head_{0};
    volatile std::size_t tail_{0};
};
