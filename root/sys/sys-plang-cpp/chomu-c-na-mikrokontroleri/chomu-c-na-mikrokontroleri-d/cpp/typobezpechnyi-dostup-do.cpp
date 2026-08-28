// Безпечний підхід C++: типізовані бітові поля через enum class та зміщення
enum class PinMode : uint32_t { Input = 0b00, Output = 0b01, Alt = 0b10, Analog = 0b11 };

template <size_t PinIndex>
struct PinField {
    static constexpr uint32_t shift = PinIndex * 2U;
    static constexpr uint32_t mask  = 0b11U << shift;

    static constexpr uint32_t encode(PinMode mode) noexcept {
        return static_cast<uint32_t>(mode) << shift;
    }
};
