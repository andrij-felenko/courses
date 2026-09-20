#include "MosfetSwitch.hpp"
#include <algorithm>
#include <cmath>

namespace hardware {

MosfetSwitch::MosfetSwitch(MosfetModel model, const PinConfig& pinCfg, const PwmConfig& pwmCfg)
    : m_model(model),
      m_pinCfg(pinCfg),
      m_pwmCfg(pwmCfg),
      m_specs(lookupSpecs(model)) {
}

MosfetSpecs MosfetSwitch::lookupSpecs(MosfetModel model) {
    MosfetSpecs specs;
    switch (model) {
        case MosfetModel::IRLZ44N:
            specs.maxVoltageV = 55.0f;
            specs.maxCurrentA = 47.0f;
            specs.rdsOnOhmsAt3v3 = 0.035f;
            specs.rdsOnOhmsAt5v0 = 0.028f;
            specs.gateChargeNnC = 63.0f;
            specs.maxPowerDissipationW = 2.5f; // Без додаткового радіатора при T_amb=25°C
            break;
        case MosfetModel::IRL540N:
            specs.maxVoltageV = 100.0f;
            specs.maxCurrentA = 30.0f;
            specs.rdsOnOhmsAt3v3 = 0.063f;
            specs.rdsOnOhmsAt5v0 = 0.044f;
            specs.gateChargeNnC = 74.0f;
            specs.maxPowerDissipationW = 2.0f;
            break;
        case MosfetModel::IRL2203N:
            specs.maxVoltageV = 30.0f;
            specs.maxCurrentA = 116.0f;
            specs.rdsOnOhmsAt3v3 = 0.010f;
            specs.rdsOnOhmsAt5v0 = 0.007f;
            specs.gateChargeNnC = 60.0f;
            specs.maxPowerDissipationW = 3.0f;
            break;
        case MosfetModel::FDD8447L:
            specs.maxVoltageV = 40.0f;
            specs.maxCurrentA = 50.0f;
            specs.rdsOnOhmsAt3v3 = 0.013f;
            specs.rdsOnOhmsAt5v0 = 0.0105f;
            specs.gateChargeNnC = 38.0f;
            specs.maxPowerDissipationW = 2.8f;
            break;
        case MosfetModel::Custom:
            specs.maxVoltageV = 30.0f;
            specs.maxCurrentA = 20.0f;
            specs.rdsOnOhmsAt3v3 = 0.050f;
            specs.rdsOnOhmsAt5v0 = 0.040f;
            specs.gateChargeNnC = 30.0f;
            specs.maxPowerDissipationW = 2.0f;
            break;
    }
    return specs;
}

bool MosfetSwitch::initialize() {
    // 1. Перевірка базової конфігурації
    if (m_pwmCfg.maxDutyPercent < m_pwmCfg.minDutyPercent || m_pwmCfg.maxSafeDutyPercent > 100.0f) {
        m_lastFault = SwitchFault::InvalidConfiguration;
        m_mode = ControlMode::FaultState;
        return false;
    }

    // 2. Гарантування безпечного стану pull-down затвора при старті МК.
    // Під час подачі живлення або скидання МК виводи GPIO перебувають у стані високого опору (Hi-Z).
    // Зовнішній або внутрішній резистор pull-down (наприклад, 10 кОм) на затворі стікає заряд ємності C_iss на GND,
    // запобігаючи довільному відкриванню транзистора IRLZ44N/FDD8447L та спаленню навантаження.
    m_currentDutyPercent = 0.0f;
    m_isEnabled = false;
    m_mode = ControlMode::Disabled;
    m_lastFault = SwitchFault::None;

    applyHardwarePinState(false);

    m_initialized = true;
    return true;
}

bool MosfetSwitch::turnOn() {
    if (!m_initialized) {
        m_lastFault = SwitchFault::NotInitialized;
        return false;
    }

    if (m_mode == ControlMode::FaultState) {
        return false;
    }

    // Повне ввімкнення ключа (дискретний режим GPIO)
    m_mode = ControlMode::DiscreteGpio;
    m_currentDutyPercent = 100.0f;
    m_isEnabled = true;
    m_switchCounter++;

    applyHardwarePinState(true);
    return true;
}

void MosfetSwitch::turnOff() {
    if (m_mode == ControlMode::FaultState) {
        return;
    }

    m_currentDutyPercent = 0.0f;
    m_isEnabled = false;
    m_mode = ControlMode::Disabled;

    applyHardwarePinState(false);
}

bool MosfetSwitch::setDutyCycle(float dutyPercent) {
    if (!m_initialized) {
        m_lastFault = SwitchFault::NotInitialized;
        return false;
    }

    if (m_mode == ControlMode::FaultState) {
        return false;
    }

    if (!m_pinCfg.isPwmSupported) {
        m_lastFault = SwitchFault::InvalidConfiguration;
        return false;
    }

    // Перевірка суворого обмеження безпечного робочого циклу
    if (dutyPercent > m_pwmCfg.maxDutyPercent) {
        m_lastFault = SwitchFault::DutyCycleExceeded;
        emergencyShutdown(SwitchFault::DutyCycleExceeded);
        return false;
    }

    // Обмеження значення безпечним верхнім лімітом maxSafeDutyPercent
    float clampedDuty = std::clamp(dutyPercent, m_pwmCfg.minDutyPercent, m_pwmCfg.maxSafeDutyPercent);

    if (clampedDuty <= 0.001f) {
        turnOff();
        return true;
    }

    m_mode = ControlMode::HardwarePwm;
    m_currentDutyPercent = clampedDuty;
    m_isEnabled = true;

    applyHardwarePwmDuty(clampedDuty);
    return true;
}

bool MosfetSwitch::smoothRampTo(float targetDutyPercent, uint32_t stepDelayMs) {
    if (!m_initialized || m_mode == ControlMode::FaultState) {
        return false;
    }

    float clampedTarget = std::clamp(targetDutyPercent, m_pwmCfg.minDutyPercent, m_pwmCfg.maxSafeDutyPercent);
    float step = m_pwmCfg.rampStepPercent;

    if (m_currentDutyPercent < clampedTarget) {
        // Плавне наростання (Ramp Up)
        while (m_currentDutyPercent < clampedTarget) {
            float nextDuty = std::min(m_currentDutyPercent + step, clampedTarget);
            if (!setDutyCycle(nextDuty)) {
                return false;
            }
            // Симуляція затримки мікроконтролера між кроками ШІМ
            (void)stepDelayMs;
        }
    } else if (m_currentDutyPercent > clampedTarget) {
        // Плавне спадання (Ramp Down)
        while (m_currentDutyPercent > clampedTarget) {
            float nextDuty = std::max(m_currentDutyPercent - step, clampedTarget);
            if (!setDutyCycle(nextDuty)) {
                return false;
            }
            (void)stepDelayMs;
        }
    }

    return true;
}

void MosfetSwitch::emergencyShutdown(SwitchFault reason) {
    // Аварійне відключення виконується негайно
    m_isEnabled = false;
    m_currentDutyPercent = 0.0f;
    m_mode = ControlMode::FaultState;
    m_lastFault = reason;

    // Апаратно притискаємо затвор до землі та вимикаємо генератор ШІМ
    applyHardwarePinState(false);
}

bool MosfetSwitch::clearFault() {
    if (m_mode != ControlMode::FaultState) {
        return true;
    }

    // Скидання стану помилки дозволено лише після безпечного знеструмлення
    m_lastFault = SwitchFault::None;
    m_mode = ControlMode::Disabled;
    m_currentDutyPercent = 0.0f;
    m_isEnabled = false;

    applyHardwarePinState(false);
    return true;
}

void MosfetSwitch::updateLoadEstimates(float loadCurrentA, float gateVoltageV) {
    m_estimatedCurrentA = loadCurrentA;

    if (!m_isEnabled || m_currentDutyPercent <= 0.001f) {
        m_estimatedPowerLossW = 0.0f;
        return;
    }

    // Оцінка опору відкритого каналу R_DS(on) залежно від напруги керування V_GS (3.3В чи 5В).
    // Для транзисторів логічного рівня (Logic-Level):
    // При V_GS = 5.0 В канал повністю відкритий (мінімальний R_DS(on)).
    // При V_GS = 3.3 В канал також відкритий, але R_DS(on) може бути на 20-30% вищим.
    float rdsOn = (gateVoltageV >= 4.5f) ? m_specs.rdsOnOhmsAt5v0 : m_specs.rdsOnOhmsAt3v3;

    // Статичні втрати на провідність P_conduct = I_D^2 * R_DS(on) * (DutyCycle / 100)
    float conductionLoss = (loadCurrentA * loadCurrentA) * rdsOn * (m_currentDutyPercent / 100.0f);

    // Оцінка динамічних втрат на перемикання P_switch (через перезаряд ємності затвора C_iss при ШІМ)
    // P_switch ≈ V_DS * I_D * f_PWM * t_sw, де t_sw залежить від заряду затвора Q_g та обмежувального резистора R_G
    float switchingTimeSec = (m_specs.gateChargeNnC * 1e-9f) / (gateVoltageV / static_cast<float>(m_pinCfg.gateResistorOhms));
    float switchingLoss = m_specs.maxVoltageV * loadCurrentA * static_cast<float>(m_pwmCfg.frequencyHz) * switchingTimeSec;

    m_estimatedPowerLossW = conductionLoss + switchingLoss;

    // Перевірка теплового ліміту корпусу без додаткового радіатора
    if (m_estimatedPowerLossW > m_specs.maxPowerDissipationW) {
        emergencyShutdown(SwitchFault::ThermalLimitReached);
    }
}

SwitchMetrics MosfetSwitch::getMetrics() const {
    SwitchMetrics metrics;
    metrics.currentDutyCyclePercent = m_currentDutyPercent;
    metrics.estimatedCurrentAmpere = m_estimatedCurrentA;
    metrics.estimatedPowerLossWatts = m_estimatedPowerLossW;
    metrics.switchCounter = m_switchCounter;
    metrics.mode = m_mode;
    metrics.lastFault = m_lastFault;
    metrics.isEnabled = m_isEnabled;
    return metrics;
}

void MosfetSwitch::applyHardwarePinState(bool state) {
    // В апаратній реалізації для мікроконтролерів (STM32, ESP32, AVR):
    // 1. При state == false: вивід переводиться у режим GPIO Output LOW.
    // 2. Якщо підключено апаратний ШІМ, канал таймера деактивується.
    // 3. Резистор R_G (наприклад, 100 Ом) між виводом МК та затвором обмежує піковий струм перезаряду C_iss
    //    до I_gate_peak = V_MCU / R_G = 3.3V / 100 Ohm = 33 mA (безпечно для виводу GPIO МК).
    // 4. Паралельний діод зворотного ходу (Flyback / Freewheeling Diode) 1N4007 / SS34 поперек індуктивного навантаження
    //    (мотор, реле, соленоїд) гасить індуктивний викид високої напруги -L*di/dt під час розмикання ключа.
    (void)state;
}

void MosfetSwitch::applyHardwarePwmDuty(float dutyPercent) {
    // В апаратній реалізації для мікроконтролерів:
    // Перераховуємо відсоток у регістр порівняння таймера (TIMx->CCRx або analogWrite).
    // Наприклад: uint32_t compareValue = (dutyPercent / 100.0f) * timerPeriod;
    (void)dutyPercent;
}

} // namespace hardware
