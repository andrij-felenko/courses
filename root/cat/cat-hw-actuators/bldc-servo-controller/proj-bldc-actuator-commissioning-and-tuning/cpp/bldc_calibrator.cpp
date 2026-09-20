#include "bldc_calibrator.hpp"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace bldc_servo {

// =============================================================================
// Реалізація CalibrationStorage
// =============================================================================

uint32_t CalibrationStorage::calculate_crc32(const uint8_t* data, size_t length) noexcept {
    // Стандартний поліном IEEE 802.3: 0xEDB88320 (у дзеркальному бітовому представленні)
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; ++i) {
        crc ^= static_cast<uint32_t>(data[i]);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 1U) {
                crc = (crc >> 1U) ^ 0xEDB88320U;
            } else {
                crc >>= 1U;
            }
        }
    }
    return ~crc;
}

bool CalibrationStorage::validate(const CalibrationData& data) noexcept {
    // Перевірка сигнатури магічного заголовка "BLDC"
    if (data.magic != 0x43444C42) {
        return false;
    }

    // Перевірка версії бінарної структури
    if (data.version != 1) {
        return false;
    }

    // Перевірка допустимості кількості пар полюсів двигуна
    if (data.pole_pairs == 0 || data.pole_pairs > 64) {
        return false;
    }

    // Перевірка діапазону зміщення нуля енкодера
    const float two_pi = 2.0f * static_cast<float>(M_PI);
    if (data.zero_offset_rad < -two_pi || data.zero_offset_rad > two_pi) {
        return false;
    }

    // Перевірка цілісності корисного навантаження за CRC32
    constexpr size_t payload_size = offsetof(CalibrationData, crc32);
    const uint32_t calculated = calculate_crc32(reinterpret_cast<const uint8_t*>(&data), payload_size);

    return calculated == data.crc32;
}

bool CalibrationStorage::save(const CalibrationData& data) noexcept {
    CalibrationData to_write = data;

    // Розрахунок та вставка контрольної суми в кінець структури
    constexpr size_t payload_size = offsetof(CalibrationData, crc32);
    to_write.crc32 = calculate_crc32(reinterpret_cast<const uint8_t*>(&to_write), payload_size);

    // Запис бінарного блоку в енергонезалежну пам'ять
    const bool write_ok = memory_.write(base_address_,
                                        reinterpret_cast<const uint8_t*>(&to_write),
                                        sizeof(CalibrationData));
    if (!write_ok) {
        return false;
    }

    // Обов'язкова верифікація зворотним читанням для виключення бітових помилок пам'яті
    CalibrationData readback{};
    const bool read_ok = memory_.read(base_address_,
                                      reinterpret_cast<uint8_t*>(&readback),
                                      sizeof(CalibrationData));
    if (!read_ok) {
        return false;
    }

    return validate(readback);
}

bool CalibrationStorage::load(CalibrationData& out_data) const noexcept {
    const bool read_ok = memory_.read(base_address_,
                                      reinterpret_cast<uint8_t*>(&out_data),
                                      sizeof(CalibrationData));
    if (!read_ok) {
        return false;
    }

    return validate(out_data);
}

// =============================================================================
// Реалізація CascadeController
// =============================================================================

