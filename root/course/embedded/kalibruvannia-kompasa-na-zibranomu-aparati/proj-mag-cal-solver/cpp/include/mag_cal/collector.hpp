// ===========================================================================
//  mag_cal/collector.hpp — накопичувач із просторовим квотуванням сфери.
//
//  Виміри лежать одним пласким масивом, а квоту стереже лічильник на комірку:
//  розв'язувачу потрібна хмара точок, а не її розкладка по секторах, і
//  std::span на суцільну пам'ять дешевший за прохід двовимірним масивом.
// ===========================================================================
#pragma once

#include <array>
#include <cstdint>
#include <optional>
#include <span>

#include "mag_cal/calibration.hpp"
#include "mag_cal/geometry.hpp"

namespace mag_cal {

enum class PushResult : std::uint8_t {
    Accepted,     // вимір ліг у комірку
    TooFast,      // |ω| > 100 °/с — динамічне спотворення
    BinFull,      // квота сектора вибрана
    Invalid       // нульовий модуль або NaN
};

template <std::size_t LatBins = 6, std::size_t LonBins = 12, std::size_t Quota = 4>
class SphereCollector;

// Робоча конфігурація конвеєра: 6 поясів × 12 секторів × 4 виміри = 288 точок
using Collector = SphereCollector<>;

template <std::size_t LatBins, std::size_t LonBins, std::size_t Quota>
class SphereCollector {
public:
    static constexpr std::size_t kBins = LatBins * LonBins;
    static constexpr std::size_t kCapacity = kBins * Quota;
    static constexpr std::size_t kMaskBytes = 10;   // поле MAVLink uint8_t[10]

    struct Rejections {
        std::uint32_t too_fast{0};
        std::uint32_t bin_full{0};
        std::uint32_t invalid{0};
    };

    explicit SphereCollector(float earth_field_ut = limits::kDefaultEarthUt) noexcept {
        reset(earth_field_ut, 0);
    }

    // now_ms — мітка старту процедури: відлік тайм-ауту бездіяльності
    // починається зі скидання, а не з першої прийнятої точки.
    void reset(float earth_field_ut, std::uint32_t now_ms) noexcept;

    // Швидкий шлях сенсорного потоку: жодних ділень на нуль і блокувань
    PushResult push(const Vec3& raw, const Vec3& gyro_rad_s,
                    std::uint32_t now_ms) noexcept;

    [[nodiscard]] std::span<const Vec3> samples() const noexcept {
        return {samples_.data(), size_};
    }
    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] float earth_field() const noexcept { return earth_field_; }
    [[nodiscard]] std::uint32_t last_accept_ms() const noexcept { return last_accept_ms_; }
    [[nodiscard]] const Rejections& rejections() const noexcept { return rejections_; }

    [[nodiscard]] std::size_t filled_bins() const noexcept;
    [[nodiscard]] float coverage_percent() const noexcept;

    // Частка вибраної квоти — саме її бачить оператор як відсоток готовності
    [[nodiscard]] std::uint8_t completion_percent() const noexcept;

    // Біт на сектор у порядку поля completion_mask MAVLink
    [[nodiscard]] std::array<std::uint8_t, kMaskBytes> completion_mask() const noexcept;

    // Одиничний вектор у центр найбіднішої комірки — підказка «доверни сюди»
    [[nodiscard]] Vec3 hint_direction() const noexcept;

    // Індекс комірки; порожньо — вимір непридатний
    [[nodiscard]] static std::optional<std::size_t> bin_of(const Vec3& raw) noexcept;
    [[nodiscard]] static Vec3 bin_center(std::size_t bin) noexcept;

private:
    std::array<Vec3, kCapacity> samples_{};
    std::array<std::uint8_t, kBins> counts_{};
    std::size_t size_{0};
    float earth_field_{limits::kDefaultEarthUt};
    std::uint32_t last_accept_ms_{0};
    Rejections rejections_{};
};

extern template class SphereCollector<6, 12, 4>;

}  // namespace mag_cal
