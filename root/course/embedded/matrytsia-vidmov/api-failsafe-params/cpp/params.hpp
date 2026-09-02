#pragma once

// Реєстр параметрів failsafe: описи, діапазони, дефолти й перевірка інваріантів.

#include <array>
#include <cstdint>
#include <expected>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace autopilot::failsafe {

enum class ParamId : std::uint8_t {
    ThrEnable, ThrValue, RcTimeout, RcRecover,
    GcsTimeout, GcsEnable,
    EkfThresh, GnssHdopMax, GnssTimeout,
    BattLowV, BattCritV, BattHystMs, BattAct,
    FenceEnable, FenceRadius, FenceAltMax, FenceAct,
    CrashDump, LastGaspTx,
    Count
};

enum class ParamType : std::uint8_t { Int8, Int16, Float };

struct ParamDesc {
    std::string_view name;   // param_id MAVLink: не більше за 16 символів
    ParamType        type;
    float            min;
    float            max;
    float            def;
    std::uint8_t     since;  // версія схеми, у якій параметр з'явився
};

inline constexpr std::size_t kParamCount = static_cast<std::size_t>(ParamId::Count);

inline constexpr std::array<ParamDesc, kParamCount> kParamDesc{{
    { "FS_THR_ENABLE",    ParamType::Int8,     0.0f,     3.0f,    1.0f, 1 },
    { "FS_THR_VALUE",     ParamType::Int16,  900.0f,  1000.0f,  950.0f, 1 },
    { "FS_RC_TIMEOUT",    ParamType::Float,    0.5f,    10.0f,    1.5f, 1 },
    { "FS_RC_RECOVER",    ParamType::Float,    1.0f,     5.0f,    2.0f, 2 },
    { "FS_GCS_TIMEOUT",   ParamType::Float,    2.0f,    60.0f,    5.0f, 1 },
    { "FS_GCS_ENABLE",    ParamType::Int8,     0.0f,     2.0f,    1.0f, 1 },
    { "FS_EKF_THRESH",    ParamType::Float,    0.5f,     2.0f,    1.0f, 2 },
    { "FS_GNSS_HDOP_MAX", ParamType::Float,    1.2f,     5.0f,    2.5f, 2 },
    { "FS_GNSS_TIMEOUT",  ParamType::Float,    1.0f,    10.0f,    3.0f, 2 },
    { "FS_BATT_LOW_V",    ParamType::Float,    3.4f,     3.7f,   3.55f, 1 },
    { "FS_BATT_CRIT_V",   ParamType::Float,    3.1f,    3.45f,   3.30f, 1 },
    { "FS_BATT_HYST_MS",  ParamType::Int16,  200.0f,  3000.0f, 1000.0f, 2 },
    { "FS_BATT_ACT",      ParamType::Int8,     1.0f,     4.0f,    2.0f, 1 },
    { "FS_FENCE_ENABLE",  ParamType::Int8,     0.0f,     1.0f,    1.0f, 1 },
    { "FS_FENCE_RADIUS",  ParamType::Float,   50.0f, 10000.0f,  500.0f, 1 },
    { "FS_FENCE_ALT_MAX", ParamType::Float,   10.0f,   500.0f,  120.0f, 1 },
    { "FS_FENCE_ACT",     ParamType::Int8,     1.0f,     3.0f,    1.0f, 1 },
    { "FS_CRASH_DUMP",    ParamType::Int8,     0.0f,     1.0f,    1.0f, 3 },
    { "FS_LAST_GASP_TX",  ParamType::Int8,     0.0f,     1.0f,    1.0f, 3 },
}};

enum class ParamError { UnknownName, OutOfRange };

std::string_view toString(ParamError e) noexcept;

constexpr const ParamDesc& desc(ParamId id) noexcept
{
    return kParamDesc[static_cast<std::size_t>(id)];
}

class ParamBlock {
public:
    ParamBlock() noexcept;  // заводські значення

    float get(ParamId id) const noexcept { return v_[static_cast<std::size_t>(id)]; }
    int   getInt(ParamId id) const noexcept { return static_cast<int>(get(id)); }

    std::expected<void, ParamError> set(ParamId id, float value) noexcept;
    std::expected<void, ParamError> set(std::string_view name, float value) noexcept;

    static std::expected<ParamId, ParamError> find(std::string_view name) noexcept;

    // Сирий зріз для серіалізації у Flash.
    std::span<const float> raw() const noexcept { return v_; }
    // Відновлення зі сховища: значення поза діапазоном замінюються заводськими.
    // Повертає кількість таких замін.
    std::size_t restore(std::span<const float> stored) noexcept;

    // Передпольотна перевірка інваріантів: порожній вектор — усе гаразд.
    std::vector<std::string> validate(float rtlAltM) const;

private:
    std::array<float, kParamCount> v_{};
};

} // namespace autopilot::failsafe
