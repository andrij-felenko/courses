#include "BatteryMonitor.h"
#include <iostream>

BatteryMonitor::BatteryMonitor(uint8_t enPin, uint8_t adcPin,
                               float rTopOhms, float rBottomOhms,
                               float vrefVolts, float adcMaxTicks,
                               float cutoffVolts, float recoveryVolts,
                               float emaAlpha)
    : m_enPin(enPin),
      m_adcPin(adcPin),
      m_dividerRatio((rTopOhms + rBottomOhms) / rBottomOhms),
      m_vref(vrefVolts),
      m_adcMax(adcMaxTicks),
      m_cutoffVolts(cutoffVolts),
      m_recoveryVolts(recoveryVolts),
      m_emaAlpha(emaAlpha) {}

void BatteryMonitor::begin() {
    applyHardwareEn(true);
    m_boostActive = true;
    m_state = BatteryState::Nominal;
    std::cout << "[BatteryMonitor] Ініціалізація: дільник x" << m_dividerRatio 
              << ", поріг відсічки " << m_cutoffVolts << " В\n";
}

void BatteryMonitor::applyHardwareEn(bool active) {
    // В апаратній прошивці: digitalWrite(m_enPin, active ? HIGH : LOW);
    std::cout << "[GPIO EN " << static_cast<int>(m_enPin) << "] Рівень: "
              << (active ? "HIGH (MT3608 увімкнено)" : "LOW (MT3608 заблоковано)") << "\n";
}

void BatteryMonitor::setState(BatteryState newState) {
    if (m_state != newState) {
        m_state = newState;
        if (m_callback) {
            m_callback(m_state, m_filteredVoltage);
        }
    }
}

void BatteryMonitor::update(uint16_t rawAdc) {
    // Миттєве значення напруги акумулятора з урахуванням опору дільника
    float instantVoltage = ((static_cast<float>(rawAdc) * m_vref) / m_adcMax) * m_dividerRatio;

    // Цифровий фільтр низьких частот: експоненційне ковзне середнє (EMA)
    m_filteredVoltage = (m_emaAlpha * instantVoltage) + ((1.0f - m_emaAlpha) * m_filteredVoltage);

    // Компаратор стану з пороговим гістерезисом
    if (m_boostActive) {
        if (m_filteredVoltage <= m_cutoffVolts) {
            m_boostActive = false;
            applyHardwareEn(false);
            setState(BatteryState::CriticalCutoff);
            std::cout << "[ЗАХИСТ] Аварійне відключення навантаження: Vbat = " 
                      << m_filteredVoltage << " В <= " << m_cutoffVolts << " В\n";
        } else if (m_filteredVoltage < m_recoveryVolts) {
            setState(BatteryState::LowWarning);
        } else {
            setState(BatteryState::Nominal);
        }
    } else {
        // Перетворювач вимкнено: відновлення можливе лише при підзарядці вище recoveryVolts
        if (m_filteredVoltage >= m_recoveryVolts) {
            m_boostActive = true;
            applyHardwareEn(true);
            setState(BatteryState::Nominal);
            std::cout << "[ВІДНОВЛЕННЯ] Напругу відновлено: Vbat = " 
                      << m_filteredVoltage << " В >= " << m_recoveryVolts << " В\n";
        } else {
            setState(BatteryState::CriticalCutoff);
        }
    }
}
