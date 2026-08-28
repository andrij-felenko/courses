// Button.h — неблокуюча обгортка кнопки під KY-004 (і будь-яку іншу).
// Сама визначає полярність (спокій на старті), гасить брязкіт,
// віддає події «натиснуто/відпущено» й детектить довгий натиск.
#pragma once
#include <Arduino.h>

class Button {
public:
  // pin — цифровий вивід із сигналом; debounceMs — вікно антибрязкоту;
  // longMs — поріг довгого натиску (0 → детект вимкнено).
  Button(uint8_t pin, uint16_t debounceMs = 15, uint16_t longMs = 800)
    : _pin(pin), _debounce(debounceMs), _long(longMs) {}

  // Викликати один раз у setup(). Пін — як INPUT: підтяжка вже на платі KY-004.
  void begin() {
    pinMode(_pin, INPUT);
    delay(2);                        // дати лінії влягтися перед зчитуванням спокою
    _idle    = digitalRead(_pin);    // рівень спокою → еталон «відпущено»
    _stable  = _idle;                // усталений стан стартує зі спокою
    _reading = _idle;
    _changed = millis();
    _pressedNow = _releasedNow = _longNow = false;
    _longFired  = false;
  }

  // Викликати ЧАСТО (щопрохід loop). Не блокує. Оновлює стан і зводить події.
  void update() {
    _pressedNow = _releasedNow = _longNow = false;   // події живуть один прохід
    uint32_t now = millis();
    uint8_t raw = digitalRead(_pin);

    if (raw != _reading) {           // сирий рівень смикнувся — почати відлік вікна
      _reading = raw;
      _changed = now;
    }

    // рівень протримався стабільно ціле вікно → визнати його усталеним
    if ((uint32_t)(now - _changed) >= _debounce && raw != _stable) {
      _stable = raw;
      if (_stable != _idle) {        // перейшли зі спокою → НАТИСК
        _pressedNow = true;
        _pressStart = now;
        _longFired  = false;
      } else {                       // повернулися у спокій → ВІДПУЩЕНО
        _releasedNow = true;
      }
    }

    // довгий натиск: кнопка усталено натиснута довше за поріг — раз на утримання
    if (_long && isPressed() && !_longFired &&
        (uint32_t)(now - _pressStart) >= _long) {
      _longNow   = true;
      _longFired = true;
    }
  }

  // ── Питання назовні ────────────────────────────────────────────────
  bool isPressed()  const { return _stable != _idle; }  // усталений стан «натиснуто»
  bool pressed()    const { return _pressedNow;  }       // мить натиску (1 прохід)
  bool released()   const { return _releasedNow; }       // мить відпускання
  bool longPress()  const { return _longNow;     }       // щойно перетнули поріг утримання

private:
  uint8_t  _pin, _idle = LOW, _stable = LOW, _reading = LOW;
  uint16_t _debounce, _long;
  uint32_t _changed = 0, _pressStart = 0;
  bool _pressedNow = false, _releasedNow = false, _longNow = false, _longFired = false;
};
