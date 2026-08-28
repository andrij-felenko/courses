#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <algorithm>

enum class ResetCause : uint8_t {
    Por        = 0,
    Wdt        = 1,
    Bor        = 2,
    Soft       = 3,
    HardFault  = 4,
    Pin        = 5
};

struct HealthMetrics {
    ResetCause reset_cause       {ResetCause::Por};
    bool       low_batt_flag     {false};
    bool       radio_retry_flag  {false};
    bool       flash_error_flag  {false};
    bool       sensor_error_flag {false};
    bool       tamper_flag       {false};
    uint16_t   v_batt_mv         {3300};
    uint16_t   v_sag_mv          {100};
    int8_t     rssi_dbm          {-85};
    uint8_t    tx_retries        {0};
    uint32_t   min_free_heap     {8192};
    int8_t     mcu_temp_c        {25};
    uint32_t   uptime_hours      {0};
};

enum class DiagScheduleMode : uint8_t {
    PiggybackOnly = 0,
    FullHeartbeat = 1,
    BurstAnomaly  = 2
};

class HealthTelemetryEncoder {
public:
    static constexpr size_t FrameSize = 8;

    static std::array<uint8_t, FrameSize> pack(const HealthMetrics& in) noexcept {
        std::array<uint8_t, FrameSize> out{};

        // Байт 0: Прапорці та причина перезавантаження
        uint8_t b0 = static_cast<uint8_t>(static_cast<uint8_t>(in.reset_cause) << 5);
        if (in.low_batt_flag)     b0 |= (1U << 4);
        if (in.radio_retry_flag)  b0 |= (1U << 3);
        if (in.flash_error_flag)  b0 |= (1U << 2);
        if (in.sensor_error_flag) b0 |= (1U << 1);
        if (in.tamper_flag)       b0 |= (1U << 0);
        out[0] = b0;

        // Байт 1: Напруга під навантаженням (2000..4550 мВ, крок 10 мВ)
        const uint16_t v = std::clamp<uint16_t>(in.v_batt_mv, 2000, 4550);
        out[1] = static_cast<uint8_t>((v - 2000) / 10);

        // Байт 2: Просадка напруги (0..510 мВ, крок 2 мВ)
        const uint16_t sag = std::clamp<uint16_t>(in.v_sag_mv, 0, 510);
        out[2] = static_cast<uint8_t>(sag / 2);

        // Байт 3: RSSI (-120..-57 dBm) + Retries (0..3)
        const int8_t r = std::clamp<int8_t>(in.rssi_dbm, -120, -57);
        const uint8_t rssi_encoded = static_cast<uint8_t>(r + 120);
        const uint8_t retries = std::min<uint8_t>(in.tx_retries, 3);
        out[3] = static_cast<uint8_t>((rssi_encoded << 2) | (retries & 0x03));

        // Байт 4: Мінімальний залишок купи (кванти 256 байтів)
        const uint32_t heap_q = in.min_free_heap / 256;
        out[4] = static_cast<uint8_t>(std::min<uint32_t>(heap_q, 255));

        // Байт 5: Температура MCU (-40..+87 °C зі зміщенням +40)
        const int8_t temp = std::clamp<int8_t>(in.mcu_temp_c, -40, 87);
        out[5] = static_cast<uint8_t>(temp + 40);

        // Байт 6-7: Аптайм у годинах (Little-Endian)
        const uint16_t up = static_cast<uint16_t>(std::min<uint32_t>(in.uptime_hours, 65535));
        out[6] = static_cast<uint8_t>(up & 0xFF);
        out[7] = static_cast<uint8_t>((up >> 8) & 0xFF);

        return out;
    }

    static HealthMetrics unpack(std::span<const uint8_t, FrameSize> in) noexcept {
        HealthMetrics out{};

        // Байт 0
        out.reset_cause       = static_cast<ResetCause>((in[0] >> 5) & 0x07);
        out.low_batt_flag     = (in[0] & (1U << 4)) != 0;
        out.radio_retry_flag  = (in[0] & (1U << 3)) != 0;
        out.flash_error_flag  = (in[0] & (1U << 2)) != 0;
        out.sensor_error_flag = (in[0] & (1U << 1)) != 0;
        out.tamper_flag       = (in[0] & (1U << 0)) != 0;

        // Байт 1
        out.v_batt_mv = static_cast<uint16_t>(in[1] * 10 + 2000);

        // Байт 2
        out.v_sag_mv = static_cast<uint16_t>(in[2] * 2);

        // Байт 3
        out.rssi_dbm   = static_cast<int8_t>((in[3] >> 2) - 120);
        out.tx_retries = in[3] & 0x03;

        // Байт 4
        out.min_free_heap = static_cast<uint32_t>(in[4] * 256);

        // Байт 5
        out.mcu_temp_c = static_cast<int8_t>(in[5] - 40);

        // Байт 6-7
        out.uptime_hours = static_cast<uint32_t>(in[6] | (in[7] << 8));

        return out;
    }

    static uint8_t generatePiggybackStatus(const HealthMetrics& in) noexcept {
        uint8_t status = 0;
        if (in.low_batt_flag || in.v_batt_mv < 3000)  status |= (1U << 7);
        if (in.v_sag_mv > 350)                         status |= (1U << 6);
        if (in.radio_retry_flag || in.tx_retries > 2)  status |= (1U << 5);
        if (in.flash_error_flag)                       status |= (1U << 4);
        if (in.sensor_error_flag)                      status |= (1U << 3);
        if (in.min_free_heap < 1024)                   status |= (1U << 2);
        return status;
    }

    static DiagScheduleMode evaluateScheduler(const HealthMetrics& m, uint32_t cycles_since_full) noexcept {
        if (m.v_sag_mv > 400 || m.v_batt_mv < 2900 || m.tx_retries >= 3 || m.min_free_heap < 512) {
            return DiagScheduleMode::BurstAnomaly;
        }
        if (cycles_since_full >= 36) {
            return DiagScheduleMode::FullHeartbeat;
        }
        return DiagScheduleMode::PiggybackOnly;
    }
};
