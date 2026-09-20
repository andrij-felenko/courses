#include "TriacDriver.h"

TriacDriver::TriacDriver(uint8_t pin, bool activeHigh)
    : pin_(pin),
      activeHigh_(activeHigh),
      isOn_(false),
      startTimeMs_(0),
      durationMs_(0),
      timerActive_(false) {
}

void TriacDriver::begin() {
    // БЕЗПЕКА: Спочатку виставляємо вихідний регістр у стан "ВИМКНЕНО".
    // Це гарантує, що при виконанні pinMode(..., OUTPUT) на пині одразу
    // з'явиться безпечний рівень, і не виникне імпульсу хибного відкриття симістора BTA16.
    uint8_t offLevel = activeHigh_ ? LOW : HIGH;
    digitalWrite(pin_, offLevel);
    pinMode(pin_, OUTPUT);

    // Додатково фіксуємо внутрішній стан
    isOn_ = false;
    timerActive_ = false;
}

void TriacDriver::applyState(bool state) {
    isOn_ = state;
    uint8_t level = (isOn_ == activeHigh_) ? HIGH : LOW;
    digitalWrite(pin_, level);
}

void TriacDriver::turnOn() {
    timerActive_ = false; // Скасовуємо таймер автовимкнення при ручному ввімкненні
    applyState(true);
}

void TriacDriver::turnOff() {
    timerActive_ = false; // Скасовуємо таймер автовимкнення
    applyState(false);
}

void TriacDriver::toggle() {
    timerActive_ = false;
    applyState(!isOn_);
}

void TriacDriver::turnOnFor(uint32_t durationMs) {
    if (durationMs == 0) {
        turnOff();
        return;
    }

    applyState(true);
    startTimeMs_ = millis();
    durationMs_ = durationMs;
    timerActive_ = true;
}

void TriacDriver::update() {
    // Безпечна перевірка неблокуючого таймера з урахуванням переповнення millis()
    if (timerActive_) {
        uint32_t elapsed = millis() - startTimeMs_;
        if (elapsed >= durationMs_) {
            timerActive_ = false;
            applyState(false); // Автоматичне вимкнення навантаження
        }
    }
}

bool TriacDriver::isOn() const {
    return isOn_;
}

bool TriacDriver::isTimerActive() const {
    return timerActive_;
}

uint32_t TriacDriver::getRemainingTimeMs() const {
    if (!timerActive_) {
        return 0;
    }

    uint32_t elapsed = millis() - startTimeMs_;
    if (elapsed >= durationMs_) {
        return 0;
    }

    return durationMs_ - elapsed;
}
