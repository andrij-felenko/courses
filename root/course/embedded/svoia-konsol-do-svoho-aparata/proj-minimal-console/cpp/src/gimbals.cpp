#include "gimbals.hpp"

#include <algorithm>

namespace console {
namespace {

// Обрив або коротке замикання давача Холла: жива вісь ніколи не впирається
// в самі краї шкали АЦП.
constexpr std::uint16_t kRawFloor = 8;
constexpr std::uint16_t kRawCeil = 4087;
constexpr std::uint8_t kBadLimit = 50;

// Кубічна експонента цілими: out = x·(1−k) + k·x³ для x у межах ±1024.
// Проміжок (x²>>10) не перевищує 1024, тож 32 біти не переповнюються.
constexpr std::int32_t applyExpo(std::int32_t x, std::uint8_t percent) noexcept
{
    if (percent == 0) {
        return x;
    }
    const std::int32_t cube = (((x * x) >> 10) * x) >> 10;
    return (x * (100 - percent) + cube * percent) / 100;
}

}   // namespace

std::uint16_t Gimbals::processAxis(std::size_t channel, std::uint16_t raw) noexcept
{
    if (channel >= hal::kAxisCount) {
        return kAxisCenter;
    }
    const AxisConfig& cfg = config_[channel];

    if (raw <= kRawFloor || raw >= kRawCeil) {
        badSamples_[channel] = std::min<std::uint8_t>(badSamples_[channel] + 1, 255);
    } else if (badSamples_[channel] > 0) {
        --badSamples_[channel];
    }

    // IIR першого порядку: свіжий відлік із вагою alpha/256.
    std::int32_t& state = filtered_[channel];
    state += ((static_cast<std::int32_t>(raw) - state) * cfg.alpha) >> 8;

    const auto value = std::clamp(state, static_cast<std::int32_t>(cfg.min),
                                  static_cast<std::int32_t>(cfg.max));

    if (cfg.unipolar) {
        const std::int32_t span = cfg.max - cfg.min;
        return span > 0 ? static_cast<std::uint16_t>((value - cfg.min) * kAxisMax / span) : 0;
    }

    std::int32_t diff = value - cfg.center;
    if (std::abs(diff) < cfg.deadband) {
        return kAxisCenter;
    }
    // Зсуваємо на ширину мертвої зони, щоб на її краю не було стрибка каналу.
    diff += (diff > 0) ? -static_cast<std::int32_t>(cfg.deadband)
                       : static_cast<std::int32_t>(cfg.deadband);

    const std::int32_t span = (diff > 0) ? cfg.max - cfg.center - cfg.deadband
                                         : cfg.center - cfg.min - cfg.deadband;
    if (span <= 0) {
        return kAxisCenter;
    }

    const std::int32_t norm = std::clamp(diff * kAxisCenter / span,
                                         -static_cast<std::int32_t>(kAxisCenter),
                                         static_cast<std::int32_t>(kAxisCenter));
    const std::int32_t out = kAxisCenter + applyExpo(norm, cfg.expoPercent);
    return static_cast<std::uint16_t>(std::clamp<std::int32_t>(out, 0, kAxisMax));
}

std::array<std::uint16_t, hal::kAxisCount> Gimbals::process(
    std::span<const std::uint16_t, hal::kAxisCount> raw) noexcept
{
    std::array<std::uint16_t, hal::kAxisCount> scaled{};
    for (std::size_t i = 0; i < hal::kAxisCount; ++i) {
        scaled[i] = processAxis(i, raw[i]);
    }
    return scaled;
}

bool Gimbals::axisDead() const noexcept
{
    return std::ranges::any_of(badSamples_, [](std::uint8_t bad) { return bad > kBadLimit; });
}

Fault Gimbals::safety(std::span<const std::uint16_t, hal::kAxisCount> scaled,
                      std::uint16_t switches) const noexcept
{
    Fault faults = Fault::None;
    if (scaled[std::to_underlying(Axis::Throttle)] > kAxisMax * 5 / 100) {   // газ понад 5%
        faults |= Fault::ThrottleUp;
    }
    if (switches & hal::sw::Arm) {
        faults |= Fault::ArmEngaged;
    }
    if (axisDead()) {
        faults |= Fault::AxisDead;
    }
    return faults;
}

std::uint8_t Gimbals::auxUpdate(std::uint16_t switches) noexcept
{
    // Кнопки опитуються на 1 кГц, а підкручувати канал корисного навантаження
    // треба на 100 Гц — інакше палець не встигає зупинити його де треба.
    if (++auxDivider_ >= 10) {
        auxDivider_ = 0;
        if ((switches & hal::sw::PayUp) && aux_ < 255) {
            ++aux_;
        }
        if ((switches & hal::sw::PayDown) && aux_ > 0) {
            --aux_;
        }
    }
    return aux_;
}

}   // namespace console
