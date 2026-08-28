// ── KY026.h ──────────────────────────────────────────────────────────────
#pragma once
#include <Arduino.h>

class KY026 {
public:
  // pinDO / pinAO — піни; invertedDO=true, якщо спокій=HIGH, вогонь=LOW
  // (як на більшості модулів). debounceMs — скільки стан має протриматись.
  KY026(uint8_t pinDO, uint8_t pinAO, bool invertedDO = true,
        uint16_t debounceMs = 40)
    : _pinDO(pinDO), _pinAO(pinAO), _inverted(invertedDO),
      _debounceMs(debounceMs) {}

  void begin() {
    pinMode(_pinDO, INPUT);
    // AO — аналоговий, режим задавати не треба; поріг DO задає гвинтик на платі
    _stable   = rawFlame();      // початковий стан — той, що зараз
    _lastRaw  = _stable;
    _changedAt = millis();
  }

  // Сирий біт «поріг перейдено», уже розвернутий під інверсію.
  // true == є вогонь (за гвинтиком на платі), без придушення дрижання.
  bool rawFlame() const {
    int v = digitalRead(_pinDO);
    return _inverted ? (v == LOW) : (v == HIGH);
  }

  // Головний метод: викликай часто (у loop). Повертає СТАБІЛЬНИЙ стан
  // «є вогонь», що змінюється лише після витримки debounceMs.
  bool update() {
    bool now = rawFlame();
    if (now != _lastRaw) {          // сире значення сіпнулося — почни відлік
      _lastRaw   = now;
      _changedAt = millis();
    } else if (now != _stable &&
               (millis() - _changedAt) >= _debounceMs) {
      _stable = now;                // новий стан протримався — приймаємо
    }
    return _stable;
  }

  bool flame() const { return _stable; }   // останній стабільний стан

  int  strength() const { return analogRead(_pinAO); }  // сира сила жару

private:
  uint8_t  _pinDO, _pinAO;
  bool     _inverted;
  uint16_t _debounceMs;
  bool     _stable = false, _lastRaw = false;
  uint32_t _changedAt = 0;
};
