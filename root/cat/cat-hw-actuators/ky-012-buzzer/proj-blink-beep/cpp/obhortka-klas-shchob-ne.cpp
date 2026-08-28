// --- Buzzer: неблокуючий драйвер активного зумера (KY-012 і подібних) ---
// Керує ЛИШЕ ввімкненням/вимкненням: висоту тону активного зумера змінити не можна.
class Buzzer {
public:
  explicit Buzzer(uint8_t pin) : _pin(pin) {}

  void begin() {
    pinMode(_pin, OUTPUT);
    _write(false);
  }

  // Один біп на ms мілісекунд.
  void beep(unsigned int ms) {
    _mode  = ONESHOT;
    _write(true);
    _until = millis() + ms;
  }

  // Серія з n біпів по half мс на півфазу (біп / пауза), тоді сама затихає.
  void series(uint8_t n, unsigned long half) {
    _mode  = SERIES;
    _left  = n * 2;                // n біпів = 2·n перемикань
    _half  = half;
    _last  = millis();
    _write(true);
  }

  // Безперервний тон, доки не викличеш stop(). Для тривоги.
  void on()  { _mode = SOLID; _write(true);  }
  void stop() { _mode = SOLID; _write(false); }

  bool busy() const { return _mode == SERIES && _left > 0; }

  // Смикати в КОЖНОМУ loop(). Нічого не блокує.
  void update() {
    unsigned long now = millis();

    if (_mode == ONESHOT) {
      if (_isOn && (long)(now - _until) >= 0) { _write(false); _mode = SOLID; }
      return;
    }
    if (_mode == SERIES) {
      if (_left > 0 && now - _last >= _half) {
        _last = now;
        _left--;
        if (_left == 0) { _write(false); _mode = SOLID; }  // серія добігла — тиша
        else            { _write(!_isOn); }
      }
      return;
    }
    // SOLID — нічого рахувати: тримаємо заданий стан
  }

private:
  enum Mode { SOLID, ONESHOT, SERIES };

  void _write(bool onState) {
    _isOn = onState;
    digitalWrite(_pin, onState ? HIGH : LOW);   // HIGH-тригер: HIGH пищить
  }

  uint8_t       _pin;
  Mode          _mode  = SOLID;
  bool          _isOn  = false;
  unsigned long _until = 0, _last = 0, _half = 100;
  uint8_t       _left  = 0;
};

// ---------- використання ----------
Buzzer buz(8);                      // модуль на D8
const uint8_t PIN_BTN = 2;

void setup() {
  buz.begin();
  pinMode(PIN_BTN, INPUT_PULLUP);
}

void loop() {
  static bool wasPressed = false;
  bool pressed = (digitalRead(PIN_BTN) == LOW);
  if (pressed && !wasPressed && !buz.busy()) {
    buz.series(3, 100);             // натиск → три біпи на помилку
  }
  wasPressed = pressed;

  buz.update();                     // єдиний обов'язок: смикати щоцикл
  // ...тут будь-яка інша логіка скетчу, вона не блокована
}
