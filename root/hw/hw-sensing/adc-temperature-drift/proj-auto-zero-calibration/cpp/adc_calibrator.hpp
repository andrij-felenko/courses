#pragma once

#include <cstdint>
#include <cmath>
#include <type_traits>
#include <algorithm>

/**
 * @brief Шаблонний клас для калібрування та температурної компенсації АЦП.
 * 
 * @tparam Bits Розрядність перетворювача (наприклад, 12, 16, 24 біти)
 * @tparam FloatType Тип чисел із рухомою комою для внутрішніх розрахунків (float або double)
 */
template <uint8_t Bits = 12, typename FloatType = float>
class AdcCalibrator {
    static_assert(Bits > 0 && Bits <= 32, "Розрядність АЦП повинна бути від 1 до 32 біт");
    static_assert(std::is_floating_point_v<FloatType>, "Тип для розрахунків повинен бути з рухомою комою");

public:
    static constexpr uint32_t MaxAdcCode = (1ULL << Bits) - 1;

    struct CalibrationParams {
        FloatType vref_nominal_v{3.3f};         // Номінальна напруга ІОН (В)
        FloatType vref_temp_coeff_ppm{20.0f};   // Температурний коефіцієнт ІОН (ppm/°C)
        FloatType t_cal_celsius{25.0f};         // Температура під час заводського калібрування (°C)
        FloatType gain_temp_coeff_ppm{15.0f};   // Температурний коефіцієнт підсилення АЦП (ppm/°C)
        FloatType offset_drift_uv_per_c{2.5f};  // Температурний дрейф зміщення нуля (мкВ/°C)
        FloatType v_offset_base_mv{1.2f};       // Базове зміщення нуля при t_cal (мВ)
    };

    explicit AdcCalibrator(const CalibrationParams& params = CalibrationParams{})
        : params_(params),
          current_offset_mv_(params.v_offset_base_mv),
          current_gain_factor_(1.0f),
          filtered_temp_celsius_(params.t_cal_celsius) {}

    /**
     * @brief Оновлення поточної температури кристала/плати за допомогою експоненційного фільтра.
     * @param raw_temp_celsius Миттєвий вимір температури з термодавача.
     * @param alpha Вага нового виміру (0.0 .. 1.0) для експоненційного згладжування.
     */
    void update_temperature(FloatType raw_temp_celsius, FloatType alpha = 0.1f) noexcept {
        filtered_temp_celsius_ = (alpha * raw_temp_celsius) + ((1.0f - alpha) * filtered_temp_celsius_);
        recalculate_coefficients();
    }

    /**
     * @brief Автонульове калібрування: оновлення зміщення нуля за замкненого на землю входу.
     * @param ground_code Сирий відлік АЦП при закороченому на землю вході.
     */
    void calibrate_zero_offset(uint32_t ground_code) noexcept {
        FloatType vref_now = get_effective_vref();
        FloatType measured_offset_v = (static_cast<FloatType>(ground_code) / static_cast<FloatType>(MaxAdcCode)) * vref_now;
        current_offset_mv_ = measured_offset_v * 1000.0f;
    }

    /**
     * @brief Двоточкове калібрування діапазону (Full-Scale) за відомим еталонним сигналом.
     * @param ref_code Сирий відлік АЦП під час подачі еталонної напруги.
     * @param actual_ref_mv Фактичне значення еталонної напруги (мВ).
     */
    void calibrate_gain(uint32_t ref_code, FloatType actual_ref_mv) noexcept {
        FloatType vref_now_mv = get_effective_vref() * 1000.0f;
        FloatType uncalibrated_v_mv = (static_cast<FloatType>(ref_code) / static_cast<FloatType>(MaxAdcCode)) * vref_now_mv;
        FloatType delta_v = uncalibrated_v_mv - current_offset_mv_;
        if (std::abs(delta_v) > 1e-6f) {
            current_gain_factor_ = actual_ref_mv / delta_v;
        }
    }

    /**
     * @brief Корекція сирого коду АЦП з урахуванням температури, дрейфу зміщення та масштабу.
     * @param raw_code Сирий вихідний код АЦП.
     * @return Відновлена скоригована напруга вхідного сигналу (у мілівольтах).
     */
    [[nodiscard]] FloatType convert_to_millivolts(uint32_t raw_code) const noexcept {
        FloatType vref_now_mv = get_effective_vref() * 1000.0f;
        FloatType raw_voltage_mv = (static_cast<FloatType>(raw_code) / static_cast<FloatType>(MaxAdcCode)) * vref_now_mv;
        
        // Віднімання температурно компенсованого зміщення нуля та масштабування
        FloatType compensated_voltage_mv = (raw_voltage_mv - current_offset_mv_) * current_gain_factor_;
        return compensated_voltage_mv;
    }

    /**
     * @brief Отримання скоригованого коду АЦП (якби АЦП був ідеальним).
     */
    [[nodiscard]] uint32_t correct_code(uint32_t raw_code) const noexcept {
        FloatType mv = convert_to_millivolts(raw_code);
        FloatType nominal_vref_mv = params_.vref_nominal_v * 1000.0f;
        FloatType ideal_code = (mv / nominal_vref_mv) * static_cast<FloatType>(MaxAdcCode);
        
        if (ideal_code < 0.0f) return 0;
        if (ideal_code > static_cast<FloatType>(MaxAdcCode)) return MaxAdcCode;
        return static_cast<uint32_t>(std::round(ideal_code));
    }

    [[nodiscard]] FloatType temperature() const noexcept { return filtered_temp_celsius_; }
    [[nodiscard]] FloatType offset_drift_mv() const noexcept { return current_offset_mv_; }
    [[nodiscard]] FloatType gain_factor() const noexcept { return current_gain_factor_; }

private:
    CalibrationParams params_;
    FloatType current_offset_mv_{0.0f};
    FloatType current_gain_factor_{1.0f};
    FloatType filtered_temp_celsius_{25.0f};

    /**
     * @brief Розрахунок ефективної опорної напруги за поточної температури.
     */
    [[nodiscard]] FloatType get_effective_vref() const noexcept {
        FloatType delta_t = filtered_temp_celsius_ - params_.t_cal_celsius;
        FloatType vref_drift_factor = 1.0f + (params_.vref_temp_coeff_ppm * 1e-6f * delta_t);
        return params_.vref_nominal_v * vref_drift_factor;
    }

    /**
     * @brief Перерахунок динамічного температурного дрейфу підсилення та зміщення.
     */
    void recalculate_coefficients() noexcept {
        FloatType delta_t = filtered_temp_celsius_ - params_.t_cal_celsius;
        
        // Дрейф зміщення: базова величина + коефіцієнт (мкВ/°C) * ΔT
        current_offset_mv_ = params_.v_offset_base_mv + (params_.offset_drift_uv_per_c * 0.001f * delta_t);
        
        // Дрейф коефіцієнта передачі тракту
        FloatType gain_drift = 1.0f + (params_.gain_temp_coeff_ppm * 1e-6f * delta_t);
        current_gain_factor_ = gain_drift;
    }
};
