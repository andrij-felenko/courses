class IrObstacleEN {
public:
  // pinOut — вихід OUT; pinEN — пін EN (0xFF = немає, поведінка як FC-51)
  IrObstacleEN(uint8_t pinOut, uint8_t pinEN = 0xFF,
               uint16_t debounceMs = 8)
    : _pinOut(pinOut), _pinEN(pinEN), _debounceMs(debounceMs) {}

  void begin() {
    pinMode(_pinOut, INPUT_PULLUP);
    if (hasEN()) {
      pinMode(_pinEN, OUTPUT);
      digitalWrite(_pinEN, LOW);       // старт із вимкненою несучою
    }
    _rawLast = _stable = readRaw();
    _changedAt = _phaseAt = millis();
    _enHigh = false;
  }

  void update() {
    if (hasEN()) strobe();             // ведемо цикл EN, читаємо у слушну мить
    else         debounceOnly(readRaw());
  }

  bool obstacle() const { return _stable; }

private:
  static const uint16_t EN_ON_MS  = 1;   // вікно несучої (≤2 мс!)
  static const uint16_t EN_OFF_MS = 1;   // пауза для розслаблення AGC

  bool hasEN() const { return _pinEN != 0xFF; }
  bool readRaw() const { return digitalRead(_pinOut) == LOW; }

  // Неблокуюча машина станів для EN.
  void strobe() {
    uint32_t now = millis();
    if (_enHigh) {
      if (now - _phaseAt >= EN_ON_MS) {  // вікно скінчилось
        debounceOnly(readRaw());         // читаємо ПОКИ несуча ще була
        digitalWrite(_pinEN, LOW);       // гасимо несучу
        _enHigh = false;
        _phaseAt = now;
      }
    } else {
      if (now - _phaseAt >= EN_OFF_MS) { // пауза скінчилась
        digitalWrite(_pinEN, HIGH);      // пускаємо несучу знову
        _enHigh = true;
        _phaseAt = now;
      }
    }
  }

  // Придушення дрижання — те саме, що у FC-51.
  void debounceOnly(bool raw) {
    uint32_t now = millis();
    if (raw != _rawLast) { _rawLast = raw; _changedAt = now; }
    if (raw != _stable && (now - _changedAt) >= _debounceMs) _stable = raw;
  }

  uint8_t  _pinOut, _pinEN;
  uint16_t _debounceMs;
  bool     _rawLast = false, _stable = false, _enHigh = false;
  uint32_t _changedAt = 0, _phaseAt = 0;
};
