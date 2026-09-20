#include "ApcLaserController.hpp"
#include <algorithm>
#include <cmath>
#include <numeric>

namespace laser {

ApcLaserController::ApcLaserController(const CurrentConfig& currentCfg, const ThermalConfig& thermalCfg)
    : m_currentCfg(currentCfg),
      m_thermalCfg(thermalCfg),
      m_targetPowerMW(currentCfg.targetPowerMW) {
    m_powerHistory.fill(0.0f);
}

bool ApcLaserController::initialize() {
    m_actualPumpCurrentmA = 0.0f;
    m_measuredPowerMW = 0.0f;
    m_measuredMpdCurrentuA = 0.0f;
    m_powerStabilityPercent = 100.0f;
    m_currentFault = FaultReason::None;

    hwEmergencyShutdown();

    // Перевіряємо початкові температурні межі перед запуском
    if (m_temperatureCelsius < m_thermalCfg.minTempCelsius) {
        m_currentFault = FaultReason::UnderTemperature;
        m_initialized = false;
        return false;
    }

    if (m_temperatureCelsius >= m_thermalCfg.maxTempCelsius) {
        m_currentFault = FaultReason::OverTemperature;
        m_initialized = false;
        return false;
    }

    m_initialized = true;
    return true;
}

bool ApcLaserController::enableLaser() {
    if (!m_initialized) {
        return false;
    }

    if (m_currentFault != FaultReason::None) {
        return false;
    }

    if (!checkSafetyLimits()) {
        return false;
    }

    // Плавний запуск (Soft-Start): поступове збільшення струму від 0 до Ith, потім до робочої точки
    m_isEnabled = true;
    float startTargetCurrent = m_currentCfg.thresholdCurrentmA + 
                               (m_targetPowerMW / m_currentCfg.slopeEfficiency);

    startTargetCurrent = std::min(startTargetCurrent, m_currentCfg.maxPumpCurrentmA);

    constexpr int RAMP_STEPS = 10;
    float currentStep = startTargetCurrent / static_cast<float>(RAMP_STEPS);

    for (int i = 1; i <= RAMP_STEPS; ++i) {
        float stepCurrent = currentStep * static_cast<float>(i);
        hwSetPumpCurrent(stepCurrent);
        m_actualPumpCurrentmA = stepCurrent;

        // Імітуємо оновлення фотодіода під час рампи для контролю контуру
        float simulatedPower = std::max(0.0f, (stepCurrent - m_currentCfg.thresholdCurrentmA) * m_currentCfg.slopeEfficiency);
        m_measuredMpdCurrentuA = simulatedPower * m_currentCfg.mpdResponsivity;
        m_measuredPowerMW = simulatedPower;

        if (!checkSafetyLimits()) {
            disableLaser(m_currentFault);
            return false;
        }
    }

    return true;
}

void ApcLaserController::disableLaser(FaultReason reason) {
    m_isEnabled = false;
    m_actualPumpCurrentmA = 0.0f;
    m_measuredPowerMW = 0.0f;
    m_measuredMpdCurrentuA = 0.0f;
    hwEmergencyShutdown();

    if (reason != FaultReason::None) {
        m_currentFault = reason;
    }
}

void ApcLaserController::processControlLoop(float deltaTimeSec) {
    if (!m_isEnabled) {
        return;
    }

    // 1. Апаратна та програмна перевірка безпеки
    if (!checkSafetyLimits()) {
        disableLaser(m_currentFault);
        return;
    }

    // 2. Обчислення зчитаної з фотодіода оптичної потужності
    if (m_currentCfg.mpdResponsivity > 0.0f) {
        m_measuredPowerMW = m_measuredMpdCurrentuA / m_currentCfg.mpdResponsivity;
    } else {
        m_measuredPowerMW = 0.0f;
    }

    // 3. Контур APC (Автоматичне регулювання потужності): PI-пропорційне коригування
    float powerError = m_targetPowerMW - m_measuredPowerMW;
    constexpr float PROPORTIONAL_GAIN = 1.5f; // мА/мВт

    float currentAdjustment = powerError * PROPORTIONAL_GAIN * deltaTimeSec;
    float newCurrent = m_actualPumpCurrentmA + currentAdjustment;

    // Обмеження струму безпечними межами
    newCurrent = std::clamp(newCurrent, 0.0f, m_currentCfg.maxPumpCurrentmA);

    hwSetPumpCurrent(newCurrent);
    m_actualPumpCurrentmA = newCurrent;

    // 4. Оновлення математичної оцінки стабільності випромінювання
    updateStabilityCalculation(m_measuredPowerMW);
}

bool ApcLaserController::setTargetPower(float powerMW) {
    if (powerMW < 0.0f) {
        return false;
    }

    // Розраховуємо необхідний струм для заданої потужності
    float requiredCurrent = m_currentCfg.thresholdCurrentmA + (powerMW / m_currentCfg.slopeEfficiency);

    if (requiredCurrent > m_currentCfg.maxPumpCurrentmA) {
        return false; // Потужність вимагає струму вище допустимого максимуму
    }

    m_targetPowerMW = powerMW;
    return true;
}

void ApcLaserController::updateTemperatureSensor(float tempCelsius) {
    m_temperatureCelsius = tempCelsius;
    if (m_isEnabled) {
        checkSafetyLimits();
    }
}

void ApcLaserController::updatePhotodiodeSensor(float mpdCurrentuA) {
    m_measuredMpdCurrentuA = mpdCurrentuA;
}

ApcMetrics ApcLaserController::getMetrics() const {
    ApcMetrics metrics;
    metrics.currentPumpmA = m_actualPumpCurrentmA;
    metrics.opticalPowerMW = m_measuredPowerMW;
    metrics.mpdCurrentuA = m_measuredMpdCurrentuA;
    metrics.temperatureCelsius = m_temperatureCelsius;
    metrics.powerStabilityPercent = m_powerStabilityPercent;
    metrics.isLaserEnabled = m_isEnabled;
    metrics.lastFault = m_currentFault;
    return metrics;
}

void ApcLaserController::clearFault() {
    m_currentFault = FaultReason::None;
}

void ApcLaserController::hwSetPumpCurrent(float currentmA) {
    // В реальній системі тут відбувається запис значення в ЦАП або ШІМ драйвера
    m_actualPumpCurrentmA = currentmA;
}

void ApcLaserController::hwEmergencyShutdown() {
    // В реальній системі тут апаратно скидається Pin Enable драйвера в 0
    m_actualPumpCurrentmA = 0.0f;
}

bool ApcLaserController::checkSafetyLimits() {
    // Контроль температурних меж
    if (m_temperatureCelsius >= m_thermalCfg.criticalTempCelsius) {
        m_currentFault = FaultReason::CriticalOverTemperature;
        return false;
    }

    if (m_temperatureCelsius > m_thermalCfg.maxTempCelsius) {
        m_currentFault = FaultReason::OverTemperature;
        return false;
    }

    if (m_temperatureCelsius < m_thermalCfg.minTempCelsius) {
        m_currentFault = FaultReason::UnderTemperature;
        return false;
    }

    // Контроль струму накачки
    if (m_actualPumpCurrentmA > m_currentCfg.maxPumpCurrentmA) {
        m_currentFault = FaultReason::OverCurrent;
        return false;
    }

    // Контроль загрози COD (Catastrophic Optical Damage) та несправності фотодіода:
    // Якщо струм накачки суттєво вищий за пороговий (I > Ith + 10мА),
    // але зворотний струм з моніторного фотодіода відсутній (Mpd ≈ 0),
    // це свідчить про руйнування дзеркальних граней (COD) або обрив фотодіода.
    if (m_actualPumpCurrentmA > (m_currentCfg.thresholdCurrentmA + 10.0f)) {
        if (m_measuredMpdCurrentuA < 0.1f) {
            m_currentFault = FaultReason::CodProtectionTriggered;
            return false;
        }
    }

    return true;
}

void ApcLaserController::updateStabilityCalculation(float currentPower) {
    m_powerHistory[m_historyIndex] = currentPower;
    m_historyIndex = (m_historyIndex + 1) % STABILITY_WINDOW_SIZE;
    if (m_historyCount < STABILITY_WINDOW_SIZE) {
        m_historyCount++;
    }

    if (m_historyCount == 0) {
        m_powerStabilityPercent = 100.0f;
        return;
    }

    // Обчислення середнього значення потужності
    float sum = std::accumulate(m_powerHistory.begin(), m_powerHistory.begin() + m_historyCount, 0.0f);
    float mean = sum / static_cast<float>(m_historyCount);

    if (mean <= 0.001f) {
        m_powerStabilityPercent = 0.0f;
        return;
    }

    // Обчислення середньоквадратичного відхилення (σ)
    float varianceSum = 0.0f;
    for (std::size_t i = 0; i < m_historyCount; ++i) {
        float diff = m_powerHistory[i] - mean;
        varianceSum += diff * diff;
    }
    float stdDev = std::sqrt(varianceSum / static_cast<float>(m_historyCount));

    // Відносна стабільність у відсотках: 100% - (stdDev / mean * 100%)
    float relativeVariation = (stdDev / mean) * 100.0f;
    m_powerStabilityPercent = std::clamp(100.0f - relativeVariation, 0.0f, 100.0f);
}

} // namespace laser
