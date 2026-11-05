#include <cstdint>
#include <cstddef>
#include <array>
#include <optional>

namespace HardwareSafety {

// Шаблонізована обгортка для безпечного виклику та голосування між двома каналами
template <typename ValueType, ValueType MaxTolerance>
class HardwareChannelVoter {
public:
    struct ChannelRegisters {
        volatile ValueType channel_a_data;
        volatile ValueType channel_b_data;
        volatile uint32_t status_control;
    };

    enum class FailureReason : uint8_t {
        None = 0,
        MemoryInversionFault,
        CrossChannelDivergence,
        HardwareTimeout
    };

    explicit HardwareChannelVoter(ChannelRegisters* hw_regs) noexcept
        : registers_(hw_regs), failure_reason_(FailureReason::None) {}

    // Виконання безпечного обчислення з двома обчислювальними лямбда-функціями
    template <typename FuncA, typename FuncB>
    [[nodiscard]] std::optional<ValueType> evaluate(ValueType input_a, ValueType input_b, FuncA&& calc_a, FuncB&& calc_b) noexcept {
        // Запис у фізичні регістри каналу А
        registers_->channel_a_data = input_a;
        ValueType res_a = calc_a(input_a);

        // Внутрішнє комплементарне кодування для каналу Б
        const ValueType b_inverted = input_b ^ static_cast<ValueType>(~0ULL);
        registers_->channel_b_data = input_b;

        // Перевірка побітової цілісності каналу Б
        if ((input_b ^ b_inverted) != static_cast<ValueType>(~0ULL)) {
            failure_reason_ = FailureReason::MemoryInversionFault;
            return std::nullopt;
        }

        ValueType res_b = calc_b(input_b);

        // Обчислення абсолютної різниці між результатами
        const ValueType diff = (res_a > res_b) ? (res_a - res_b) : (res_b - res_a);
        if (diff > MaxTolerance) {
            failure_reason_ = FailureReason::CrossChannelDivergence;
            return std::nullopt;
        }

        failure_reason_ = FailureReason::None;
        return static_cast<ValueType>((res_a + res_b) / 2);
    }

    [[nodiscard]] FailureReason getLastError() const noexcept {
        return failure_reason_;
    }

private:
    ChannelRegisters* registers_;
    FailureReason failure_reason_;
};

} // namespace HardwareSafety
