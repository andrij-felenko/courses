// ============================================================================
// Енергоефективний менеджер радіотранзакцій (C++20 / RAII та Strict Types)
// ============================================================================
#include <cstdint>
#include <array>
#include <span>
#include <chrono>
#include <algorithm>

namespace embedded::radio {

using namespace std::chrono_literals;

enum class SpreadingFactor : uint8_t {
    SF7 = 7, SF8 = 8, SF9 = 9, SF10 = 10, SF11 = 11, SF12 = 12
};

enum class State : uint8_t {
    Sleep,
    WarmupPll,
    Transmitting,
    WaitRx1,
    ListenRx1,
    WaitRx2,
    ListenRx2
};

#pragma pack(push, 1)
struct TelemetryFrame {
    int16_t  temp_centi_deg;
    uint8_t  humidity_half_pct;
    uint8_t  battery_raw_mv;
    uint8_t  status_flags;

    static constexpr size_t Size = 5;
};
#pragma pack(pop)

class EnergyAwareRadioManager {
public:
    static constexpr uint8_t MaxRetries = 3;
    static constexpr uint32_t AdrAckLimit = 64;
    static constexpr uint32_t AdrAckDelay = 32;

    EnergyAwareRadioManager() = default;

    [[nodiscard]] std::array<uint8_t, TelemetryFrame::Size> pack_telemetry(
        float temp_c, float hum_pct, float v_batt, bool sensor_ok) const noexcept 
    {
        std::array<uint8_t, TelemetryFrame::Size> buffer{};
        TelemetryFrame frame{
            .temp_centi_deg = static_cast<int16_t>(temp_c * 100.0f),
            .humidity_half_pct = static_cast<uint8_t>(std::clamp(hum_pct, 0.0f, 100.0f) * 2.0f),
            .battery_raw_mv = static_cast<uint8_t>((std::clamp(static_cast<uint32_t>(v_batt * 1000.0f), 2000u, 4550u) - 2000) / 10),
            .status_flags = static_cast<uint8_t>(sensor_ok ? 0x00 : 0x01)
        };
        std::copy_n(reinterpret_cast<const uint8_t*>(&frame), TelemetryFrame::Size, buffer.begin());
        return buffer;
    }

    void start_transmission(std::chrono::milliseconds toa) noexcept {
        state_ = State::Transmitting;
        ++tx_count_;
        ++adr_ack_counter_;

        const uint32_t current_ma = (tx_power_dbm_ >= 20) ? 95 : ((tx_power_dbm_ <= 2) ? 12 : 22);
        total_microcoulombs_ += (current_ma * static_cast<uint32_t>(toa.count())) + (5 * 2);
    }

    void handle_ack(int8_t gateway_snr) noexcept {
        adr_ack_counter_ = 0;
        retry_count_ = 0;
        state_ = State::Sleep;

        if (gateway_snr > 8 && tx_power_dbm_ > 2) {
            tx_power_dbm_ -= 3;
        }
    }

    void handle_timeout() noexcept {
        if (retry_count_ < MaxRetries) {
            ++retry_count_;
            state_ = State::Sleep;
            return;
        }

        if (adr_ack_counter_ >= (AdrAckLimit + AdrAckDelay)) {
            if (tx_power_dbm_ < 20) {
                tx_power_dbm_ = 20;
            } else if (sf_ != SpreadingFactor::SF12) {
                sf_ = static_cast<SpreadingFactor>(static_cast<uint8_t>(sf_) + 1);
                adr_ack_counter_ = AdrAckLimit;
            }
        }
        retry_count_ = 0;
        state_ = State::Sleep;
    }

    [[nodiscard]] SpreadingFactor spreading_factor() const noexcept { return sf_; }
    [[nodiscard]] int8_t tx_power() const noexcept { return tx_power_dbm_; }
    [[nodiscard]] uint64_t total_charge_uc() const noexcept { return total_microcoulombs_; }
    [[nodiscard]] State current_state() const noexcept { return state_; }

private:
    State state_{State::Sleep};
    SpreadingFactor sf_{SpreadingFactor::SF7};
    int8_t tx_power_dbm_{14};
    uint32_t tx_count_{0};
    uint32_t adr_ack_counter_{0};
    uint64_t total_microcoulombs_{0};
    uint8_t retry_count_{0};
};

} // namespace embedded::radio