float CascadeController::update(float target_pos_rad, float actual_pos_rad, float dt_seconds) noexcept {
    if (dt_seconds <= 1e-6f) {
        return 0.0f;
    }

    // 1. Оцінка швидкості обертання: чисельне диференціювання з фільтрацією низьких частот
    if (is_first_update_) {
        actual_vel_rad_s_ = 0.0f;
        is_first_update_ = false;
    } else {
        const float raw_velocity = (actual_pos_rad - last_pos_rad_) / dt_seconds;
        // Фільтр ковзного експоненційного згладжування для придушення шуму енкодера
        actual_vel_rad_s_ = 0.65f * actual_vel_rad_s_ + 0.35f * raw_velocity;
    }
    last_pos_rad_ = actual_pos_rad;

    // 2. Зовнішній контур: регулювання положення -> генерація цільової кутової швидкості
    const float pos_error = target_pos_rad - actual_pos_rad;
    pos_integral_ += gains_.pos_ki * pos_error * dt_seconds;
    pos_integral_ = std::clamp(pos_integral_, -gains_.max_velocity_rad_s, gains_.max_velocity_rad_s);

    const float raw_target_vel = (gains_.pos_kp * pos_error) + pos_integral_;
    target_vel_rad_s_ = std::clamp(raw_target_vel, -gains_.max_velocity_rad_s, gains_.max_velocity_rad_s);

    // 3. Внутрішній контур: регулювання швидкості -> розрахунок струму моменту Iq
    const float vel_error = target_vel_rad_s_ - actual_vel_rad_s_;
    const float prop_term = gains_.vel_kp * vel_error;

    // Захист від інтегрального насичення Anti-Windup (умовне інтегрування з clamping)
    const float candidate_integral = vel_integral_ + (gains_.vel_ki * vel_error * dt_seconds);
    const float candidate_iq = prop_term + candidate_integral;

    float output_iq = candidate_iq;
    if (candidate_iq > gains_.max_current_amps) {
        output_iq = gains_.max_current_amps;
        // Дозволяємо інтегрування тільки у разі дії помилки на вихід із насичення
        if (vel_error < 0.0f) {
            vel_integral_ = candidate_integral;
        }
    } else if (candidate_iq < -gains_.max_current_amps) {
        output_iq = -gains_.max_current_amps;
        if (vel_error > 0.0f) {
            vel_integral_ = candidate_integral;
        }
    } else {
        vel_integral_ = candidate_integral;
    }

    return output_iq;
}

void CascadeController::tune_for_load(float inertia_kg_m2, float target_bw_rad_s, float kt_nm_a) noexcept {
    if (inertia_kg_m2 <= 1e-7f || target_bw_rad_s <= 1.0f || kt_nm_a <= 1e-4f) {
        return;
    }

    // Аналітичний розрахунок за інженерним методом симетричного оптимуму:
    // Контур швидкості:
    // Kp_vel = (J * w_bw) / Kt
    // Ki_vel = Kp_vel * (w_bw / 4)
    const float kp_vel = (inertia_kg_m2 * target_bw_rad_s) / kt_nm_a;
    const float ki_vel = kp_vel * (target_bw_rad_s * 0.25f);

    // Зовнішній контур положення:
    // Смуга пропускання обирається у 4 рази нижчою для уникнення взаємного збурення контурів
    const float kp_pos = target_bw_rad_s * 0.25f;
    const float ki_pos = 0.0f; // Статична похибка позиції компенсується інтегратором швидкості

    gains_.pos_kp = kp_pos;
    gains_.pos_ki = ki_pos;
    gains_.vel_kp = kp_vel;
    gains_.vel_ki = ki_vel;
}

void CascadeController::reset() noexcept {
    pos_integral_ = 0.0f;
    vel_integral_ = 0.0f;
    last_pos_rad_ = 0.0f;
    target_vel_rad_s_ = 0.0f;
    actual_vel_rad_s_ = 0.0f;
    is_first_update_ = true;
}

// =============================================================================
// Реалізація BldcCalibrator
// =============================================================================

BldcCalibrator::BldcCalibrator(IInverter& inverter,
                               IEncoder& encoder,
                               CascadeController& controller,
                               CalibrationStorage& storage,
                               uint16_t pole_pairs,
                               float motor_kt_nm_a) noexcept
    : inverter_(inverter),
      encoder_(encoder),
      controller_(controller),
      storage_(storage),
      pole_pairs_(pole_pairs),
      motor_kt_nm_a_(motor_kt_nm_a) {}

void BldcCalibrator::start_calibration(float step_magnitude_rad) noexcept {
    if (state_ != CalibrationState::Idle && state_ != CalibrationState::Completed && state_ != CalibrationState::Fault) {
        return;
    }

    step_magnitude_rad_ = (step_magnitude_rad < 0.1f) ? 0.5f : step_magnitude_rad;
    last_error_ = CalibrationError::None;
    telemetry_count_ = 0;
    step_metrics_ = StepMetrics{};
    controller_.reset();

    transition_to(CalibrationState::AligningPhases, 0);
}

