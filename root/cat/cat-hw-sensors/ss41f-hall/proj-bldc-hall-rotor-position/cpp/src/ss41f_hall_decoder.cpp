#include "ss41f_hall_decoder.hpp"

namespace bldc {

Ss41fHallDecoder::Ss41fHallDecoder(uint8_t pole_pairs)
    : pole_pairs_(pole_pairs > 0 ? pole_pairs : 1) {
    reset();
}

void Ss41fHallDecoder::reset() {
    telemetry_ = RotorTelemetry{};
    dt_buffer_.clear();
}

RotorSector Ss41fHallDecoder::decode_sector(uint8_t raw_hall_code) const noexcept {
    // В 120-градусній розміщеній системі датчиків SS41F з 8 комбінацій станів 
    // 0b000 та 0b111 є фізично недопустимими (помилка підключення/давача).
    switch (raw_hall_code & 0x07) {
        case static_cast<uint8_t>(HallState::S1_101): return RotorSector::Sector1; // 0b101 (5)
        case static_cast<uint8_t>(HallState::S2_100): return RotorSector::Sector2; // 0b100 (4)
        case static_cast<uint8_t>(HallState::S3_110): return RotorSector::Sector3; // 0b110 (6)
        case static_cast<uint8_t>(HallState::S4_010): return RotorSector::Sector4; // 0b010 (2)
        case static_cast<uint8_t>(HallState::S5_011): return RotorSector::Sector5; // 0b011 (3)
        case static_cast<uint8_t>(HallState::S6_001): return RotorSector::Sector6; // 0b001 (1)
        default: return RotorSector::Unknown;
    }
}

bool Ss41fHallDecoder::validate_transition(RotorSector prev, RotorSector curr, RotationDirection& out_dir) const noexcept {
    if (curr == RotorSector::Unknown) {
        out_dir = RotationDirection::Unknown;
        return false;
    }

    if (prev == RotorSector::Unknown) {
        // Перше отримане значення після ініціалізації або скидання
        out_dir = RotationDirection::Unknown;
        return true;
    }

    const auto p = static_cast<uint8_t>(prev);
    const auto c = static_cast<uint8_t>(curr);

    // Пряме обертання (Forward): 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 1
    const uint8_t expected_forward = (p % 6) + 1;
    if (c == expected_forward) {
        out_dir = RotationDirection::Forward;
        return true;
    }

    // Зворотне обертання (Reverse): 1 -> 6 -> 5 -> 4 -> 3 -> 2 -> 1
    const uint8_t expected_reverse = (c % 6) + 1;
    if (p == expected_reverse) {
        out_dir = RotationDirection::Reverse;
        return true;
    }

    out_dir = RotationDirection::Unknown;
    return false;
}

uint32_t Ss41fHallDecoder::calculate_rpm(uint32_t delta_us) noexcept {
    if (delta_us == 0) {
        return telemetry_.speed_rpm;
    }

    dt_buffer_.push(delta_us);

    const uint32_t dt_sum = dt_buffer_.sum();
    const std::size_t k = dt_buffer_.size();

    if (dt_sum == 0 || k == 0) {
        return 0;
    }

    // Формула розрахунку RPM без плаваючої крапки:
    // 1 механічний оберт = P електричних обертів = 6 * P переключень секторів.
    // RPM = 60 * 10^6 / (6 * P * delta_t_avg) = 10^7 / (P * delta_t_avg)
    // Оскільки delta_t_avg = dt_sum / k, маємо:
    // RPM = (10^7 * k) / (P * dt_sum)
    const uint64_t numerator = 10000000ULL * static_cast<uint64_t>(k);
    const uint64_t denominator = static_cast<uint64_t>(pole_pairs_) * static_cast<uint64_t>(dt_sum);

    if (denominator == 0) {
        return 0;
    }

    return static_cast<uint32_t>(numerator / denominator);
}

void Ss41fHallDecoder::process_hall_change(uint8_t raw_hall_code, uint32_t timestamp_us) {
    const RotorSector new_sector = decode_sector(raw_hall_code);

    // 1. Перевірка на некоректні 3-бітні стани (0b000 або 0b111)
    if (new_sector == RotorSector::Unknown) {
        telemetry_.last_error = DecoderError::InvalidHallState;
        telemetry_.error_count++;
        if (error_cb_) {
            error_cb_(DecoderError::InvalidHallState, raw_hall_code);
        }
        return;
    }

    // 2. Перевірка коректності фазового переходу
    RotationDirection new_dir = RotationDirection::Unknown;
    const bool valid = validate_transition(telemetry_.current_sector, new_sector, new_dir);

    if (!valid) {
        telemetry_.last_error = DecoderError::IllegalStateTransition;
        telemetry_.error_count++;
        if (error_cb_) {
            error_cb_(DecoderError::IllegalStateTransition, raw_hall_code);
        }
        return;
    }

    // 3. Обчислення часового інтервалу та кутової швидкості
    if (telemetry_.last_transition_us > 0 && timestamp_us > telemetry_.last_transition_us) {
        const uint32_t dt = timestamp_us - telemetry_.last_transition_us;
        telemetry_.speed_rpm = calculate_rpm(dt);
    }

    // 4. Оновлення телеметрії ротора
    telemetry_.previous_sector = telemetry_.current_sector;
    telemetry_.current_sector = new_sector;
    if (new_dir != RotationDirection::Unknown) {
        telemetry_.direction = new_dir;
    }
    telemetry_.last_transition_us = timestamp_us;
    telemetry_.state_change_count++;
    telemetry_.last_error = DecoderError::None;

    // 5. Виклик користувацького callback-обробника
    if (sector_cb_) {
        sector_cb_(telemetry_);
    }
}

void Ss41fHallDecoder::check_timeout(uint32_t current_timestamp_us, uint32_t timeout_us) {
    if (telemetry_.last_transition_us > 0 && current_timestamp_us > telemetry_.last_transition_us) {
        const uint32_t elapsed = current_timestamp_us - telemetry_.last_transition_us;
        if (elapsed >= timeout_us) {
            telemetry_.speed_rpm = 0;
            if (telemetry_.last_error == DecoderError::None) {
                telemetry_.last_error = DecoderError::SensorTimeout;
                if (error_cb_) {
                    error_cb_(DecoderError::SensorTimeout, 0);
                }
            }
        }
    }
}

} // namespace bldc
