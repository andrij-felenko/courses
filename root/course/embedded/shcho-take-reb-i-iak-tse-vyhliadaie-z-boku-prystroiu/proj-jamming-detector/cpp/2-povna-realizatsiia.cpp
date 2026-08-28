#include <cstdint>
#include <array>
#include <span>
#include <optional>
#include <numeric>
#include <algorithm>

namespace embedded::ew {

enum class ThreatType : uint8_t {
    None = 0,
    WeakSignal,
    SpotJamming,
    BarrageBlocking,
    PulseJamming,
    GnssSpoofing
};

struct RfSample {
    int16_t rssi_dbm{0};
    int8_t  snr_db{0};
    uint8_t agc_gain_code{255};
    bool    preamble_detected{false};
    bool    crc_error{false};
};

struct GnssSatInfo {
    uint8_t  prn{0};
    uint16_t cnr_x10{0};     // CNR in dB-Hz * 10 (450 = 45.0 dB-Hz)
    int16_t  doppler_hz{0};
    uint8_t  elevation_deg{0};
};

struct GnssFrame {
    std::span<const GnssSatInfo> satellites;
    bool clock_jump_detected{false};
    bool position_jump_without_imu{false};
};

template <std::size_t WindowSize = 16>
class ThreatClassifier {
public:
    static constexpr int16_t  kRssiJamThresholdDbm{-65};
    static constexpr int16_t  kRssiBarrageThresholdDbm{-40};
    static constexpr uint32_t kRssiPulseVarianceMin{120};
    static constexpr uint8_t   kPerJamThresholdPct{75};
    static constexpr uint16_t  kGnssSpoofCnrThreshold{510}; // 51.0 dB-Hz
    static constexpr uint16_t  kGnssSpoofMaxDev{25};       // 2.5 dB-Hz

    constexpr ThreatClassifier() noexcept = default;

    void pushSample(const RfSample& sample) noexcept {
        m_history[m_head] = sample;
        m_head = (m_head + 1) % WindowSize;
        if (m_count < WindowSize) {
            ++m_count;
        }
    }

    [[nodiscard]] ThreatType evaluate(const std::optional<GnssFrame>& gnss = std::nullopt) noexcept {
        if (gnss.has_value() && isGnssSpoofed(*gnss)) {
            m_current_threat = ThreatType::GnssSpoofing;
            return m_current_threat;
        }

        if (m_count == 0) {
            m_current_threat = ThreatType::None;
            return m_current_threat;
        }

        const auto stats = computeRfStats();

        if (stats.avg_rssi >= kRssiBarrageThresholdDbm && stats.avg_agc <= 30 && stats.sync_hits == 0) {
            m_current_threat = ThreatType::BarrageBlocking;
        } else if (stats.avg_rssi >= kRssiJamThresholdDbm && stats.per >= kPerJamThresholdPct && stats.sync_hits <= 1) {
            m_current_threat = ThreatType::SpotJamming;
        } else if (stats.rssi_variance >= kRssiPulseVarianceMin && stats.per >= 40) {
            m_current_threat = ThreatType::PulseJamming;
        } else if (stats.avg_rssi <= -105 && stats.per >= kPerJamThresholdPct) {
            m_current_threat = ThreatType::WeakSignal;
        } else {
            m_current_threat = ThreatType::None;
        }

        return m_current_threat;
    }

    [[nodiscard]] ThreatType currentThreat() const noexcept {
        return m_current_threat;
    }

private:
    struct RfStats {
        int16_t  avg_rssi{0};
        uint8_t  avg_agc{0};
        uint8_t  per{0};
        uint8_t  sync_hits{0};
        uint32_t rssi_variance{0};
    };

    [[nodiscard]] RfStats computeRfStats() const noexcept {
        int32_t rssi_acc = 0;
        uint32_t agc_acc = 0;
        uint8_t crc_errors = 0;
        uint8_t sync_count = 0;

        for (std::size_t i = 0; i < m_count; ++i) {
            rssi_acc += m_history[i].rssi_dbm;
            agc_acc += m_history[i].agc_gain_code;
            if (m_history[i].crc_error) ++crc_errors;
            if (m_history[i].preamble_detected) ++sync_count;
        }

        const auto avg_rssi = static_cast<int16_t>(rssi_acc / static_cast<int32_t>(m_count));
        const auto avg_agc = static_cast<uint8_t>(agc_acc / m_count);
        const auto per = static_cast<uint8_t>((crc_errors * 100) / m_count);

        uint32_t var_acc = 0;
        for (std::size_t i = 0; i < m_count; ++i) {
            const int32_t diff = m_history[i].rssi_dbm - avg_rssi;
            var_acc += static_cast<uint32_t>(diff * diff);
        }

        return RfStats{
            .avg_rssi = avg_rssi,
            .avg_agc = avg_agc,
            .per = per,
            .sync_hits = sync_count,
            .rssi_variance = var_acc / m_count
        };
    }

    [[nodiscard]] static bool isGnssSpoofed(const GnssFrame& gnss) noexcept {
        if (gnss.satellites.size() < 4) return false;
        if (gnss.position_jump_without_imu || gnss.clock_jump_detected) return true;

        uint32_t cnr_sum = 0;
        std::size_t high_cnr_count = 0;

        for (const auto& sat : gnss.satellites) {
            cnr_sum += sat.cnr_x10;
            if (sat.cnr_x10 >= kGnssSpoofCnrThreshold) {
                ++high_cnr_count;
            }
        }

        const auto cnr_avg = static_cast<uint16_t>(cnr_sum / gnss.satellites.size());

        uint32_t dev_sum = 0;
        for (const auto& sat : gnss.satellites) {
            const auto diff = std::abs(static_cast<int32_t>(sat.cnr_x10) - static_cast<int32_t>(cnr_avg));
            dev_sum += static_cast<uint32_t>(diff);
        }
        const auto mean_dev = static_cast<uint16_t>(dev_sum / gnss.satellites.size());

        const auto high_pct = (high_cnr_count * 100) / gnss.satellites.size();
        return (high_pct >= 70 && mean_dev <= kGnssSpoofMaxDev);
    }

    std::array<RfSample, WindowSize> m_history{};
    std::size_t m_head{0};
    std::size_t m_count{0};
    ThreatType  m_current_threat{ThreatType::None};
};

} // namespace embedded::ew