void BldcCalibrator::abort() noexcept {
    inverter_.disable();
    state_ = CalibrationState::Idle;
    last_error_ = CalibrationError::None;
}

void BldcCalibrator::reset() noexcept {
    abort();
}

const char* BldcCalibrator::state_name() const noexcept {
    switch (state_) {
        case CalibrationState::Idle:              return "Очікування (Idle)";
        case CalibrationState::AligningPhases:     return "Вирівнювання фаз (AligningPhases)";
        case CalibrationState::DetectingZero:      return "Визначення нуля (DetectingZero)";
        case CalibrationState::TuningGains:        return "Синтез регуляторів (TuningGains)";
        case CalibrationState::RunningStepTest:    return "Тестовий стрибок (RunningStepTest)";
        case CalibrationState::EvaluatingMetrics:  return "Оцінка перехідного процесу (EvaluatingMetrics)";
        case CalibrationState::SavingCalibration:  return "Збереження у EEPROM (SavingCalibration)";
        case CalibrationState::Completed:          return "Калібрування завершено (Completed)";
        case CalibrationState::Fault:              return "Аварія калібрування (Fault)";
        default:                                   return "Невідомий стан";
    }
}

const char* BldcCalibrator::error_name() const noexcept {
    switch (last_error_) {
        case CalibrationError::None:                  return "Помилок немає";
        case CalibrationError::InverterHardwareFault: return "Апаратний збій інвертора";
        case CalibrationError::EncoderHardwareFault:  return "Збій або неготовність енкодера";
        case CalibrationError::RotorMotionTimeout:    return "Таймаут механічного заспокоєння ротора";
        case CalibrationError::StepResponseUnstable:  return "Нестійкий перехідний процес тестового кроку";
        case CalibrationError::StorageWriteFailed:    return "Помилка запису в енергонезалежну пам'ять";
        case CalibrationError::StorageCrcMismatch:    return "Невідповідність контрольної суми CRC32";
        default:                                      return "Невідома помилка";
    }
}

void BldcCalibrator::transition_to(CalibrationState new_state, uint32_t now_ms) noexcept {
    state_ = new_state;
    state_start_time_ms_ = now_ms;
    last_step_time_ms_ = now_ms;
}

void BldcCalibrator::fail(CalibrationError error) noexcept {
    last_error_ = error;
    state_ = CalibrationState::Fault;
    inverter_.disable();
}

void BldcCalibrator::step(uint32_t current_time_ms) noexcept {
    if (inverter_.is_fault()) {
        fail(CalibrationError::InverterHardwareFault);
        return;
    }

    if (!encoder_.is_ready() && state_ != CalibrationState::Idle && state_ != CalibrationState::Completed) {
        fail(CalibrationError::EncoderHardwareFault);
        return;
    }

    switch (state_) {
        case CalibrationState::Idle:
            break;

        case CalibrationState::AligningPhases:
            process_aligning_phases(current_time_ms);
            break;

        case CalibrationState::DetectingZero:
            process_detecting_zero();
            break;

        case CalibrationState::TuningGains:
            process_tuning_gains();
            break;

        case CalibrationState::RunningStepTest:
            process_running_step(current_time_ms);
            break;

        case CalibrationState::EvaluatingMetrics:
            process_evaluating_metrics();
            break;

        case CalibrationState::SavingCalibration:
            process_saving_calibration();
            break;

        case CalibrationState::Completed:
        case CalibrationState::Fault:
            break;
    }
}

void BldcCalibrator::process_aligning_phases(uint32_t now_ms) noexcept {
    // Вмикаємо інвертор та прикладаємо постійний вектор струму прямої осі Id
    inverter_.enable();
    inverter_.apply_id_vector(align_current_amps_);

    // Час очікування заспокоєння коливань ротора в положенні фази A (300 мс)
    constexpr uint32_t kAlignDurationMs = 300;
    if (now_ms - state_start_time_ms_ >= kAlignDurationMs) {
        transition_to(CalibrationState::DetectingZero, now_ms);
    }
}

