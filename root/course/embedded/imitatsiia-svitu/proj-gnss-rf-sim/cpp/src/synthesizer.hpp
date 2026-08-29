// synthesizer.hpp — канал сузір'я і сума каналів у квадратурні вибірки для SDR.
#pragma once

#include <cstdint>
#include <map>
#include <optional>
#include <span>

#include "ca_code.hpp"
#include "ephemeris.hpp"
#include "geometry.hpp"
#include "nav_frame.hpp"

namespace gnss {

class Channel {
public:
    Channel(int prn, CaCode code) noexcept : prn_{prn}, code_{code} {}

    // Кадр живе 30 с; щойно час вийшов за його межі — будуємо наступний.
    void ensure_frame(const Ephemeris& eph, const NavContext& ctx, GpsTime t_tx);

    // Прив'язка до нової геометрії: фаза коду й несучої задається часом
    // випромінювання, тож псевдовідстань відтворюється буквально.
    void update(GpsTime t_tx, double pseudorange_m, double doppler_hz,
                double power_dbm, double elevation, const Multipath& multipath) noexcept;

    void accumulate(double& acc_i, double& acc_q) const noexcept;
    void advance(double dt) noexcept;

    [[nodiscard]] bool   ready()     const noexcept { return frame_.has_value(); }
    [[nodiscard]] int    prn()       const noexcept { return prn_; }
    [[nodiscard]] double power_dbm() const noexcept { return power_dbm_; }
    [[nodiscard]] double elevation() const noexcept { return elevation_; }
    void drop_frame() noexcept { frame_.reset(); }

private:
    [[nodiscard]] std::int8_t chip_at(double phase_chips) const noexcept;

    int    prn_{};
    CaCode code_{};
    std::optional<NavFrame> frame_;

    double code_phase_{}, code_rate_{kCaChipRateHz};
    double carrier_phase_{}, doppler_{};
    double data_position_{};
    double amplitude_{};

    bool   multipath_{false};
    double mp_delay_chips_{}, mp_amplitude_{}, mp_phase_{};

    double pseudorange_{}, elevation_{}, power_dbm_{};
};

class Synthesizer {
public:
    Synthesizer(double sample_rate, double dac_scale) noexcept
        : sample_rate_{sample_rate}, scale_{dac_scale} {}

    // std::map тримає вузли на місці, тож посилання переживає і додавання,
    // і зникнення сусідніх каналів.
    [[nodiscard]] Channel& acquire(int prn);
    void release(int prn) noexcept { channels_.erase(prn); }
    void invalidate_frames() noexcept;

    void generate(std::span<std::int16_t> interleaved) noexcept;

    [[nodiscard]] std::size_t   size()    const noexcept { return channels_.size(); }
    [[nodiscard]] std::uint64_t clipped() const noexcept { return clipped_; }
    [[nodiscard]] const std::map<int, Channel>& channels() const noexcept { return channels_; }

private:
    std::map<int, Channel> channels_;
    double sample_rate_{};
    double scale_{};
    std::uint64_t clipped_{};
};

}  // namespace gnss
