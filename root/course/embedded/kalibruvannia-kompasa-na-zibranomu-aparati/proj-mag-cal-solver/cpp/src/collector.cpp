// ===========================================================================
//  collector.cpp — просторове квотування хмари вимірів
//
//  Означення шаблона тримаємо тут і явно інстанціюємо єдину робочу
//  конфігурацію: у прошивці немає жодної причини компілювати другу, а
//  заголовок лишається коротким.
// ===========================================================================

#include "mag_cal/collector.hpp"

#include <algorithm>
#include <numbers>

namespace mag_cal {
namespace {

constexpr float kPi = std::numbers::pi_v<float>;
constexpr float kHalfPi = kPi / 2.0F;
constexpr float kTwoPi = 2.0F * kPi;

}  // namespace

template <std::size_t LatBins, std::size_t LonBins, std::size_t Quota>
void SphereCollector<LatBins, LonBins, Quota>::reset(float earth_field_ut,
                                                     std::uint32_t now_ms) noexcept {
    counts_.fill(0);
    size_ = 0;
    last_accept_ms_ = now_ms;
    rejections_ = {};
    // Поле поза межами земного діапазону — це помилка налаштування, а не
    // екзотична локація: беремо типове значення й працюємо далі.
    earth_field_ = (earth_field_ut > 10.0F && earth_field_ut < 100.0F)
                       ? earth_field_ut
                       : limits::kDefaultEarthUt;
}

template <std::size_t LatBins, std::size_t LonBins, std::size_t Quota>
std::optional<std::size_t> SphereCollector<LatBins, LonBins, Quota>::bin_of(
    const Vec3& raw) noexcept {
    const float norm = raw.norm();
    if (!(norm > 1e-3F)) {
        return std::nullopt;   // заразом ловить NaN
    }

    // Округлення float здатне вивести аргумент за межі області визначення
    const float sin_elev = std::clamp(raw.z / norm, -1.0F, 1.0F);
    const float elev = std::asin(sin_elev);          // кут місця, [-π/2, +π/2]
    const float azim = std::atan2(raw.y, raw.x);     // азимут,    [-π,   +π]

    const auto lat = static_cast<std::size_t>(std::clamp(
        static_cast<int>((elev + kHalfPi) / (kPi / static_cast<float>(LatBins))), 0,
        static_cast<int>(LatBins) - 1));
    const auto lon = static_cast<std::size_t>(std::clamp(
        static_cast<int>((azim + kPi) / (kTwoPi / static_cast<float>(LonBins))), 0,
        static_cast<int>(LonBins) - 1));

    return lat * LonBins + lon;
}

template <std::size_t LatBins, std::size_t LonBins, std::size_t Quota>
Vec3 SphereCollector<LatBins, LonBins, Quota>::bin_center(std::size_t bin) noexcept {
    const auto lat = bin / LonBins;
    const auto lon = bin % LonBins;

    const float elev = -kHalfPi + (static_cast<float>(lat) + 0.5F) *
                                      (kPi / static_cast<float>(LatBins));
    const float azim = -kPi + (static_cast<float>(lon) + 0.5F) *
                                  (kTwoPi / static_cast<float>(LonBins));

    const float ce = std::cos(elev);
    return {ce * std::cos(azim), ce * std::sin(azim), std::sin(elev)};
}

template <std::size_t LatBins, std::size_t LonBins, std::size_t Quota>
PushResult SphereCollector<LatBins, LonBins, Quota>::push(
    const Vec3& raw, const Vec3& gyro_rad_s, std::uint32_t now_ms) noexcept {
    // Різкий рух: цифровий фільтр магнітометра відстає, і вимір лягає не в
    // те положення, у якому апарат був насправді.
    if (gyro_rad_s.norm() > limits::kGyroLimitRadS) {
        ++rejections_.too_fast;
        return PushResult::TooFast;
    }

    const auto bin = bin_of(raw);
    if (!bin) {
        ++rejections_.invalid;
        return PushResult::Invalid;
    }

    auto& count = counts_[*bin];
    if (count >= Quota) {
        ++rejections_.bin_full;   // квота вибрана — це норма, а не помилка
        return PushResult::BinFull;
    }

    samples_[size_] = raw;
    ++size_;
    ++count;
    last_accept_ms_ = now_ms;
    return PushResult::Accepted;
}

template <std::size_t LatBins, std::size_t LonBins, std::size_t Quota>
std::size_t SphereCollector<LatBins, LonBins, Quota>::filled_bins() const noexcept {
    return static_cast<std::size_t>(
        std::ranges::count_if(counts_, [](std::uint8_t c) { return c > 0; }));
}

template <std::size_t LatBins, std::size_t LonBins, std::size_t Quota>
float SphereCollector<LatBins, LonBins, Quota>::coverage_percent() const noexcept {
    return static_cast<float>(filled_bins()) / static_cast<float>(kBins) * 100.0F;
}

template <std::size_t LatBins, std::size_t LonBins, std::size_t Quota>
std::uint8_t SphereCollector<LatBins, LonBins, Quota>::completion_percent()
    const noexcept {
    // Рахуємо по вибраній квоті, а не по «хоч одна точка»: інакше шкала
    // стрибнула б до ста, коли роботи ще на пів процедури.
    const float ratio = static_cast<float>(size_) / static_cast<float>(kCapacity);
    return static_cast<std::uint8_t>(std::clamp(ratio * 100.0F + 0.5F, 0.0F, 100.0F));
}

template <std::size_t LatBins, std::size_t LonBins, std::size_t Quota>
auto SphereCollector<LatBins, LonBins, Quota>::completion_mask() const noexcept
    -> std::array<std::uint8_t, kMaskBytes> {
    std::array<std::uint8_t, kMaskBytes> mask{};
    for (std::size_t i = 0; i < kBins; ++i) {
        // Зеленим наземна станція має малювати лише те, що більше чіпати
        // не треба, тобто повністю вибрані сектори.
        if (counts_[i] >= Quota) {
            mask[i / 8] |= static_cast<std::uint8_t>(1U << (i % 8));
        }
    }
    return mask;
}

template <std::size_t LatBins, std::size_t LonBins, std::size_t Quota>
Vec3 SphereCollector<LatBins, LonBins, Quota>::hint_direction() const noexcept {
    const auto worst = std::ranges::min_element(counts_);
    if (worst == counts_.end() || *worst >= Quota) {
        return {0.0F, 0.0F, 1.0F};   // хмара повна
    }
    return bin_center(static_cast<std::size_t>(std::distance(counts_.begin(), worst)));
}

template class SphereCollector<6, 12, 4>;

}  // namespace mag_cal
