#include <array>
#include <string_view>
#include <optional>
#include <cmath>
#include <algorithm>
#include <cstdint>

enum class Pollutant : std::size_t {
    PM25 = 0,
    PM10,
    CO,
    SO2,
    NO2,
    O3_8H,
    O3_1H,
    Count
};

enum class AqiCategory {
    Good,
    Moderate,
    UnhealthyForSensitiveGroups,
    Unhealthy,
    VeryUnhealthy,
    Hazardous,
    OutOfRange
};

struct Breakpoint {
    float bp_lo;
    float bp_hi;
    int32_t i_lo;
    int32_t i_hi;
};

// Константні таблиці порогових точок EPA (C++ constexpr)
namespace EpaTables {
    using namespace std::string_view_literals;

    constexpr std::array<Breakpoint, 6> PM25{{
        {0.0f,   9.0f,    0,  50},
        {9.1f,  35.4f,   51, 100},
        {35.5f, 55.4f,  101, 150},
        {55.5f, 125.4f, 151, 200},
        {125.5f, 225.4f, 201, 300},
        {225.5f, 325.4f, 301, 500}
    }};

    constexpr std::array<Breakpoint, 6> PM10{{
        {0.0f,   54.0f,   0,  50},
        {55.0f, 154.0f,  51, 100},
        {155.0f, 254.0f, 101, 150},
        {255.0f, 354.0f, 151, 200},
        {355.0f, 424.0f, 201, 300},
        {425.0f, 604.0f, 301, 500}
    }};

    constexpr std::array<Breakpoint, 6> CO{{
        {0.0f,   4.4f,    0,  50},
        {4.5f,   9.4f,   51, 100},
        {9.5f,  12.4f,  101, 150},
        {12.5f, 15.4f,  151, 200},
        {15.5f, 30.4f,  201, 300},
        {30.5f, 50.4f,  301, 500}
    }};

    constexpr std::array<Breakpoint, 6> SO2{{
        {0.0f,   35.0f,   0,  50},
        {36.0f,  75.0f,  51, 100},
        {76.0f, 185.0f, 101, 150},
        {186.0f, 304.0f, 151, 200},
        {305.0f, 604.0f, 201, 300},
        {605.0f, 1004.0f, 301, 500}
    }};

    constexpr std::array<Breakpoint, 6> NO2{{
        {0.0f,    53.0f,   0,  50},
        {54.0f,  100.0f,  51, 100},
        {101.0f, 360.0f, 101, 150},
        {361.0f, 649.0f, 151, 200},
        {650.0f, 1249.0f, 201, 300},
        {1250.0f, 2049.0f, 301, 500}
    }};

    constexpr std::array<Breakpoint, 5> O3_8H{{
        {0.0f,   54.0f,   0,  50},
        {55.0f,  70.0f,  51, 100},
        {71.0f,  85.0f, 101, 150},
        {86.0f, 105.0f, 151, 200},
        {106.0f, 200.0f, 201, 300}
    }};

    constexpr std::array<Breakpoint, 4> O3_1H{{
        {125.0f, 164.0f, 101, 150},
        {165.0f, 204.0f, 151, 200},
        {205.0f, 404.0f, 201, 300},
        {405.0f, 604.0f, 301, 500}
    }};

    constexpr std::array<std::string_view, static_cast<std::size_t>(Pollutant::Count)> PollutantNames{
        "PM2.5"sv, "PM10"sv, "CO"sv, "SO2"sv, "NO2"sv, "O3 (8h)"sv, "O3 (1h)"sv
    };
}

class AqiCalculator {
public:
    struct OverallResult {
        int32_t aqi{-1};
        AqiCategory category{AqiCategory::OutOfRange};
        Pollutant dominant_pollutant{Pollutant::PM25};
        std::string_view dominant_name{"Невідомо"};
        std::string_view category_description{"Поза шкалою"};
        std::array<std::optional<int32_t>, static_cast<std::size_t>(Pollutant::Count)> sub_indices{};
    };

    // Гігроскопічна поправка PM
    [[nodiscard]] static constexpr float compensate_pm_humidity(float raw_pm, float rh_pct, float kappa = 0.35f) noexcept {
        if (rh_pct <= 0.0f) return raw_pm;
        const float rh_clamped = std::min(rh_pct, 99.0f);
        const float gf = 1.0f + kappa * (rh_clamped / (100.0f - rh_clamped));
        return raw_pm / gf;
    }

