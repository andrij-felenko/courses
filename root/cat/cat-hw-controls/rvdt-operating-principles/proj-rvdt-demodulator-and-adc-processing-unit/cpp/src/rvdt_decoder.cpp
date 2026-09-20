#include "rvdt_decoder.hpp"
#include <algorithm>

namespace controls {

std::optional<RVDTResult> RVDTDecoder::update() {
    auto sample_opt = adc_hal_.readSample();
    if (!sample_opt.has_value()) {
        return std::nullopt; // Помилка зчитування АЦП
    }

    const auto& sample = sample_opt.value();

    // Перевірка цілісності колу живлення та збудження (запобігання діленню на нуль при обриві)
    const float sum_s = sample.s1_volts + sample.s2_volts;
    if (sample.v_ref_volts < config_.min_valid_vref || sum_s <= 1e-4f) {
        RVDTResult invalid_res{};
        invalid_res.is_valid = false;
        return invalid_res;
    }

    // Нормалізоване пропорційне відношення амплітуд: R = (S1 - S2) / (S1 + S2)
    // Усуває вплив дрейфу напруги збудження
    const float diff_s = sample.s1_volts - sample.s2_volts;
    const float raw_ratio = diff_s / sum_s;

    // Однополюсний цифровий ІІР-фільтр низьких частот для пригнічення ВЧ-завад
    if (!filtered_ratio_.has_value()) {
        filtered_ratio_ = raw_ratio;
    } else {
        const float a = std::clamp(config_.iir_alpha, 0.01f, 1.0f);
        filtered_ratio_ = filtered_ratio_.value() + a * (raw_ratio - filtered_ratio_.value());
    }

    // Поліноміальна лінеаризація нелінійності магнітопроводу RVDT
    const float corrected_ratio = config_.poly_corr.evaluate(filtered_ratio_.value());

    // Перетворення нормалізованої величини у фізичний кут у градусах
    RVDTResult result{};
    result.angle_degrees = corrected_ratio * config_.sensitivity_deg_per_ratio;
    result.raw_ratio = raw_ratio;
    result.is_valid = true;

    return result;
}

} // namespace controls
