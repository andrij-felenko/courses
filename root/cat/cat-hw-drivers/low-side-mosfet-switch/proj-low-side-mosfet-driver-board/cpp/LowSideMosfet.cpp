#include "LowSideMosfet.hpp"
#include <iostream>
#include <algorithm>
#include <thread>
#include <chrono>

LowSideMosfet::LowSideMosfet()
    : m_config{0, 1000, 0.0f, false, 16000000},
      m_state(DriverState::Uninitialized),
      m_currentDutyCycle(0.0f),
      m_currentArr(0),
      m_currentCcr(0),
      m_enabled(false) {
}

LowSideMosfet::~LowSideMosfet() {
    // При знищенні об'єкта негайно знеструмлюємо навантаження для безпеки
    emergencyStop();
}

bool LowSideMosfet::begin(const MosfetConfig& config) {
    // Крок 1: Негайно переводимо пин затвора в безпечний стан
    // Затвор N-канал MOSFET має великий опір ізолятора; без pull-down він ловить наводки!
    m_config = config;
    setupSafePinState();

    // Перевірка коректності вхідних параметрів
    if (m_config.pwmFrequencyHz == 0 || m_config.timerClockHz == 0) {
        std::cout << "[ERROR] Помилка конфігурації: частота не може дорівнювати 0 Гц!" << std::endl;
        m_state = DriverState::Fault;
        return false;
    }

    // Обмеження початкового Duty Cycle у межах 0.0%..100.0%
    m_config.initialDutyCycle = std::clamp(m_config.initialDutyCycle, 0.0f, 100.0f);
    m_currentDutyCycle = m_config.initialDutyCycle;

    // Крок 2: Перераховуємо регістри таймера для заданої частоти та заповнення
    if (!recalculateTimerRegisters(m_config.pwmFrequencyHz, m_currentDutyCycle)) {
        m_state = DriverState::Fault;
        return false;
    }

    m_state = DriverState::Disabled;
    std::cout << "[DRIVER] Успішна ініціалізація N-MOSFET на пині " 
              << static_cast<int>(m_config.gpioPin) 
              << " | Частота: " << m_config.pwmFrequencyHz << " Гц"
              << " | Стартовий Duty: " << m_currentDutyCycle << "%" << std::endl;

    return true;
}

void LowSideMosfet::setupSafePinState() {
    // Імітація низькорівневого налаштування GPIO МК:
    // Конфігуруємо вивід як Push-Pull Output і записуємо 0 (LOW), 
    // щоб увімкнути внутрішній/зовнішній pull-down та заземлити затвор під час скидання МК.
    std::cout << "[HW GPIO] Пин " << static_cast<int>(m_config.gpioPin) 
              << " налаштовано як OUTPUT LOW (Pull-Down активний). Затвор притиснуто до GND." << std::endl;
}

bool LowSideMosfet::recalculateTimerRegisters(uint32_t frequencyHz, float dutyPercent) {
    if (frequencyHz == 0) {
        return false;
    }

    // Формула для розрахунку періоду таймера (Auto-Reload Register):
    // ARR = (Timer_Clock / Frequency) - 1
    uint64_t arrValue = (static_cast<uint64_t>(m_config.timerClockHz) / frequencyHz);
    if (arrValue == 0) {
        std::cout << "[ERROR] Частота ШІМ занадто висока для даного таймера!" << std::endl;
        return false;
    }
    arrValue -= 1;

    // Обмеження значення регістру 16-бітним або 32-бітним діапазоном
    m_currentArr = static_cast<uint32_t>(arrValue);

    // Формула для розрахунку регістру порівняння (Capture/Compare Register):
    // CCR = (ARR + 1) * (DutyCycle / 100%)
    float clampedDuty = std::clamp(dutyPercent, 0.0f, 100.0f);
    if (m_config.invertedLogic) {
        clampedDuty = 100.0f - clampedDuty;
    }

    m_currentCcr = static_cast<uint32_t>((m_currentArr + 1) * (clampedDuty / 100.0f));
    return true;
}

void LowSideMosfet::updateHardwareRegisters() {
    if (!m_enabled) {
        // Якщо ШІМ вимкнено, CCR примусово рівний 0 (сигнал постійний LOW)
        std::cout << "[HW TIMER] ШІМ вимкнено -> TIM_CCR = 0 (Затвор 0V)" << std::endl;
        return;
    }

    // Запис обчислених значень у фізичні регістри таймера МК (наприклад, TIMx->ARR та TIMx->CCR1)
    std::cout << "[HW TIMER] Оновлення регістрів -> ARR (Період): " << m_currentArr 
              << " | CCR (Імпульс): " << m_currentCcr 
              << " | Розрахунковий Duty: " << m_currentDutyCycle << "%" << std::endl;
}

