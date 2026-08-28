#include <cstdint>
#include <cmath>
#include <optional>
#include <span>

namespace uwb {

inline constexpr double SpeedOfLightMS     = 299792458.0;
inline constexpr double TimeResolutionSec  = 15.65104167e-12;
inline constexpr uint64_t TimestampMask    = 0xFFFFFFFFFFULL;
inline constexpr float NlosThresholdDb     = 6.0f;

enum class MessageType : uint8_t {
    Poll     = 0x01,
    Response = 0x02,
    Final    = 0x03
};

#pragma pack(push, 1)
struct Header {
    uint8_t     frame_ctrl[2]{};
    uint8_t     seq_num{0};
    uint16_t    pan_id{0};
    uint16_t    dest_address{0};
    uint16_t    src_address{0};
    MessageType message_type{MessageType::Poll};
};

struct FinalMessage {
    Header   header;
    uint64_t poll_tx_ts{0};     // t1
    uint64_t resp_rx_ts{0};     // t4
    uint64_t final_tx_ts{0};    // t5
};
#pragma pack(pop)

struct CirDiagnostics {
    uint16_t fp_ampl1{0};
    uint16_t fp_ampl2{0};
    uint16_t fp_ampl3{0};
    uint16_t cir_pwr{0};
    uint16_t rxpacc{0};
};

struct RangeResult {
    float distance_meters{0.0f};
    float first_path_power_dbm{0.0f};
    float total_power_dbm{0.0f};
    bool  is_nlos{false};
};

class RangingEngine {
public:
    explicit constexpr RangingEngine(int32_t antenna_delay_ticks = 16436) noexcept
        : antenna_delay_ticks_(antenna_delay_ticks) {}

    [[nodiscard]] static constexpr uint64_t diffTimestamp(uint64_t end_ts, uint64_t start_ts) noexcept {
        return (end_ts - start_ts) & TimestampMask;
    }

    [[nodiscard]] static std::pair<float, float> evaluatePower(const CirDiagnostics& diag) noexcept {
        if (diag.rxpacc == 0) {
            return {-120.0f, -120.0f};
        }
        constexpr float PrfConstantA = 121.74f;
        const float n = static_cast<float>(diag.rxpacc);
        const float f1 = static_cast<float>(diag.fp_ampl1);
        const float f2 = static_cast<float>(diag.fp_ampl2);
        const float f3 = static_cast<float>(diag.fp_ampl3);

        const float fp_sum = (f1 * f1) + (f2 * f2) + (f3 * f3);
        const float fpp = 10.0f * std::log10(fp_sum / (n * n)) - PrfConstantA;

        const float c_pwr = static_cast<float>(diag.cir_pwr);
        const float rxp = 10.0f * std::log10((c_pwr * 131072.0f) / (n * n)) - PrfConstantA;

        return {fpp, rxp};
    }

    [[nodiscard]] std::optional<RangeResult> computeDoubleSided(
        uint64_t t1, uint64_t t2, uint64_t t3,
        uint64_t t4, uint64_t t5, uint64_t t6,
        const CirDiagnostics& diag) const noexcept {

        const uint64_t t_round1 = diffTimestamp(t4, t1);
        const uint64_t t_reply1 = diffTimestamp(t3, t2);
        const uint64_t t_round2 = diffTimestamp(t6, t3);
        const uint64_t t_reply2 = diffTimestamp(t5, t4);

        const double r1 = static_cast<double>(t_round1);
        const double p1 = static_cast<double>(t_reply1);
        const double r2 = static_cast<double>(t_round2);
        const double p2 = static_cast<double>(t_reply2);

        const double numerator   = (r1 * r2) - (p1 * p2);
        const double denominator = r1 + r2 + p1 + p2;

        if (denominator <= 0.0 || numerator <= 0.0) {
            return std::nullopt;
        }

        double tof_ticks = (numerator / denominator) - static_cast<double>(antenna_delay_ticks_);
        if (tof_ticks < 0.0) {
            tof_ticks = 0.0;
        }

        const double tof_sec = tof_ticks * TimeResolutionSec;
        const float distance = static_cast<float>(tof_sec * SpeedOfLightMS);

        if (distance < 0.0f || distance > 200.0f) {
            return std::nullopt;
        }

        const auto [fpp, rxp] = evaluatePower(diag);
        const bool nlos = (rxp - fpp) > NlosThresholdDb;

        return RangeResult{
            .distance_meters      = distance,
            .first_path_power_dbm = fpp,
            .total_power_dbm      = rxp,
            .is_nlos              = nlos
        };
    }

private:
    int32_t antenna_delay_ticks_{16436};
};

} // namespace uwb
