#include "pwm_timer.hpp"
#include <chrono>
#include <thread>
#include <algorithm>
#include <iostream>

namespace embedded {

PwmTimer::PwmTimer(uint8_t pinIn1, uint8_t pinIn2, uint8_t pinEnable, uint32_t frequencyHz)
    : pinIn1_(pinIn1), pinIn2_(pinIn2), pinEnable_(pinEnable), frequencyHz_(frequencyHz) {}

bool PwmTimer::init() {
    if (frequencyHz_ == 0 || frequencyHz_ > 100000) {
        std::cerr << "[PwmTimer] Помилка: недопустима частота ШІМ: " << frequencyHz_ << " Гц.\n";
        initialized_ = false;
        return false;
    }

    std::cout << "[PwmTimer] Конфігурація GPIO виводів Push-Pull: IN1=" << static_cast<int>(pinIn1_)
              << ", IN2=" << static_cast<int>(pinIn2_)
              << ", EN/PWM=" << static_cast<int>(pinEnable_) << "\n";
    std::cout << "[PwmTimer] Програмування регістрів апаратного таймера: частота ШІМ = "
              << frequencyHz_ << " Гц (беззвучний режим обмоток).\n";

    // Безпечна ініціалізація виводів у стан LOW
    setDirectionPins(false, false);
    stopPwm();

    initialized_ = true;
    return true;
}

void PwmTimer::setDirectionPins(bool in1, bool in2) {
    std::cout << "[PwmTimer] Запис у регістр GPIO: IN1 (Pin " << static_cast<int>(pinIn1_) << ") = "
              << (in1 ? "HIGH" : "LOW") << ", IN2 (Pin " << static_cast<int>(pinIn2_) << ") = "
              << (in2 ? "HIGH" : "LOW") << "\n";
}

void PwmTimer::setPwmDuty(uint8_t dutyPercent) {
    if (!initialized_) {
        std::cerr << "[PwmTimer] Помилка: спроба задати ШІМ до ініціалізації периферії!\n";
        return;
    }

    currentDutyPercent_ = std::min(dutyPercent, static_cast<uint8_t>(100));
    uint16_t compareVal = calculateCompareValue(currentDutyPercent_);

    std::cout << "[PwmTimer] Оновлення регістру порівняння TIMx->CCR: Duty Cycle = "
              << static_cast<int>(currentDutyPercent_) << "% (Compare Count = "
              << compareVal << " / 1000)\n";
}

void PwmTimer::stopPwm() {
    currentDutyPercent_ = 0;
    std::cout << "[PwmTimer] Зупинка генерації ШІМ-сигналу (Duty Cycle = 0%).\n";
}

uint16_t PwmTimer::calculateCompareValue(uint8_t dutyPercent) const noexcept {
    constexpr uint16_t timerPeriodARR = 1000;
    return static_cast<uint16_t>((static_cast<uint32_t>(dutyPercent) * timerPeriodARR) / 100);
}

void PwmTimer::delayMs(uint32_t ms) {
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
}

} // namespace embedded
