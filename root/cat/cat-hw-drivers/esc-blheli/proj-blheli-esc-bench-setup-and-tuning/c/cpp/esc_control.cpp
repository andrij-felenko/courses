#include "esc_control.hpp"
#include <iostream>

namespace esc {

namespace {
// Емуляція регістрів таймера та АЦП для низькорівневого контролю
struct HardwareTimer {
    uint32_t prescaler{71};
    uint32_t auto_reload{19999};
    uint32_t compare_channel1{1000};
    bool enabled{false};
};

struct HardwareAdc {
    bool enabled{false};
};

HardwareTimer g_timer{};
HardwareAdc g_adc{};
} // namespace

void EscController::initHardwarePeripherals() {
    // Налаштування преддільника для отримання тактування 1 МГц (1 мкс на відлік)
    g_timer.prescaler = 71;
    g_timer.auto_reload = kPwmPeriodUs - 1;
    g_timer.compare_channel1 = kMinPulseUs;
    g_timer.enabled = true;

    // Увімкнення модуля АЦП
    g_adc.enabled = true;
}

void EscController::writePwmHardware(uint16_t pulse_us) {
    g_timer.compare_channel1 = pulse_us;
}

void EscController::init() {
    initHardwarePeripherals();
    
    // Армування ESC: видача початкового мінімального сигналу (1000 мкс)
    current_pulse_us_ = kMinPulseUs;
    writePwmHardware(kMinPulseUs);
    
    bec_voltage_ = kBecNominalVolts;
    status_ = BecStatus::Ok;
    emergency_stop_ = false;
    is_armed_ = true;
}

bool EscController::setThrottle(uint16_t pulse_us) {
    if (!is_armed_) {
        return false;
    }

    if (emergency_stop_) {
        // Якщо спрацював аварійний захист від просідання живлення BEC,
        // скидаємо газ до 0% та блокуємо зміну обертів
        current_pulse_us_ = kMinPulseUs;
        writePwmHardware(kMinPulseUs);
        return false;
    }

    // Обмеження діапазону імпульсу в межах 1000..2000 мкс
    current_pulse_us_ = std::clamp(pulse_us, kMinPulseUs, kMaxPulseUs);
    writePwmHardware(current_pulse_us_);
    return true;
}

BecStatus EscController::updateBecMonitoring(uint16_t raw_adc) {
    bec_voltage_ = convertAdcToVoltage(raw_adc);

    if (bec_voltage_ < kBecCritVolts) {
        status_ = BecStatus::Critical;
        emergency_stop_ = true; // Тригер аварійного зупину двигуна
    } else if (bec_voltage_ < kBecWarnVolts) {
        status_ = BecStatus::Warning;
    } else {
        status_ = BecStatus::Ok;
    }

    return status_;
}

void EscController::process(uint16_t raw_adc, uint16_t target_pulse_us) {
    updateBecMonitoring(raw_adc);
    setThrottle(target_pulse_us);
}

std::string_view EscController::statusToString(BecStatus status) noexcept {
    switch (status) {
        case BecStatus::Ok: return "НОРМА";
        case BecStatus::Warning: return "ПОПЕРЕДЖЕННЯ";
        case BecStatus::Critical: return "КРИТИЧНО";
    }
    return "НЕВІДОМО";
}

} // namespace esc
