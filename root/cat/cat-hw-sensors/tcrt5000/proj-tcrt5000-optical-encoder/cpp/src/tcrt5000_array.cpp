#include "tcrt5000_array.hpp"
#include <algorithm>
#include <cmath>

TCRT5000Array::TCRT5000Array(IAdcArrayReader& adc_reader, std::size_t sensor_count, float filter_alpha)
    : adc_reader_(adc_reader),
      sensor_count_(sensor_count),
      filter_alpha_(filter_alpha),
      calibration_(sensor_count),
      raw_buffer_(sensor_count, 0),
      filtered_raw_(sensor_count, 0),
      normalized_values_(sensor_count, 0) {
    
    std::int32_t center = static_cast<std::int32_t>((sensor_count_ - 1) * 1000 / 2);
    last_position_ = center;
}

void TCRT5000Array::reset_calibration() {
    for (auto& cal : calibration_) {
        cal.min_value = 4095;
        cal.max_value = 0;
    }
}

bool TCRT5000Array::calibrate_step() {
    if (!adc_reader_.read_channels(raw_buffer_)) {
        return false;
    }

    for (std::size_t i = 0; i < sensor_count_; ++i) {
        if (raw_buffer_[i] < calibration_[i].min_value) {
            calibration_[i].min_value = raw_buffer_[i];
        }
        if (raw_buffer_[i] > calibration_[i].max_value) {
            calibration_[i].max_value = raw_buffer_[i];
        }
    }
    return true;
}

bool TCRT5000Array::update() {
    if (!adc_reader_.read_channels(raw_buffer_)) {
        return false;
    }

    // 1. Цифрова ЕМА-фільтрація оптичного шуму та засвічення
    if (first_read_) {
        for (std::size_t i = 0; i < sensor_count_; ++i) {
            filtered_raw_[i] = raw_buffer_[i];
        }
        first_read_ = false;
    } else {
        for (std::size_t i = 0; i < sensor_count_; ++i) {
            float filtered = filter_alpha_ * static_cast<float>(raw_buffer_[i]) +
                             (1.0f - filter_alpha_) * static_cast<float>(filtered_raw_[i]);
            filtered_raw_[i] = static_cast<std::uint16_t>(filtered);
        }
    }

    // 2. Нормування вибірок до діапазону [0, 1000]
    for (std::size_t i = 0; i < sensor_count_; ++i) {
        std::uint16_t min_val = calibration_[i].min_value;
        std::uint16_t max_val = calibration_[i].max_value;

        if (max_val <= min_val) {
            normalized_values_[i] = 0;
            continue;
        }

        std::int32_t val = static_cast<std::int32_t>(filtered_raw_[i]);
        std::int32_t norm = ((val - static_cast<std::int32_t>(min_val)) * 1000) /
                             (static_cast<std::int32_t>(max_val) - static_cast<std::int32_t>(min_val));

        normalized_values_[i] = static_cast<std::uint16_t>(std::clamp(norm, 0, 1000));
    }

    // 3. Обчислення позиції лінії за зваженим середнім
    std::uint64_t weighted_sum = 0;
    std::uint32_t sum_values = 0;

    for (std::size_t i = 0; i < sensor_count_; ++i) {
        std::uint32_t val = normalized_values_[i];
        
        // Порогова відсічка дрібних фонових завад
        if (val > 50) {
            weighted_sum += static_cast<std::uint64_t>(i) * 1000ULL * val;
            sum_values += val;
        }
    }

    // 4. Розрахунок зсуву лінії відносно центру
    std::int32_t center = static_cast<std::int32_t>((sensor_count_ - 1) * 1000 / 2);

    if (sum_values > 0) {
        last_position_ = static_cast<std::int32_t>(weighted_sum / sum_values);
        line_detected_ = true;
    } else {
        line_detected_ = false;
        if (last_position_ < center) {
            last_position_ = 0;
        } else {
            last_position_ = static_cast<std::int32_t>((sensor_count_ - 1) * 1000);
        }
    }

    line_error_ = last_position_ - center;
    return true;
}

std::int32_t TCRT5000Array::get_line_error() const {
    return line_error_;
}

std::int32_t TCRT5000Array::get_line_position() const {
    return last_position_;
}

bool TCRT5000Array::is_line_detected() const {
    return line_detected_;
}

const std::vector<std::uint16_t>& TCRT5000Array::get_normalized_values() const {
    return normalized_values_;
}

const std::vector<std::uint16_t>& TCRT5000Array::get_filtered_raw() const {
    return filtered_raw_;
}

const std::vector<SensorCalibration>& TCRT5000Array::get_calibration() const {
    return calibration_;
}
