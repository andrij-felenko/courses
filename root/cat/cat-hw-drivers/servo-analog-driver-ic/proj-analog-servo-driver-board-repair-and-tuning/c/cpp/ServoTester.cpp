#include "ServoTester.hpp"

namespace ServoControl {

ServoTester::ServoTester(std::uint32_t systemClockHz) noexcept
    : systemClockHz_(systemClockHz) {}

ServoTester::~ServoTester() {
    stop();
}

ServoTester::ServoTester(ServoTester&& other) noexcept
    : timerRegs_(other.timerRegs_),
      systemClockHz_(other.systemClockHz_),
      currentPulseUs_(other.currentPulseUs_),
      active_(other.active_) {
    other.active_ = false;
    other.timerRegs_ = {};
}

ServoTester& ServoTester::operator=(ServoTester&& other) noexcept {
    if (this != &other) {
        stop();
        timerRegs_ = other.timerRegs_;
        systemClockHz_ = other.systemClockHz_;
        currentPulseUs_ = other.currentPulseUs_;
        active_ = other.active_;

        other.active_ = false;
        other.timerRegs_ = {};
    }
    return *this;
}

bool ServoTester::init() noexcept {
    if (systemClockHz_ < 1000000U) {
        return false;
    }

    // Переддільник частоти для таймера: квант часу = 1 мкс (1 МГц)
    const std::uint32_t prescaler = (systemClockHz_ / 1000000U) - 1U;
    timerRegs_.PSC = prescaler;

    // Регістр автоперезавантаження ARR = 20000 мкс - 1 (кадр 50 Гц / 20 мс)
    timerRegs_.ARR = PERIOD_US - 1U;

    // Початковий високий рівень імпульсу — нейтраль 1500 мкс
    currentPulseUs_ = NEUTRAL_PULSE_US;
    timerRegs_.CCR1 = currentPulseUs_;

    // Вимкнено до явно виклику start()
    timerRegs_.CR1 &= ~TIM_CR1_CEN;
    timerRegs_.CCER &= ~TIM_CCER_CC1E;
    active_ = false;

    return true;
}

void ServoTester::start() noexcept {
    timerRegs_.CCER |= TIM_CCER_CC1E;
    timerRegs_.CR1 |= TIM_CR1_CEN;
    active_ = true;
}

void ServoTester::stop() noexcept {
    timerRegs_.CR1 &= ~TIM_CR1_CEN;
    timerRegs_.CCER &= ~TIM_CCER_CC1E;
    active_ = false;
}

void ServoTester::setPulseWidthUs(std::uint16_t microseconds) noexcept {
    // Внутрішня схема AA5188 / KC0032 чутлива до тривалості імпульсів.
    // Обрізаємо значення до безпечних меж (1000..2000 мкс), щоб уникнути
    // виходу мотора на механічні упори та перегріву Н-моста.
    const std::uint16_t safePulse = std::clamp(microseconds, MIN_PULSE_US, MAX_PULSE_US);
    currentPulseUs_ = safePulse;
    timerRegs_.CCR1 = currentPulseUs_;
}

void ServoTester::setAngleDeg(float degrees) noexcept {
    const float clampedDeg = std::clamp(degrees, MIN_ANGLE_DEG, MAX_ANGLE_DEG);
    
    // Перерахунок кута 0..180° у час високого рівня 1000..2000 мкс
    const float ratio = clampedDeg / MAX_ANGLE_DEG;
    const auto pulseUs = static_cast<std::uint16_t>(
        MIN_PULSE_US + ratio * (MAX_PULSE_US - MIN_PULSE_US)
    );

    setPulseWidthUs(pulseUs);
}

float ServoTester::angleDeg() const noexcept {
    if (currentPulseUs_ <= MIN_PULSE_US) {
        return MIN_ANGLE_DEG;
    }
    const float pulseOffset = static_cast<float>(currentPulseUs_ - MIN_PULSE_US);
    const float totalRange = static_cast<float>(MAX_PULSE_US - MIN_PULSE_US);
    return (pulseOffset / totalRange) * MAX_ANGLE_DEG;
}

void ServoTester::calibrateNeutral() noexcept {
    // 1500 мкс — еталонна точка нейтралі для вистановки потенціометра серводрайвера
    setPulseWidthUs(NEUTRAL_PULSE_US);
}

} // namespace ServoControl