void BldcCalibrator::process_detecting_zero() noexcept {
    // Зчитуємо стаціонарне механічне положення ротора, зафіксованого вектором Id
    const float raw_angle = encoder_.read_mechanical_angle_rad();
    const float two_pi = 2.0f * static_cast<float>(M_PI);

    // Нормалізація зміщення в діапазон [0..2*PI)
    float offset = std::fmod(raw_angle, two_pi);
    if (offset < 0.0f) {
        offset += two_pi;
    }
    zero_offset_rad_ = offset;

    // Знімаємо струм вирівнювання перед переходом до керування
    inverter_.apply_id_vector(0.0f);

    transition_to(CalibrationState::TuningGains, state_start_time_ms_);
}

void BldcCalibrator::process_tuning_gains() noexcept {
    // Автоматичне підстроювання коефіцієнтів під розрахункову динаміку навантаження
    // Типовий привідний вузол: ротор + маховик J = 0.00045 кг*м^2, смуга контуру швидкості 45 рад/с
    constexpr float kEstimatedInertia = 0.00045f;
    constexpr float kTargetBandwidth = 45.0f;

    controller_.tune_for_load(kEstimatedInertia, kTargetBandwidth, motor_kt_nm_a_);
    controller_.reset();

    // Фіксація точки початку тесту для формування стрибка завдання
    test_start_pos_rad_ = encoder_.read_mechanical_angle_rad();
    telemetry_count_ = 0;

    transition_to(CalibrationState::RunningStepTest, state_start_time_ms_);
}

void BldcCalibrator::process_running_step(uint32_t now_ms) noexcept {
    constexpr uint32_t kStepDurationMs = 400; // Тривалість спостереження перехідного процесу (мс)
    constexpr uint32_t kSampleIntervalMs = 5; // Квант запису телеметрії (200 Гц)

    const uint32_t elapsed_ms = now_ms - state_start_time_ms_;
    const float dt = static_cast<float>(now_ms - last_step_time_ms_) * 0.001f;
    last_step_time_ms_ = now_ms;

    const float target_pos = test_start_pos_rad_ + step_magnitude_rad_;
    const float actual_pos = encoder_.read_mechanical_angle_rad();

    // Обчислення миттєвого електричного кута з урахуванням знайденого калібрувального зміщення
    const float two_pi = 2.0f * static_cast<float>(M_PI);
    float elec_angle = std::fmod((actual_pos - zero_offset_rad_) * static_cast<float>(pole_pairs_), two_pi);
    if (elec_angle < 0.0f) {
        elec_angle += two_pi;
    }

    // Обчислення керуючого впливу каскадним ПІ-регулятором
    const float safe_dt = (dt > 1e-4f && dt < 0.1f) ? dt : 0.005f;
    const float iq_cmd = controller_.update(target_pos, actual_pos, safe_dt);

    // Застосування квадратурного струму моменту інвертором
    inverter_.apply_torque_current(iq_cmd, elec_angle);

    // Запис точки відгуку у фіксований буфер без динамічного виділення пам'яті
    if (telemetry_count_ < kMaxTelemetryPoints &&
        (telemetry_count_ == 0 || elapsed_ms >= telemetry_count_ * kSampleIntervalMs)) {
        TelemetryPoint pt;
        pt.timestamp_ms = elapsed_ms;
        pt.target_pos_rad = target_pos;
        pt.actual_pos_rad = actual_pos;
        pt.target_vel_rad_s = controller_.target_velocity();
        pt.actual_vel_rad_s = controller_.actual_velocity();
        pt.current_iq_amps = iq_cmd;
        telemetry_buffer_[telemetry_count_++] = pt;
    }

    if (elapsed_ms >= kStepDurationMs) {
        transition_to(CalibrationState::EvaluatingMetrics, now_ms);
    }
}

