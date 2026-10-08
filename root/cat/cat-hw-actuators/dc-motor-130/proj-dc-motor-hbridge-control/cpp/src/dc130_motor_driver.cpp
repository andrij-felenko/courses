#include "dc130_motor_driver.hpp"
#include <algorithm>
#include <iostream>

namespace embedded {

DC130MotorDriver::DC130MotorDriver(const MotorConfig& config)
    : config_(config),
      timer_(config.pinIn1, config.pinIn2, config.pinEnable, config.pwmFrequencyHz) {}

DC130MotorDriver::~DC130MotorDriver() {
    std::cout << "[DC130MotorDriver] Деструктор: автоматичний перевід мотора у безпечний стан вибігу.\n";
    coast();
}

bool DC130MotorDriver::init() {
    std::cout << "[DC130MotorDriver] Ініціалізація об'єктно-орієнтованого драйвера мотора 130...\n";
    if (!timer_.init()) {
        std::cerr << "[DC130MotorDriver] Збій ініціалізації ШІМ-таймера!\n";
        return false;
    }
    coast();
    return true;
}

void DC130MotorDriver::setSpeed(uint8_t percent) {
    uint8_t targetSpeed = std::min(percent, static_cast<uint8_t>(100));

    if (targetSpeed == 0) {
        std::cout << "[DC130MotorDriver] Встановлено 0% швидкості -> інерційний вибіг (Coast).\n";
        coast();
        return;
    }

    // Корекція швидкості для подолання початкового тертя спокою 130-го двигуна
    if (targetSpeed < config_.minDutyCycle) {
        std::cout << "[DC130MotorDriver] Запитана швидкість (" << static_cast<int>(targetSpeed)
                  << "%) нижча за мінімальний поріг (" << static_cast<int>(config_.minDutyCycle)
                  << "%). Автокорекція.\n";
        targetSpeed = config_.minDutyCycle;
    }

    currentSpeed_ = targetSpeed;
    isRunning_ = true;

    applyDirectionPins();
    timer_.setPwmDuty(currentSpeed_);
}

void DC130MotorDriver::setDirection(Direction dir) {
    if (currentDirection_ == dir && isRunning_) {
        return;
    }

    // Якщо мотор в активному русі, застосовуємо програмне витримання Dead Time при реверсі
    if (isRunning_) {
        std::cout << "[DC130MotorDriver] Виявлено реверс під час обертання! Активація захисту Dead Time ("
                  << config_.deadTimeMs << " мс).\n";
        executeDeadTime();
    }

    currentDirection_ = dir;
    std::cout << "[DC130MotorDriver] Встановлено напрямок: "
              << (currentDirection_ == Direction::Forward ? "Forward (Вперед)" : "Reverse (Назад)") << "\n";

    if (isRunning_) {
        applyDirectionPins();
        timer_.setPwmDuty(currentSpeed_);
    }
}

void DC130MotorDriver::brake() {
    std::cout << "[DC130MotorDriver] Виконання активного електродинамічного гальмування (BRAKE):\n";
    std::cout << "  -> Зупинка ШІМ генерації.\n";
    timer_.stopPwm();

    std::cout << "  -> Коротке замикання обмоток двигуна (IN1=HIGH, IN2=HIGH, EN=100%).\n";
    std::cout << "  -> Поглинання енергії проти-ЕРС викликає швидку зупинку ротора.\n";

    timer_.setDirectionPins(true, true);
    timer_.setPwmDuty(100);

    currentSpeed_ = 0;
    isRunning_ = false;
    lastStopMode_ = StopMode::Brake;
}

void DC130MotorDriver::coast() {
    std::cout << "[DC130MotorDriver] Виконання інерційного вибігу (COAST):\n";
    std::cout << "  -> Вимкнення ШІМ генерації.\n";
    timer_.stopPwm();

    std::cout << "  -> Переведення ключів H-моста у високоімпедансний стан Z (IN1=LOW, IN2=LOW).\n";
    std::cout << "  -> Вільне обертання вала за інерцією до повної зупинки.\n";

    timer_.setDirectionPins(false, false);

    currentSpeed_ = 0;
    isRunning_ = false;
    lastStopMode_ = StopMode::Coast;
}

void DC130MotorDriver::executeDeadTime() {
    timer_.stopPwm();
    timer_.setDirectionPins(false, false);
    std::cout << "  [Dead Time] Пауза " << config_.deadTimeMs
              << " мс для примусового розмикання всіх транзисторів моста (захист від наскрізних струмів).\n";
    PwmTimer::delayMs(config_.deadTimeMs);
    std::cout << "  [Dead Time] Паузу витримано успішно.\n";
}

void DC130MotorDriver::applyDirectionPins() {
    if (currentDirection_ == Direction::Forward) {
        timer_.setDirectionPins(true, false);
    } else {
        timer_.setDirectionPins(false, true);
    }
}

// ---------------- Реалізація MotorGuard ----------------

MotorGuard::MotorGuard(DC130MotorDriver& driver, StopMode safeMode) noexcept
    : driver_(&driver), safeMode_(safeMode), active_(true) {}

MotorGuard::~MotorGuard() {
    if (active_ && driver_ != nullptr) {
        std::cout << "[MotorGuard] Автоматична безпечна зупинка у деструкторі RAII-обгортки.\n";
        if (safeMode_ == StopMode::Brake) {
            driver_->brake();
        } else {
            driver_->coast();
        }
    }
}

MotorGuard::MotorGuard(MotorGuard&& other) noexcept
    : driver_(other.driver_), safeMode_(other.safeMode_), active_(other.active_) {
    other.driver_ = nullptr;
    other.active_ = false;
}

MotorGuard& MotorGuard::operator=(MotorGuard&& other) noexcept {
    if (this != &other) {
        if (active_ && driver_ != nullptr) {
            driver_->coast();
        }
        driver_ = other.driver_;
        safeMode_ = other.safeMode_;
        active_ = other.active_;
        other.driver_ = nullptr;
        other.active_ = false;
    }
    return *this;
}

void MotorGuard::dismiss() noexcept {
    active_ = false;
    std::cout << "[MotorGuard] Захисник відключено вручну.\n";
}

} // namespace embedded
