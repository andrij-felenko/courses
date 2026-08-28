// uvi_calculator.hpp
// Ідіоматичний C++20 модуль обчислення УФ-індексу та еритемної дози

#pragma once

#include <cstdint>
#include <string_view>
#include <expected>
#include <algorithm>
#include <chrono>

namespace sensing::uv {

// Категорії небезпеки ультрафіолетового опромінення за шкалою ВООЗ
enum class RiskLevel : std::uint8_t {
    Low = 0,       // UVI 0.0 .. 2.9
    Moderate,      // UVI 3.0 .. 5.9
    High,          // UVI 6.0 .. 7.9
    VeryHigh,      // UVI 8.0 .. 10.9
    Extreme        // UVI 11.0+
};

// Класифікація фототипів шкіри за Фіцпатріком
enum class SkinPhototype : std::uint8_t {
    TypeI = 1,   // Дуже світла, руде волосся (1 MED ≈ 200 Дж/м²)
    TypeII,      // Світла, скандинавський тип (1 MED ≈ 250 Дж/м²)
    TypeIII,     // Середньоєвропейський тип  (1 MED ≈ 350 Дж/м²)
    TypeIV,      // Середземноморський тип    (1 MED ≈ 450 Дж/м²)
    TypeV,       // Азійський/латиноамериканський (1 MED ≈ 600 Дж/м²)
    TypeVI       // Темна шкіра, африканський тип (1 MED ≈ 1000 Дж/м²)
};

// Можливі апаратні та розрахункові помилки
enum class SensorError : std::uint8_t {
    InvalidCalibration,
    SaturatedReading,
    CommunicationFailure
};

// Сирі 16-бітні кванти від АЦП
struct RawData {
    std::uint16_t uva{0};
    std::uint16_t uvb{0};
    std::uint16_t visible{0};
    std::uint16_t infrared{0};
};

// Калібрувальна матриця компенсації перехресної чутливості
struct CalibrationMatrix {
    float uva_a_vis{2.22f};
    float uva_b_ir{2.12f};
    float uvb_c_vis{2.95f};
    float uvb_d_ir{1.74f};
    float uva_offset{0.0f};
    float uvb_offset{0.0f};
    float uva_responsivity{0.001461f};
    float uvb_responsivity{0.002591f};

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        return uva_responsivity > 0.0f && uvb_responsivity > 0.0f;
    }
};

// Результат комплексного розрахунку УФ-індексу
struct IndexResult {
    float uva_compensated{0.0f};
    float uvb_compensated{0.0f};
    float uv_index{0.0f};
    float erythemal_irradiance_wm2{0.0f};
    RiskLevel risk{RiskLevel::Low};
    std::chrono::seconds safe_exposure_time{0};

    [[nodiscard]] constexpr std::string_view risk_description() const noexcept {
        switch (risk) {
            case RiskLevel::Low:
                return "Низький рівень: захист не потрібен";
            case RiskLevel::Moderate:
                return "Помірний: необхідні сонцезахисні окуляри та капелюх";
            case RiskLevel::High:
                return "Високий: обов'язковий крем SPF 30+ та затінок";
            case RiskLevel::VeryHigh:
                return "Дуже високий: зведіть перебування на вулиці до мінімуму";
            case RiskLevel::Extreme:
                return "Екстремальний: небезпечно виходити без спецзахисту";
        }
        return "Невідомо";
    }
};

class Calculator {
public:
    explicit constexpr Calculator(CalibrationMatrix calib = {}) noexcept
        : calib_{calib} {}

    [[nodiscard]] constexpr const CalibrationMatrix& calibration() const noexcept {
        return calib_;
    }

    constexpr void set_calibration(const CalibrationMatrix& calib) noexcept {
        calib_ = calib;
    }

    // Обчислення УФ-індексу та часу експозиції
    [[nodiscard]] constexpr std::expected<IndexResult, SensorError>
    process(const RawData& raw, SkinPhototype phototype = SkinPhototype::TypeII) const noexcept {
        if (!calib_.is_valid()) {
            return std::unexpected(SensorError::InvalidCalibration);
        }

        const float vis = static_cast<float>(raw.visible);
        const float ir  = static_cast<float>(raw.infrared);

        // Матричне віднімання паразитних засвіток видимої та ІЧ смуг
        float comp_uva = static_cast<float>(raw.uva)
                         - (calib_.uva_a_vis * vis)
                         - (calib_.uva_b_ir * ir)
                         - calib_.uva_offset;

        float comp_uvb = static_cast<float>(raw.uvb)
                         - (calib_.uvb_c_vis * vis)
                         - (calib_.uvb_d_ir * ir)
                         - calib_.uvb_offset;

        comp_uva = std::max(0.0f, comp_uva);
        comp_uvb = std::max(0.0f, comp_uvb);

        // Переведення в еритемний еквівалент UVI
        const float uvi_a = comp_uva * calib_.uva_responsivity;
        const float uvi_b = comp_uvb * calib_.uvb_responsivity;
        const float total_uvi = std::max(0.0f, (uvi_a + uvi_b) * 0.5f);

        // 1 UVI відповідає 0.025 Вт/м² еритемно-ефективного випромінювання
        const float e_er = total_uvi * 0.025f;

        IndexResult result{
            .uva_compensated = comp_uva,
            .uvb_compensated = comp_uvb,
            .uv_index = total_uvi,
            .erythemal_irradiance_wm2 = e_er,
            .risk = classify_risk(total_uvi),
            .safe_exposure_time = calculate_safe_time(e_er, phototype)
        };

        return result;
    }

private:
    CalibrationMatrix calib_;

    [[nodiscard]] static constexpr RiskLevel classify_risk(float uvi) noexcept {
        if (uvi < 3.0f)  return RiskLevel::Low;
        if (uvi < 6.0f)  return RiskLevel::Moderate;
        if (uvi < 8.0f)  return RiskLevel::High;
        if (uvi < 11.0f) return RiskLevel::VeryHigh;
        return RiskLevel::Extreme;
    }

    [[nodiscard]] static constexpr std::chrono::seconds
    calculate_safe_time(float e_er, SkinPhototype skin) noexcept {
        if (e_er < 0.0001f) {
            return std::chrono::hours(24);
        }

        const float med_joules = get_med_threshold(skin);
        const float seconds = med_joules / e_er;

        if (seconds >= 86400.0f) {
            return std::chrono::hours(24);
        }
        return std::chrono::seconds(static_cast<std::int64_t>(seconds));
    }

    [[nodiscard]] static constexpr float get_med_threshold(SkinPhototype skin) noexcept {
        switch (skin) {
            case SkinPhototype::TypeI:   return 200.0f;
            case SkinPhototype::TypeII:  return 250.0f;
            case SkinPhototype::TypeIII: return 350.0f;
            case SkinPhototype::TypeIV:  return 450.0f;
            case SkinPhototype::TypeV:   return 600.0f;
            case SkinPhototype::TypeVI:  return 1000.0f;
        }
        return 250.0f;
    }
};

} // namespace sensing::uv