void BldcCalibrator::process_evaluating_metrics() noexcept {
    if (telemetry_count_ < 5) {
        fail(CalibrationError::StepResponseUnstable);
        return;
    }

    const float target_pos = test_start_pos_rad_ + step_magnitude_rad_;
    const float initial_pos = test_start_pos_rad_;
    const float step_amplitude = std::abs(step_magnitude_rad_);

    float max_pos = initial_pos;
    float rise_time_ms = 0.0f;
    float settling_time_ms = 0.0f;
    bool reached_10pct = false;
    uint32_t t_10pct = 0;

    const float val_10pct = initial_pos + 0.10f * (target_pos - initial_pos);
    const float val_90pct = initial_pos + 0.90f * (target_pos - initial_pos);
    const float tolerance = 0.05f * step_amplitude; // Допустима зона встановлення +-5%

    for (size_t i = 0; i < telemetry_count_; ++i) {
        const auto& pt = telemetry_buffer_[i];
        if (pt.actual_pos_rad > max_pos) {
            max_pos = pt.actual_pos_rad;
        }

        // Фіксація часу наростання фронту перехідної характеристики
        if (!reached_10pct && pt.actual_pos_rad >= val_10pct) {
            reached_10pct = true;
            t_10pct = pt.timestamp_ms;
        }
        if (reached_10pct && rise_time_ms == 0.0f && pt.actual_pos_rad >= val_90pct) {
            rise_time_ms = static_cast<float>(pt.timestamp_ms - t_10pct);
        }
    }

    // Визначення моменту останнього виходу за межі трубки допуску +-5%
    for (size_t i = telemetry_count_; i > 0; --i) {
        const auto& pt = telemetry_buffer_[i - 1];
        if (std::abs(pt.actual_pos_rad - target_pos) > tolerance) {
            settling_time_ms = static_cast<float>(pt.timestamp_ms);
            break;
        }
    }

    // Розрахунок відсотка динамічного перерегулювання
    const float overshoot_rad = std::max(0.0f, max_pos - target_pos);
    const float overshoot_pct = (overshoot_rad / step_amplitude) * 100.0f;

    // Усталена статична похибка в стаціонарній точці
    const float final_pos = telemetry_buffer_[telemetry_count_ - 1].actual_pos_rad;
    const float steady_error = std::abs(target_pos - final_pos);

    step_metrics_.rise_time_ms = rise_time_ms;
    step_metrics_.settling_time_ms = settling_time_ms;
    step_metrics_.overshoot_percent = overshoot_pct;
    step_metrics_.steady_state_error_rad = steady_error;

    // Критерії стійкості: перерегулювання <= 30%, похибка в межах допуску
    step_metrics_.is_stable = (overshoot_pct <= 30.0f) && (steady_error <= tolerance * 1.5f);

    if (!step_metrics_.is_stable) {
        fail(CalibrationError::StepResponseUnstable);
        return;
    }

    transition_to(CalibrationState::SavingCalibration, state_start_time_ms_);
}

void BldcCalibrator::process_saving_calibration() noexcept {
    CalibrationData data{};
    data.magic = 0x43444C42;
    data.version = 1;
    data.pole_pairs = pole_pairs_;
    data.zero_offset_rad = zero_offset_rad_;
    data.pos_kp = controller_.gains().pos_kp;
    data.pos_ki = controller_.gains().pos_ki;
    data.vel_kp = controller_.gains().vel_kp;
    data.vel_ki = controller_.gains().vel_ki;

    const bool saved = storage_.save(data);
    if (!saved) {
        fail(CalibrationError::StorageWriteFailed);
        return;
    }

    // Додаткова перевірка прочитаних даних на відповідність збереженому зміщенню
    CalibrationData verified{};
    if (!storage_.load(verified) || verified.zero_offset_rad != zero_offset_rad_) {
        fail(CalibrationError::StorageCrcMismatch);
        return;
    }

    // Успішне завершення циклу автоналагодження
    state_ = CalibrationState::Completed;
}

} // namespace bldc_servo
