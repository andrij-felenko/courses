#pragma once

#include <cstdint>
#include <string_view>

#include "fixed.hpp"
#include "raw_frame.hpp"

// Драйвер віддає мілі-одиниці SI, і кожна величина має СВІЙ тип: додати
// мрад/с до мм/с² компілятор не дасть, а магічні коефіцієнти лишаються
// тут, а не розповзаються по формулах регулятора.
namespace si {

template <class Tag>
class Milli {
public:
    static constexpr std::string_view unit = Tag::unit;

    explicit constexpr Milli(std::int32_t v = 0) noexcept : v_{v} {}

    [[nodiscard]] constexpr std::int32_t count() const noexcept { return v_; }

    [[nodiscard]] friend constexpr Milli operator+(Milli a, Milli b) noexcept {
        return Milli{fx::saturate(static_cast<std::int64_t>(a.v_) + b.v_)};
    }
    [[nodiscard]] friend constexpr Milli operator-(Milli a, Milli b) noexcept {
        return Milli{fx::saturate(static_cast<std::int64_t>(a.v_) - b.v_)};
    }
    [[nodiscard]] friend constexpr auto operator<=>(Milli, Milli) noexcept = default;

private:
    std::int32_t v_{0};
};

struct AccelTag {
    static constexpr std::string_view unit{"м/с^2"};
};
struct RateTag {
    static constexpr std::string_view unit{"рад/с"};
};
struct TempTag {
    static constexpr std::string_view unit{"°C"};
};
struct FluxTag {
    static constexpr std::string_view unit{"мкТл"};
};
struct VoltTag {
    static constexpr std::string_view unit{"В"};
};

using Acceleration = Milli<AccelTag>; // мм/с²
using AngularRate = Milli<RateTag>;   // мрад/с
using Temperature = Milli<TempTag>;   // м°C
using MagneticFlux = Milli<FluxTag>;  // нТл
using Voltage = Milli<VoltTag>;       // мВ

// 0.061 мг/LSB * 9.80665 = 0.59820565 мм/с² на розряд 16-бітного слова;
// після зсуву лівовирівняного кадру на чотири біти вага ×16.
inline constexpr fx::Q16 kAccelWeight16 = fx::Q16::from_real(0.59820565L);
inline constexpr fx::Q16 kAccelWeight12 = fx::Q16::from_real(9.5712904L);
// 8.75 мград/с * (pi/180) = 0.1527163 мрад/с на розряд.
inline constexpr fx::Q16 kGyroWeight = fx::Q16::from_real(0.1527163L);
// 1/6842 Гаус = 14.61561 нТл на розряд.
inline constexpr fx::Q16 kMagWeight = fx::Q16::from_real(14.61561L);

// Ударне перевантаження не повинне обертати знак: межі, а не загортання.
inline constexpr std::int32_t kAccelLimit = 157'000; // ±16 g у мм/с²
inline constexpr std::int32_t kGyroLimit = 40'000;   // ±2000 °/с у мрад/с

[[nodiscard]] constexpr std::int32_t clamp_to(std::int32_t v, std::int32_t limit) noexcept {
    return v > limit ? limit : (v < -limit ? -limit : v);
}

[[nodiscard]] constexpr Acceleration accel_from_lsb16(std::int16_t raw,
                                                      std::int16_t zero = 0) noexcept {
    const auto centred = static_cast<std::int32_t>(raw) - static_cast<std::int32_t>(zero);
    return Acceleration{clamp_to(fx::scale_raw(centred, kAccelWeight16), kAccelLimit)};
}

[[nodiscard]] constexpr Acceleration accel_from_lsb12(std::int16_t raw,
                                                      std::int16_t zero = 0) noexcept {
    const auto centred = static_cast<std::int32_t>(raw) - static_cast<std::int32_t>(zero);
    return Acceleration{clamp_to(fx::scale_raw(centred, kAccelWeight12), kAccelLimit)};
}

struct AccelVector {
    Acceleration x{};
    Acceleration y{};
    Acceleration z{};

    // Сума квадратів доходить до 7.4e10 — рахуємо у 64 бітах, корінь цілий.
    [[nodiscard]] constexpr Acceleration magnitude() const noexcept {
        const auto sq = [](Acceleration a) {
            const auto v = static_cast<std::int64_t>(a.count());
            return static_cast<std::uint64_t>(v * v);
        };
        return Acceleration{static_cast<std::int32_t>(fx::isqrt(sq(x) + sq(y) + sq(z)))};
    }
};

[[nodiscard]] constexpr AccelVector accel_from_frame(raw::Vec3Raw f,
                                                     raw::Vec3Raw zero = {}) noexcept {
    return AccelVector{accel_from_lsb12(f.x, zero.x), accel_from_lsb12(f.y, zero.y),
                       accel_from_lsb12(f.z, zero.z)};
}

[[nodiscard]] constexpr AngularRate gyro_from_lsb(std::int16_t raw,
                                                  std::int16_t zero = 0) noexcept {
    const auto centred = static_cast<std::int32_t>(raw) - static_cast<std::int32_t>(zero);
    return AngularRate{clamp_to(fx::scale_raw(centred, kGyroWeight), kGyroLimit)};
}

// 0.0078125 °C = 125/16 м°C — точний дріб, множення й зсув без Q-формату.
[[nodiscard]] constexpr Temperature tmp117(std::int16_t raw) noexcept {
    return Temperature{(static_cast<std::int32_t>(raw) * 125 + 8) >> 4};
}

// 0.0625 °C = 125/2 м°C; на вході вже розширений за знаком відлік.
[[nodiscard]] constexpr Temperature mcp9808(std::int16_t raw) noexcept {
    return Temperature{(static_cast<std::int32_t>(raw) * 125 + 1) >> 1};
}

[[nodiscard]] constexpr MagneticFlux mag_from_lsb(std::int16_t raw) noexcept {
    return MagneticFlux{fx::scale_raw(static_cast<std::int32_t>(raw), kMagWeight)};
}

// 4095 * 3300 = 13 513 500: у 16 бітах добуток гине, тому проміжок 32-бітний.
[[nodiscard]] constexpr Voltage adc12_to_voltage(std::uint16_t raw,
                                                 std::uint16_t vref_mv) noexcept {
    const std::uint32_t clamped = raw > 4095u ? 4095u : raw;
    return Voltage{static_cast<std::int32_t>((clamped * vref_mv + 2047u) / 4095u)};
}

} // namespace si
