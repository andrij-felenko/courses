#include "lm35_filter.hpp"

LM35Filter::LM35Filter(AdcConfig adc_cfg,
                       CalibrationParams cal_params,
                       AnalogReadCallback read_cb,
                       size_t window_size) noexcept
    : adc_config_(adc_cfg),
      calibration_(cal_params),
      read_callback_(read_cb),
      window_size_((window_size > 0 && window_size <= MAX_BUFFER_CAPACITY) ? window_size : 8) {
    buffer_.fill(0);
}

bool LM35Filter::init() noexcept {
    if (!read_callback_) {
        return false;
    }

    resetBuffer();

    // Заповнюємо буфер первинними відліками для швидкого виходу на робочий режим
    for (size_t i = 0; i < window_size_; ++i) {
        sample();
    }

    return true;
}

uint16_t LM35Filter::sample() noexcept {
    if (!read_callback_) {
        return 0;
    }

    uint16_t raw_val = read_callback_(adc_config_.analog_pin);

    // Якщо буфер вже заповнений до window_size_, віднімаємо старий елемент зі суми
    if (count_ >= window_size_) {
        buffer_sum_ -= buffer_[write_index_];
    } else {
        ++count_;
    }

    // Записуємо новий відлік і додаємо його до суми
    buffer_[write_index_] = raw_val;
    buffer_sum_ += raw_val;

    // Переміщуємо індекс запису в кільцевому буфері
    write_index_ = (write_index_ + 1) % window_size_;

    return raw_val;
}

float LM35Filter::getFilteredRaw() const noexcept {
    if (count_ == 0) {
        return 0.0f;
    }
    return static_cast<float>(buffer_sum_) / static_cast<float>(count_);
}

float LM35Filter::getTemperatureCelsius() const noexcept {
    float filtered_raw = getFilteredRaw();
    uint32_t max_adc = adc_config_.maxAdcValue();
    if (max_adc == 0) {
        return 0.0f;
    }

    float voltage_mv = (filtered_raw / static_cast<float>(max_adc)) * adc_config_.ref_voltage_v * 1000.0f;
    float uncalibrated_temp = voltage_mv / (LM35_SENSITIVITY_V_PER_C * 1000.0f);
    return (uncalibrated_temp + calibration_.offset_celsius) * calibration_.scale_factor;
}

float LM35Filter::rawToCelsius(uint16_t raw_adc) const noexcept {
    float voltage_mv = rawToMillivolts(raw_adc);
    float uncalibrated_temp = voltage_mv / (LM35_SENSITIVITY_V_PER_C * 1000.0f);
    return (uncalibrated_temp + calibration_.offset_celsius) * calibration_.scale_factor;
}

float LM35Filter::rawToMillivolts(uint16_t raw_adc) const noexcept {
    uint32_t max_adc = adc_config_.maxAdcValue();
    if (max_adc == 0) {
        return 0.0f;
    }

    // Напруга у вольтах: V = (raw / max_adc) * ref_voltage_v
    float voltage_v = (static_cast<float>(raw_adc) / static_cast<float>(max_adc)) * adc_config_.ref_voltage_v;
    return voltage_v * 1000.0f;
}

bool LM35Filter::setWindowSize(size_t window_size) noexcept {
    if (window_size == 0 || window_size > MAX_BUFFER_CAPACITY) {
        return false;
    }
    window_size_ = window_size;
    resetBuffer();
    return true;
}

void LM35Filter::resetBuffer() noexcept {
    buffer_.fill(0);
    write_index_ = 0;
    count_ = 0;
    buffer_sum_ = 0;
}
