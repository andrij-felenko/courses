// ── KY040.h ─────────────────────────────────────────────────────────────────
#pragma once
#include <Arduino.h>

class KY040 {
public:
  KY040(uint8_t pinClk, uint8_t pinDt, uint8_t pinSw)
    : _clk(pinClk), _dt(pinDt), _sw(pinSw) {}

  void begin() {
    pinMode(_clk, INPUT);            // на платі KY-040 підтяжки CLK/DT вже стоять
    pinMode(_dt,  INPUT);
    pinMode(_sw,  INPUT_PULLUP);     // а на кнопці підтяжки нема — вмикаємо внутрішню
  }

  // Викликати ЯКОМОГА ЧАСТІШЕ: з loop() (опитування) або з обробника краю CLK/DT.
  // Оновлює лічильник; тримати короткою — придатна для переривання.
  void tick() {
    // повнокрокова таблиця Бакстона (крок раз на клац фіксатора);
    // локальна static — жодних клопотів з окремим визначенням члена класу
    static const uint8_t T[7][4] = {
      {0x0, 0x2, 0x4, 0x0},              // R_START
      {0x3, 0x0, 0x1, 0x0 | 0x10},       // R_CW_FINAL  → DIR_CW
      {0x3, 0x2, 0x0, 0x0},              // R_CW_BEGIN
      {0x3, 0x2, 0x1, 0x0},              // R_CW_NEXT
      {0x6, 0x0, 0x4, 0x0},              // R_CCW_BEGIN
      {0x6, 0x5, 0x0, 0x0 | 0x20},       // R_CCW_FINAL → DIR_CCW
      {0x6, 0x5, 0x4, 0x0},              // R_CCW_NEXT
    };
    uint8_t pin = (digitalRead(_clk) << 1) | digitalRead(_dt);
    _state = T[_state & 0x0F][pin];
    uint8_t dir = _state & 0x30;
    if      (dir == 0x10) _count++;      // DIR_CW
    else if (dir == 0x20) _count--;      // DIR_CCW
  }

  // Накопичене значення. atomic-читання для 8-бітних платформ.
  long position() const {
    noInterrupts();
    long v = _count;
    interrupts();
    return v;
  }
  void  setPosition(long v) { noInterrupts(); _count = v; interrupts(); }

  // true РІВНО раз на кожен натиск кнопки (з дебаунсом). Кликати з loop().
  bool pressed() {
    bool now = digitalRead(_sw);
    if (now != _swPrev && (millis() - _swMs) > SW_DEBOUNCE) {
      _swMs   = millis();
      _swPrev = now;
      if (now == LOW) return true;
    }
    return false;
  }

private:
  const uint8_t _clk, _dt, _sw;
  volatile long _count  = 0;
  volatile uint8_t _state = 0;         // R_START

  bool          _swPrev = HIGH;
  unsigned long _swMs   = 0;
  static const unsigned long SW_DEBOUNCE = 30;
};
