#include "gearmotor.hpp"
#include <algorithm>

namespace actuators {

namespace {

/**
 * @brief Рядок таблиці комутації для дискретних ліній напрямку H-моста.
 */
struct BridgeEntry {
    bool in1;
    bool in2;
};

/**
 * @brief Таблиця безпечної комутації силових ключів H-моста.
 * Індексується значенням enum class State.
 *
 * - STOP_COAST: IN1 = 0, IN2 = 0 -> Усі ключі вимкнено (High-Z), вільний вибіг.
 * - FORWARD:    IN1 = 1, IN2 = 0 -> Верхній лівий і нижній правий ключі відкриті.
 * - REVERSE:    IN1 = 0, IN2 = 1 -> Верхній правий і нижній лівий ключі відкриті.
 * - BRAKE:      IN1 = 1, IN2 = 1 -> Обидва нижні ключі відкриті на GND,
 *                                   замикаючи обмотки накоротко для демпфування проти-ЕРС.
 */
constexpr BridgeEntry BRIDGE_COMMUTATION_TABLE[] = {
    { false, false }, // State::STOP_COAST
    { true,  false }, // State::FORWARD
    { false, true  }, // State::REVERSE
    { true,  true  }  // State::BRAKE
};

} // анонімний простір імен

Gearmotor::Gearmotor(const Config& config) noexcept
    : m_config(config) {
}

bool Gearmotor::init() noexcept {
    if (!m_config.writeGpio || !m_config.writePwm) {
        return false;
    }

    // Початковий перехід у безпечний стан: ключі розімкнені, ШІМ дорівнює нулю
    m_state = State::STOP_COAST;
    m_activeDir = Direction::STOP;
    m_targetDir = Direction::STOP;
    m_currentDuty = 0;
    m_targetDuty = 0;
    m_deadTimeRemainingMs = 0;
    m_rampAccumulator = 0;
    m_brakeActive = false;

    applyHBridge(State::STOP_COAST, 0);
    return true;
}

void Gearmotor::setSpeed(int16_t targetSpeed) noexcept {
    // Обмеження значення за модулем у межах заданого maxDuty
    const int16_t maxLimit = static_cast<int16_t>(m_config.maxDuty);
    if (targetSpeed > maxLimit) {
        targetSpeed = maxLimit;
    } else if (targetSpeed < -maxLimit) {
        targetSpeed = -maxLimit;
    }

    if (targetSpeed > 0) {
        setTarget(Direction::FORWARD, static_cast<uint16_t>(targetSpeed));
    } else if (targetSpeed < 0) {
        setTarget(Direction::REVERSE, static_cast<uint16_t>(-targetSpeed));
    } else {
        setTarget(Direction::STOP, 0);
    }
}

void Gearmotor::setTarget(Direction dir, uint16_t duty) noexcept {
    // Будь-яка нова команда руху або зупинки скасовує форсоване активне гальмування
    m_brakeActive = false;

    if (duty > m_config.maxDuty) {
        duty = m_config.maxDuty;
    }

    if (dir == Direction::STOP || duty == 0) {
        m_targetDir = Direction::STOP;
        m_targetDuty = 0;
    } else {
        m_targetDir = dir;
        m_targetDuty = duty;
    }
}

void Gearmotor::brake() noexcept {
    m_brakeActive = true;
    m_targetDir = Direction::STOP;
    m_activeDir = Direction::STOP;
    m_targetDuty = 0;
    m_currentDuty = 0;
    m_deadTimeRemainingMs = 0;
    m_rampAccumulator = 0;
    m_state = State::BRAKE;

    // Активне гальмування: закорочення обмоток на шину GND при 100% шпаруватості
    applyHBridge(State::BRAKE, m_config.maxDuty);
}

void Gearmotor::coast() noexcept {
    m_brakeActive = false;
    m_targetDir = Direction::STOP;
    m_activeDir = Direction::STOP;
    m_targetDuty = 0;
    m_currentDuty = 0;
    m_deadTimeRemainingMs = 0;
    m_rampAccumulator = 0;
    m_state = State::STOP_COAST;

    // Вільний вибіг: зняття ШІМ і переведення моста у стан високого імпедансу (High-Z)
    applyHBridge(State::STOP_COAST, 0);
}

bool Gearmotor::isRamping() const noexcept {
    if (m_brakeActive) {
        return false;
    }
    if (m_deadTimeRemainingMs > 0) {
        return true;
    }
    if (m_activeDir != m_targetDir) {
        return true;
    }
    return (m_currentDuty != m_targetDuty);
}

void Gearmotor::applyHBridge(State state, uint16_t duty) noexcept {
    if (!m_config.writeGpio || !m_config.writePwm) {
        return;
    }

    const auto tableIndex = static_cast<size_t>(state);
    if (tableIndex >= sizeof(BRIDGE_COMMUTATION_TABLE) / sizeof(BRIDGE_COMMUTATION_TABLE[0])) {
        return;
    }
    const BridgeEntry& entry = BRIDGE_COMMUTATION_TABLE[tableIndex];

    // ЗАХИСТ ВІД НАСКРІЗНОГО СТРУМУ (Break-before-make):
    // Крок 1: Обов'язково скидаємо сигнал ШІМ у 0 перед зміною логічних рівнів напрямку,
    // щоб силові транзистори гарантовано закрилися до комутації плечей моста.
    m_config.writePwm(m_config.pins.pwm, 0);

    // Крок 2: Встановлюємо логічні рівні на дискретних входах напрямку IN1 та IN2
    m_config.writeGpio(m_config.pins.in1, entry.in1);
    m_config.writeGpio(m_config.pins.in2, entry.in2);

    // Крок 3: Подаємо шпаруватість тільки після фіксації напрямку
    if (state == State::BRAKE) {
        // У режимі динамічного гальмування відкриваємо обидва нижні ключі повністю (100% ШІМ)
        m_config.writePwm(m_config.pins.pwm, m_config.maxDuty);
    } else if (state != State::STOP_COAST && duty > 0) {
        // У режимі руху подаємо обчислену шпаруватість
        m_config.writePwm(m_config.pins.pwm, duty);
    }
}

void Gearmotor::update(uint32_t deltaMs) noexcept {
    if (deltaMs == 0 || m_brakeActive) {
        return;
    }

    // ФАЗА 1: Обробка захисної паузи (dead-time) під час зміни полярності
    if (m_deadTimeRemainingMs > 0) {
        if (deltaMs >= m_deadTimeRemainingMs) {
            m_deadTimeRemainingMs = 0;
            // Захисна пауза минула: індуктивні струми спали, тепер безпечно комутувати новий напрямок
            m_activeDir = m_targetDir;
            if (m_activeDir == Direction::FORWARD) {
                m_state = State::FORWARD;
            } else if (m_activeDir == Direction::REVERSE) {
                m_state = State::REVERSE;
            } else {
                m_state = State::STOP_COAST;
            }
            applyHBridge(m_state, 0);
        } else {
            m_deadTimeRemainingMs -= deltaMs;
            return; // Продовжуємо утримувати міст розімкненим
        }
    }

    // ФАЗА 2: Старт із нерухомого стану
    if (m_activeDir == Direction::STOP) {
        if (m_targetDir != Direction::STOP) {
            m_activeDir = m_targetDir;
            m_state = (m_activeDir == Direction::FORWARD) ? State::FORWARD : State::REVERSE;
            applyHBridge(m_state, 0);
        } else {
            return;
        }
    }

    // ФАЗА 3: Визначення проміжної цілі для лінійної рампи:
    // Якщо активний напрямок не збігається з цільовим (реверс або плавна зупинка),
    // ми зобов'язані спочатку плавно скинути шпаруватість поточного напрямку до 0!
    uint16_t stepTarget = 0;
    bool isDecelerating = false;

    if (m_activeDir != m_targetDir) {
        stepTarget = 0;
        isDecelerating = true;
    } else {
        stepTarget = m_targetDuty;
        isDecelerating = (m_currentDuty > stepTarget);
    }

    // Якщо швидкість уже досягла цільового значення
    if (m_currentDuty == stepTarget) {
        if (m_currentDuty == 0 && m_activeDir != m_targetDir) {
            if (m_targetDir != Direction::STOP) {
                // Швидкість скинута до нуля під час реверсу: починаємо dead-time
                m_state = State::STOP_COAST;
                applyHBridge(State::STOP_COAST, 0);
                m_deadTimeRemainingMs = m_config.deadTimeMs;
            } else {
                // Завершено плавне уповільнення до повної зупинки
                m_activeDir = Direction::STOP;
                m_state = State::STOP_COAST;
                applyHBridge(State::STOP_COAST, 0);
            }
        }
        return;
    }

    // ФАЗА 4: Розрахунок кроку рампи з дробовим накопичувачем
    // Темп задано в одиницях шпаруватості за секунду (одиниць/1000 мс)
    const uint32_t rate = isDecelerating ? m_config.decelRate : m_config.accelRate;
    const uint32_t totalDelta = rate * deltaMs + m_rampAccumulator;
    const uint16_t step = static_cast<uint16_t>(totalDelta / 1000);
    m_rampAccumulator = totalDelta % 1000;

    if (step == 0) {
        return; // За короткий інтервал крок ще не накопичився
    }

    // ФАЗА 5: Зміна шпаруватості ШІМ (акселерація або деселерація)
    if (!isDecelerating) {
        // Розгін: плавне наростання крутного моменту, захист зубців редуктора від удару
        if (m_currentDuty + step >= stepTarget) {
            m_currentDuty = stepTarget;
        } else {
            m_currentDuty += step;
        }
    } else {
        // Уповільнення
        if (m_currentDuty <= step || m_currentDuty - step <= stepTarget) {
            m_currentDuty = stepTarget;
        } else {
            m_currentDuty -= step;
        }
    }

    // ФАЗА 6: Оновлення ШІМ на драйвері або запуск dead-time при досягненні нуля
    if (m_currentDuty == 0 && m_activeDir != m_targetDir) {
        if (m_targetDir != Direction::STOP) {
            // Нульова швидкість під час реверсу: вимикаємо ключі на час dead-time
            m_state = State::STOP_COAST;
            applyHBridge(State::STOP_COAST, 0);
            m_deadTimeRemainingMs = m_config.deadTimeMs;
        } else {
            // Зупинка завершена
            m_activeDir = Direction::STOP;
            m_state = State::STOP_COAST;
            applyHBridge(State::STOP_COAST, 0);
        }
    } else {
        // Оновлюємо коефіцієнт заповнення ШІМ без зайвої перекомутації дискретних ліній
        if (m_config.writePwm) {
            m_config.writePwm(m_config.pins.pwm, m_currentDuty);
        }
    }
}

} // namespace actuators
