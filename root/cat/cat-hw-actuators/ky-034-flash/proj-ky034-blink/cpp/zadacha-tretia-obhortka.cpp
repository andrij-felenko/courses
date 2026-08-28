// --- Ky034: неблокуючий драйвер увімкнення для самограйного RGB-модуля ---
// Керує ЛИШЕ ввімкненням/вимкненням (кольором KY-034 керувати не можна).
class Ky034 {
public:
  explicit Ky034(uint8_t pin) : _pin(pin) {}

  void begin() {
    pinMode(_pin, OUTPUT);
    off();
  }

  // Постійно ввімкнути / вимкнути (скидає будь-який активний режим блимання)
  void on()  { _mode = SOLID; _write(true);  }
  void off() { _mode = SOLID; _write(false); }

  // Рівне блимання: onMs горить, offMs згас, доти доки не змінять режим
  void blink(unsigned long onMs, unsigned long offMs) {
    _onMs = onMs; _offMs = offMs;
    _mode = BLINK;
    _last = millis();
    _write(true);
  }

  // Пачка з n спалахів по halfMs на півфазу, тоді сама затихає
  void burst(uint8_t n, unsigned long halfMs) {
    _left = n * 2;                 // n спалахів = 2·n перемикань
    _halfMs = halfMs;
    _mode = BURST;
    _last = millis();
    _write(true);
  }

  bool busy() const { return _mode == BURST && _left > 0; }

  // Смикати в КОЖНОМУ loop(). Нічого не блокує.
  void tick() {
    if (_mode == SOLID) return;                 // постійний стан — нічого рахувати
    unsigned long now = millis();

    if (_mode == BLINK) {
      unsigned long phase = _isOn ? _onMs : _offMs;
      if (now - _last >= phase) {
        _last = now;
        _write(!_isOn);
      }
      return;
    }

    // BURST
    if (_left > 0 && now - _last >= _halfMs) {
      _last = now;
      _left--;
      if (_left == 0) { _write(false); _mode = SOLID; }  // пачка добігла — гасимо
      else            { _write(!_isOn); }
    }
  }

private:
  enum Mode { SOLID, BLINK, BURST };

  void _write(bool onState) {
    _isOn = onState;
    digitalWrite(_pin, onState ? HIGH : LOW);
  }

  uint8_t       _pin;
  Mode          _mode  = SOLID;
  bool          _isOn  = false;
  unsigned long _last  = 0;
  unsigned long _onMs  = 500, _offMs = 500, _halfMs = 200;
  uint8_t       _left  = 0;
};

// ---------- використання ----------
Ky034 lamp(8);                          // модуль на D8
const uint8_t PIN_BTN = 2;

void setup() {
  lamp.begin();
  pinMode(PIN_BTN, INPUT_PULLUP);
  lamp.blink(500, 500);                 // за замовчуванням — рівно блимає тлом
}

void loop() {
  static bool wasPressed = false;
  bool pressed = (digitalRead(PIN_BTN) == LOW);
  if (pressed && !wasPressed && !lamp.busy()) {
    lamp.burst(3, 150);                 // натиск → блимнути тричі поверх усього
  }
  wasPressed = pressed;

  lamp.tick();                          // єдиний обов'язок: смикати щоцикл
  // ...тут будь-яка інша логіка скетчу, вона не блокована
}
