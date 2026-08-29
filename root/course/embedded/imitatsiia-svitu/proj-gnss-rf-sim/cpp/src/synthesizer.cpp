#include "synthesizer.hpp"

#include <algorithm>
#include <cmath>
#include <format>
#include <numbers>
#include <stdexcept>

namespace gnss {
namespace {

constexpr double kPi = std::numbers::pi;
// Опорний рівень: сигнал −130 дБм має одиничну амплітуду.
constexpr double kReferenceDbm = -130.0;

}  // namespace

void Channel::ensure_frame(const Ephemeris& eph, const NavContext& ctx, GpsTime t_tx)
{
    if (!frame_ || !frame_->bit_position(t_tx)) frame_.emplace(eph, ctx, t_tx);
}

void Channel::update(GpsTime t_tx, double pseudorange_m, double doppler_hz,
                     double power_dbm, double elevation, const Multipath& multipath) noexcept
{
    doppler_     = doppler_hz;
    pseudorange_ = pseudorange_m;
    elevation_   = elevation;
    power_dbm_   = power_dbm;
    amplitude_   = std::pow(10.0, (power_dbm - kReferenceDbm) / 20.0);

    // Доплер стискає й шкалу коду — інакше кореляційний пік поповз би.
    code_rate_ = kCaChipRateHz * (1.0 + doppler_hz / kL1Hz);

    code_phase_ = std::fmod(t_tx.tow() * kCaChipRateHz, static_cast<double>(kCaCodeLength));
    if (code_phase_ < 0.0) code_phase_ += static_cast<double>(kCaCodeLength);

    if (frame_) {
        if (const auto pos = frame_->bit_position(t_tx)) data_position_ = *pos;
    }

    // Фаза несучої — це затримка поширення, узята за модулем 2π.
    carrier_phase_ = -2.0 * kPi * std::fmod(kL1Hz * pseudorange_m / kSpeedOfLight, 1.0);

    if (multipath.gamma > 0.0 && elevation > 0.0) {
        multipath_      = true;
        mp_delay_chips_ = multipath.delay_s * kCaChipRateHz;
        mp_amplitude_   = amplitude_ * multipath.gamma * std::pow(10.0, multipath.xpol_db / 20.0);
        // Зайвий хід дає свій набіг фази, а дзеркало обертає поляризацію — плюс π.
        mp_phase_ = -2.0 * kPi * std::fmod(kL1Hz * multipath.delay_s, 1.0) + kPi;
    } else {
        multipath_ = false;
    }
}

std::int8_t Channel::chip_at(double phase_chips) const noexcept
{
    double p = std::fmod(phase_chips, static_cast<double>(kCaCodeLength));
    if (p < 0.0) p += static_cast<double>(kCaCodeLength);
    return code_[static_cast<std::size_t>(p)];
}

void Channel::accumulate(double& acc_i, double& acc_q) const noexcept
{
    if (!frame_) return;

    // BPSK: знак чипа й знак біта даних — решта в амплітуді та фазі.
    const double data = frame_->sign_at(data_position_);
    const double direct = amplitude_ * chip_at(code_phase_) * data;
    acc_i += direct * std::cos(carrier_phase_);
    acc_q += direct * std::sin(carrier_phase_);

    if (multipath_) {
        const double reflected = mp_amplitude_ * chip_at(code_phase_ - mp_delay_chips_) * data;
        const double phase = carrier_phase_ + mp_phase_;
        acc_i += reflected * std::cos(phase);
        acc_q += reflected * std::sin(phase);
    }
}

void Channel::advance(double dt) noexcept
{
    carrier_phase_ += 2.0 * kPi * doppler_ * dt;
    if (carrier_phase_ >  kPi) carrier_phase_ -= 2.0 * kPi;
    if (carrier_phase_ < -kPi) carrier_phase_ += 2.0 * kPi;

    code_phase_ += code_rate_ * dt;
    if (code_phase_ >= static_cast<double>(kCaCodeLength))
        code_phase_ -= static_cast<double>(kCaCodeLength);

    data_position_ += kNavBitRateHz * dt;
    if (data_position_ >= static_cast<double>(NavFrame::kBits))
        data_position_ -= static_cast<double>(NavFrame::kBits);
}

Channel& Synthesizer::acquire(int prn)
{
    if (const auto it = channels_.find(prn); it != channels_.end()) return it->second;

    const auto code = make_ca_code(prn);
    if (!code) throw std::invalid_argument{std::format("PRN {} не має коду C/A", prn)};

    return channels_.emplace(prn, Channel{prn, *code}).first->second;
}

void Synthesizer::invalidate_frames() noexcept
{
    for (auto& [prn, channel] : channels_) channel.drop_frame();
}

void Synthesizer::generate(std::span<std::int16_t> interleaved) noexcept
{
    const double dt = 1.0 / sample_rate_;

    for (std::size_t n = 0; n + 1 < interleaved.size(); n += 2) {
        double acc_i = 0.0, acc_q = 0.0;

        for (auto& [prn, channel] : channels_) {
            channel.accumulate(acc_i, acc_q);
            channel.advance(dt);
        }

        // Насичення ЦАП псує спектр гармоніками, тож рахуємо кожен випадок:
        // якщо лічильник росте — масштаб треба зменшувати.
        const auto quantize = [this](double v) {
            const double limited = std::clamp(v * scale_, -32768.0, 32767.0);
            if (limited != v * scale_) ++clipped_;
            return static_cast<std::int16_t>(std::lrint(limited));
        };

        interleaved[n]     = quantize(acc_i);
        interleaved[n + 1] = quantize(acc_q);
    }
}

}  // namespace gnss
