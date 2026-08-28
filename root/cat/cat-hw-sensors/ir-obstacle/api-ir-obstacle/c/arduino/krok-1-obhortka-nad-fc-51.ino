#include <Arduino.h>

class IrObstacle {
public:
  // pin      — цифровий вхід, куди йде OUT давача
  // debounceMs — скільки стан має протриматись, щоб його прийняти (мс)
  // usePullup  — чи вмикати внутрішню підтяжку (лікує «плаваючу» лінію)
  IrObstacle(uint8_t pin, uint16_t debounceMs = 8, bool usePullup = true)
    : _pin(pin), _debounceMs(debounceMs), _usePullup(usePullup) {}

  void begin() {
    pinMode(_pin, _usePullup ? INPUT_PULLUP : INPUT);
    // початковий стан читаємо одразу, щоб не «клацнути» на старті
    _rawLast   = readRaw();
    _stable     = _rawLast;
    _changedAt = millis();
  }

  // Викликати часто (кожен loop). Оновлює підтверджений стан.
  void update() {
    bool raw = readRaw();
    if (raw != _rawLast) {          // сирий стан щойно смикнувся
      _rawLast   = raw;
      _changedAt = millis();        // перезапускаємо відлік стабільності
    }
    // прийняти новий стан лише коли він протримався досить довго
    if (raw != _stable && (millis() - _changedAt) >= _debounceMs) {
      _stable = raw;
    }
  }

  // Чесна подія: true = перешкода поруч (інверсію вже враховано).
  bool obstacle() const { return _stable; }

private:
  // Сирий біт → логічна «перешкода»: активний нуль, тож LOW = true.
  bool readRaw() const { return digitalRead(_pin) == LOW; }

  uint8_t  _pin;
  uint16_t _debounceMs;
  bool     _usePullup;
  bool     _rawLast   = false;
  bool     _stable     = false;
  uint32_t _changedAt = 0;
};
