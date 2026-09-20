#include "ServoController.hpp"
#include <cmath>
#include <algorithm>

namespace servo {

ServoController::ServoController(ServoChipType chip)
    : m_chipType(chip)
{
    // AA5188 та KC0032 мають власну порогову чутливість внутрішнього компаратора.
    // AA5188 стандартно потребує deadband ~4 мкс для стійкості проти шуму дрібних флуктуацій.
    // KC0032 є більш високоточним підсилювачем, де достатньо ~2 мкс.
    if (m_chipType == ServoChipType::KC0032) {
        m_deadbandConfig.deadbandUs = 2;
    } else {
        m_deadbandConfig.deadbandUs = 4;
    }
    m_currentPulseUs = m_pulseConfig.centerPulseUs;
}

bool ServoController::configure(const PulseConfig& pulseCfg, const DeadbandConfig& deadbandCfg) {
    // Перевірка некоректних часових меж імпульсів
    if (pulseCfg.minPulseUs >= pulseCfg.maxPulseUs) {
        return false;
    }
    if (pulseCfg.centerPulseUs < pulseCfg.minPulseUs || pulseCfg.centerPulseUs > pulseCfg.maxPulseUs) {
        return false;
    }
    if (pulseCfg.framePeriodUs <= pulseCfg.maxPulseUs) {
        return false;
    }

    m_pulseConfig = pulseCfg;
    m_deadbandConfig = deadbandCfg;

    // Нормалізація поточного значення у нових межах
    m_currentPulseUs = std::clamp(m_currentPulseUs, m_pulseConfig.minPulseUs, m_pulseConfig.maxPulseUs);
    m_lastActionFiltered = false;
    return true;
}

uint16_t ServoController::setTargetAngle(float angleDeg, float maxAngleDeg) {
    if (maxAngleDeg <= 0.0f) {
        maxAngleDeg = 180.0f;
    }

    // Обмеження кута в дозволеному діапазоні
    float clampedAngle = std::clamp(angleDeg, 0.0f, maxAngleDeg);

    // Перетворення кута в мікросекунди імпульсу (лінійна інтерполяція)
    float ratio = clampedAngle / maxAngleDeg;
    float pulseFloat = static_cast<float>(m_pulseConfig.minPulseUs) +
                       ratio * static_cast<float>(m_pulseConfig.maxPulseUs - m_pulseConfig.minPulseUs);

    uint16_t targetUs = static_cast<uint16_t>(std::round(pulseFloat));
    return setTargetPulseUs(targetUs);
}

uint16_t ServoController::setTargetPulseUs(uint16_t targetUs) {
    // Обмеження тривалості імпульсу в допустимих межах [minPulseUs, maxPulseUs]
    uint16_t boundedUs = std::clamp(targetUs, m_pulseConfig.minPulseUs, m_pulseConfig.maxPulseUs);
    return filterDeadband(boundedUs);
}

uint16_t ServoController::filterDeadband(uint16_t targetUs) {
    if (!m_deadbandConfig.enabled) {
        m_lastActionFiltered = false;
        m_currentPulseUs = targetUs;
        return m_currentPulseUs;
    }

    // Абсолютна різниця між запитуваним та поточним встановленим значенням
    int diff = std::abs(static_cast<int>(targetUs) - static_cast<int>(m_currentPulseUs));

    // Якщо відхилення менше або дорівнює порогу зони нечутливості (deadband),
    // вихідний імпульс НЕ змінюється. Це відсікає дрібні флуктуації сигналу
    // зворотного зв'язку, придушує високочастотне "тремтіння" (hunting/jitter)
    // сервоприводу та запобігає перегріву силових ключових транзисторів H-моста AA5188/KC0032.
    if (diff <= static_cast<int>(m_deadbandConfig.deadbandUs)) {
        m_lastActionFiltered = true;
        return m_currentPulseUs;
    }

    m_lastActionFiltered = false;
    m_currentPulseUs = targetUs;
    return m_currentPulseUs;
}

uint16_t ServoController::getCurrentPulseUs() const {
    return m_currentPulseUs;
}

TimerTiming ServoController::calculateTimerTiming(uint32_t timerClockHz) const {
    TimerTiming timing{};
    timing.pulseDurationUs = m_currentPulseUs;
    timing.periodUs = m_pulseConfig.framePeriodUs;

    if (m_pulseConfig.framePeriodUs > 0) {
        timing.dutyCyclePercent = (static_cast<float>(m_currentPulseUs) / static_cast<float>(m_pulseConfig.framePeriodUs)) * 100.0f;
    } else {
        timing.dutyCyclePercent = 0.0f;
    }

    // Кількість тіків таймера: Ticks = (pulseUs * clockHz) / 1,000,000
    if (timerClockHz > 0) {
        uint64_t ticks = (static_cast<uint64_t>(m_currentPulseUs) * static_cast<uint64_t>(timerClockHz)) / 1000000ULL;
        timing.timerTicks = static_cast<uint32_t>(ticks);
    } else {
        timing.timerTicks = 0;
    }

    return timing;
}

const DeadbandConfig& ServoController::getDeadbandConfig() const {
    return m_deadbandConfig;
}

const PulseConfig& ServoController::getPulseConfig() const {
    return m_pulseConfig;
}

void ServoController::setDeadbandUs(uint16_t deadbandUs) {
    m_deadbandConfig.deadbandUs = deadbandUs;
}

bool ServoController::wasFilteredByDeadband() const {
    return m_lastActionFiltered;
}

} // namespace servo