    // Декупелювання O3 / NO2
    [[nodiscard]] static constexpr std::pair<float, float> decouple_o3_no2(float raw_o3, float raw_no2, float k_cross = 1.0f) noexcept {
        const float corrected_o3 = std::max(0.0f, raw_o3 - k_cross * raw_no2);
        return {corrected_o3, raw_no2};
    }

    // Обчислення суб-індексу для окремого забруднювача
    [[nodiscard]] static std::optional<int32_t> calculate_subindex(Pollutant pollutant, float concentration) noexcept {
        const float c = truncate_concentration(pollutant, concentration);

        switch (pollutant) {
            case Pollutant::PM25:  return interpolate(EpaTables::PM25, c);
            case Pollutant::PM10:  return interpolate(EpaTables::PM10, c);
            case Pollutant::CO:    return interpolate(EpaTables::CO, c);
            case Pollutant::SO2:   return interpolate(EpaTables::SO2, c);
            case Pollutant::NO2:   return interpolate(EpaTables::NO2, c);
            case Pollutant::O3_8H: return interpolate(EpaTables::O3_8H, c);
            case Pollutant::O3_1H: return interpolate(EpaTables::O3_1H, c);
            default: return std::nullopt;
        }
    }

    // Агрегація показників усіх сенсорів методом max()
    [[nodiscard]] static OverallResult calculate_overall(
        const std::array<std::optional<float>, static_cast<std::size_t>(Pollutant::Count)>& telemetry) noexcept {

        OverallResult result{};
        int32_t max_aqi = -1;
        Pollutant dominant = Pollutant::PM25;

        for (std::size_t i = 0; i < telemetry.size(); ++i) {
            if (!telemetry[i].has_value()) continue;

            const auto p = static_cast<Pollutant>(i);
            const auto sub = calculate_subindex(p, *telemetry[i]);
            result.sub_indices[i] = sub;

            if (sub.has_value() && *sub > max_aqi) {
                max_aqi = *sub;
                dominant = p;
            }
        }

        if (max_aqi >= 0) {
            result.aqi = max_aqi;
            result.dominant_pollutant = dominant;
            result.dominant_name = EpaTables::PollutantNames[static_cast<std::size_t>(dominant)];
            result.category = categorize(max_aqi);
            result.category_description = describe_category(result.category);
        }

        return result;
    }

private:
    [[nodiscard]] static constexpr float truncate_concentration(Pollutant pollutant, float conc) noexcept {
        if (conc < 0.0f) return 0.0f;
        switch (pollutant) {
            case Pollutant::PM25:
            case Pollutant::CO:
                return std::floor(conc * 10.0f) / 10.0f;
            default:
                return std::floor(conc);
        }
    }

    template <std::size_t N>
    [[nodiscard]] static std::optional<int32_t> interpolate(
        const std::array<Breakpoint, N>& table, float c) noexcept {

        if (c < table[0].bp_lo) return 0;

        for (const auto& bp : table) {
            if (c >= bp.bp_lo && c <= bp.bp_hi) {
                const float slope = static_cast<float>(bp.i_hi - bp.i_lo) / (bp.bp_hi - bp.bp_lo);
                const float raw_idx = slope * (c - bp.bp_lo) + static_cast<float>(bp.i_lo);
                return static_cast<int32_t>(std::lround(raw_idx));
            }
        }
        return std::nullopt; // Поза межами таблиці
    }

    [[nodiscard]] static constexpr AqiCategory categorize(int32_t aqi) noexcept {
        if (aqi <= 50) return AqiCategory::Good;
        if (aqi <= 100) return AqiCategory::Moderate;
        if (aqi <= 150) return AqiCategory::UnhealthyForSensitiveGroups;
        if (aqi <= 200) return AqiCategory::Unhealthy;
        if (aqi <= 300) return AqiCategory::VeryUnhealthy;
        return AqiCategory::Hazardous;
    }

    [[nodiscard]] static constexpr std::string_view describe_category(AqiCategory cat) noexcept {
        using namespace std::string_view_literals;
        switch (cat) {
            case AqiCategory::Good: return "Добре (Good)"sv;
            case AqiCategory::Moderate: return "Помірне (Moderate)"sv;
            case AqiCategory::UnhealthyForSensitiveGroups: return "Шкідливе для чутливих (USG)"sv;
            case AqiCategory::Unhealthy: return "Шкідливе (Unhealthy)"sv;
            case AqiCategory::VeryUnhealthy: return "Дуже шкідливе (Very Unhealthy)"sv;
            case AqiCategory::Hazardous: return "Небезпечне (Hazardous)"sv;
            default: return "Поза шкалою (Out of Range)"sv;
        }
    }
};
