#include <cstdint>
#include <array>
#include <numbers>
#include <cmath>

/* Універсальний C++ клас для генерації та швидкої інтерполяції 
   періодичних таблиць замін довільного розміру N */
template <size_t TableBits = 8>
class SineLookupTable {
public:
    static constexpr size_t Size = 1ULL << TableBits;
    static constexpr size_t Mask = Size - 1;

    consteval SineLookupTable() : table_{} {
        constexpr double step = 2.0 * std::numbers::pi / static_cast<double>(Size);
        for (size_t i = 0; i < Size; ++i) {
            double val = std::sin(static_cast<double>(i) * step) * 32767.0;
            table_[i] = static_cast<int16_t>(std::round(val));
        }
    }

    [[nodiscard]] constexpr int16_t operator()(uint16_t angle) const noexcept {
        constexpr uint32_t shift = 16 - TableBits;
        const size_t idx0 = (angle >> shift) & Mask;
        const size_t idx1 = (idx0 + 1) & Mask;
        const auto frac = static_cast<int32_t>(angle & ((1U << shift) - 1));

        const int32_t y0 = table_[idx0];
        const int32_t y1 = table_[idx1];
        const int32_t delta = y1 - y0;

        return static_cast<int16_t>(y0 + ((delta * frac) >> shift));
    }

private:
    std::array<int16_t, Size> table_;
};

inline constexpr SineLookupTable<8> FastSin;