void LowSideMosfet::setDutyCycle(float percent) {
    if (m_state == DriverState::Uninitialized || m_state == DriverState::Fault) {
        std::cout << "[WARN] Спроба встановити Duty Cycle для несправного або неініціалізованого драйвера!" << std::endl;
        return;
    }

    m_currentDutyCycle = std::clamp(percent, 0.0f, 100.0f);
    recalculateTimerRegisters(m_config.pwmFrequencyHz, m_currentDutyCycle);
    updateHardwareRegisters();
}

float LowSideMosfet::getDutyCycle() const {
    return m_currentDutyCycle;
}

bool LowSideMosfet::setFrequency(uint32_t frequencyHz) {
    if (frequencyHz == 0 || m_state == DriverState::Uninitialized) {
        return false;
    }

    if (recalculateTimerRegisters(frequencyHz, m_currentDutyCycle)) {
        m_config.pwmFrequencyHz = frequencyHz;
        updateHardwareRegisters();
        std::cout << "[DRIVER] Частоту ШІМ успішно змінено на " << frequencyHz << " Гц" << std::endl;
        return true;
    }
    return false;
}

uint32_t LowSideMosfet::getFrequency() const {
    return m_config.pwmFrequencyHz;
}

void LowSideMosfet::rampPower(float targetPercent, uint32_t durationMs, uint32_t stepMs) {
    if (m_state != DriverState::Active) {
        std::cout << "[WARN] Плавна зміна потужності доступна лише у стані Active!" << std::endl;
        return;
    }

    targetPercent = std::clamp(targetPercent, 0.0f, 100.0f);
    if (durationMs == 0 || stepMs == 0) {
        setDutyCycle(targetPercent);
        return;
    }

    uint32_t totalSteps = durationMs / stepMs;
    if (totalSteps == 0) {
        totalSteps = 1;
    }

    float startDuty = m_currentDutyCycle;
    float stepDelta = (targetPercent - startDuty) / static_cast<float>(totalSteps);

    std::cout << "[RAMP] Початок плавного переходу: " << startDuty << "% -> " << targetPercent 
              << "% за " << durationMs << " мс (" << totalSteps << " кроків)" << std::endl;

    for (uint32_t i = 1; i <= totalSteps; ++i) {
        float nextDuty = startDuty + (stepDelta * static_cast<float>(i));
        setDutyCycle(nextDuty);
        std::this_thread::sleep_for(std::chrono::milliseconds(stepMs));
    }

    // Встановлюємо точне цільове значення у кінці для уникнення накопичення накопичувальної похибки float
    setDutyCycle(targetPercent);
    std::cout << "[RAMP] Плавний перехід завершено. Поточна потужність: " << m_currentDutyCycle << "%" << std::endl;
}

void LowSideMosfet::emergencyStop() {
    m_enabled = false;
    m_currentDutyCycle = 0.0f;
    m_currentCcr = 0;
    m_state = DriverState::Disabled;

    // Аварійне притиснення затвора до землі (0 В на Gate)
    std::cout << "[EMERGENCY STOP] Аварійне вимкнення MOSFET! Вихід знеструмлено." << std::endl;
    updateHardwareRegisters();
}

void LowSideMosfet::enable() {
    if (m_state == DriverState::Fault || m_state == DriverState::Uninitialized) {
        std::cout << "[ERROR] Неможливо увімкнути драйвер у стані Fault/Uninitialized!" << std::endl;
        return;
    }

    m_enabled = true;
    m_state = DriverState::Active;
    std::cout << "[DRIVER] Генерацію ШІМ увімкнено." << std::endl;
    updateHardwareRegisters();
}

void LowSideMosfet::disable() {
    m_enabled = false;
    m_state = DriverState::Disabled;
    std::cout << "[DRIVER] Генерацію ШІМ зупинено (Ключ закритий)." << std::endl;
    updateHardwareRegisters();
}

bool LowSideMosfet::isEnabled() const {
    return m_enabled;
}

DriverState LowSideMosfet::getState() const {
    return m_state;
}
