#include <cstdint>
#include <concepts>

namespace math {

// Типобезпечний клас чисел із фіксованою комою формату Q_m.n
template <int FractionalBits = 16>
class FixedPoint {
public:
    static constexpr int FracBits = FractionalBits;
    static constexpr int64_t Scale = 1LL << FracBits;
    static constexpr int64_t HalfLsb = 1LL << (FracBits - 1);

    constexpr FixedPoint() noexcept = default;

    // Конструктор із цілого числа
    explicit constexpr FixedPoint(int32_t integer_val) noexcept 
        : raw_val_(static_cast<int32_t>(integer_val << FracBits)) {}

    // Фабричний метод для сирого значення
    [[nodiscard]] static constexpr FixedPoint from_raw(int32_t raw) noexcept {
        FixedPoint fp;
        fp.raw_val_ = raw;
        return fp;
    }

    [[nodiscard]] constexpr int32_t raw() const noexcept { return raw_val_; }

    [[nodiscard]] constexpr int32_t to_int() const noexcept {
        return (raw_val_ + static_cast<int32_t>(HalfLsb)) >> FracBits;
    }

    // Перевантаження арифметичних операторів
    [[nodiscard]] constexpr FixedPoint operator+(const FixedPoint& other) const noexcept {
        return from_raw(raw_val_ + other.raw_val_);
    }

    [[nodiscard]] constexpr FixedPoint operator-(const FixedPoint& other) const noexcept {
        return from_raw(raw_val_ - other.raw_val_);
    }

    [[nodiscard]] constexpr FixedPoint operator*(const FixedPoint& other) const noexcept {
        const int64_t prod = static_cast<int64_t>(raw_val_) * other.raw_val_;
        return from_raw(static_cast<int32_t>((prod + HalfLsb) >> FracBits));
    }

    [[nodiscard]] constexpr FixedPoint operator/(const FixedPoint& other) const noexcept {
        if (other.raw_val_ == 0) {
            return from_raw(0);
        }
        const int64_t num = (static_cast<int64_t>(raw_val_) << FracBits);
        return from_raw(static_cast<int32_t>(num / other.raw_val_));
    }

private:
    int32_t raw_val_{0};
};

using Q16 = FixedPoint<16>;

} // namespace math
