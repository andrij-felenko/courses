#include "rc_link.hpp"

#include <algorithm>

namespace fc {
namespace {

// Порядок каналів AETR — так їх кладе більшість апаратур.
constexpr std::size_t kRoll = 0, kPitch = 1, kThrottle = 2, kYaw = 3, kModeCh = 4;

constexpr float norm_sym(std::uint16_t us) noexcept {
    return std::clamp((static_cast<float>(us) - 1500.0f) / 500.0f, -1.0f, 1.0f);
}

constexpr float norm_uni(std::uint16_t us) noexcept {
    return std::clamp((static_cast<float>(us) - 1000.0f) / 1000.0f, 0.0f, 1.0f);
}

constexpr FlightMode mode_from_us(std::uint16_t us) noexcept {
    if (us < 1300) return FlightMode::Auto;
    if (us < 1700) return FlightMode::PosHold;
    return FlightMode::Manual;
}

} // namespace

std::uint16_t RcLink::crsf_ticks_to_us(std::uint16_t ticks) noexcept {
    const float us = std::clamp(0.62477120195241f * static_cast<float>(ticks) + 881.0f,
                                static_cast<float>(kMinUs), static_cast<float>(kMaxUs));
    return static_cast<std::uint16_t>(us + 0.5f);
}

bool RcLink::push(std::span<const std::uint16_t> pwm_us, Seconds now) noexcept {
    if (pwm_us.size() < kChannels) return false;

    // Побитий кадр не має права зрушити ані стіки, ані таймер зв'язку.
    const bool bad = std::any_of(pwm_us.begin(), pwm_us.begin() + kChannels,
                                 [](std::uint16_t us) { return us < kMinUs || us > kMaxUs; });
    if (bad) return false;

    std::copy_n(pwm_us.begin(), kChannels, last_.begin());
    last_frame_ = now;
    have_frame_ = true;

    // Антибрязкіт тумблера: нова позиція мусить протриматися kDebounceFrames
    // кадрів поспіль, інакше джитер радіоканалу зриватиме місію.
    const FlightMode raw = mode_from_us(last_[kModeCh]);
    if (raw == mode_) {
        candidate_ = raw;
        candidate_count_ = 0;
    } else if (raw == candidate_) {
        if (++candidate_count_ >= kDebounceFrames) {
            mode_ = raw;
            candidate_count_ = 0;
        }
    } else {
        candidate_ = raw;
        candidate_count_ = 1;
    }
    return true;
}

std::optional<RcCommand> RcLink::poll(Seconds now) const noexcept {
    if (!have_frame_) return std::nullopt;
    if (now - last_frame_ > kTimeout) {
        // Кадри зникли. Повертати останні прийняті значення не можна:
        // заморожений стік — найгірше, що тут можна зробити.
        return std::nullopt;
    }

    return RcCommand{norm_sym(last_[kRoll]), norm_sym(last_[kPitch]),
                     norm_sym(last_[kYaw]), norm_uni(last_[kThrottle]), mode_};
}

} // namespace fc
