// ── Potentiometer: читання повзунка з EMA-згладжуванням, калібруванням і мертвою зоною.
//    Готовий до вставки в проєкт. Arduino / ESP32 (див. ADC_MAX нижче).
#if defined(ESP32)
  static const int ADC_MAX = 4095;   // 12 біт
#else
  static const int ADC_MAX = 1023;   // 10 біт
#endif

class Potentiometer {
public:
  Potentiometer(uint8_t pin, uint8_t shift = 4, int deadband = 4)
    : _pin(pin), _shift(shift), _deadband(deadband),
      _calMin(ADC_MAX), _calMax(0), _lastAccepted(-10000), _ema(0) {}

  // Викликати раз у setup(): ініціалізувати фільтр першим відліком.
  void begin() {
    _ema = (long)analogRead(_pin) << _shift;
  }

  // Викликати в циклі, поки користувач крутить ручку від упору до упору (кілька секунд).
  void calibrate() {
    int v = raw();                   // калібруємо по ЗГЛАДЖЕНОМУ, не по сирому
    if (v < _calMin) _calMin = v;
    if (v > _calMax) _calMax = v;
  }

  // Якщо калібрування не робимо — вважаємо краї повним ходом АЦП.
  void useFullRange() { _calMin = 0; _calMax = ADC_MAX; }

  // Згладжене СИРЕ значення 0..ADC_MAX (оновлює фільтр). Основа для решти.
  int raw() {
    int  r = analogRead(_pin);
    long delta = ((long)r << _shift) - _ema;
    _ema += (delta >> _shift);
    return (int)((_ema + (1 << (_shift - 1))) >> _shift);   // з округленням
  }

  // Згладжене й КАЛІБРОВАНЕ значення, лінійно перекладене в [outLo..outHi].
  // Напрямок задають самі межі: outLo>outHi → інверсія.
  int value(int outLo = 0, int outHi = 100) {
    int v  = map(raw(), _calMin, _calMax, outLo, outHi);
    int lo = min(outLo, outHi), hi = max(outLo, outHi);     // затиснути незалежно від порядку меж
    return constrain(v, lo, hi);
  }

  // true й записує *out, ЛИШЕ коли значення відійшло від прийнятого далі за мертву зону.
  // Мертва зона працює в СИРИХ одиницях, тож стабільна незалежно від масштабу виходу.
  bool changed(int *out, int outLo = 0, int outHi = 100) {
    int rawNow = raw();
    if (abs(rawNow - _lastAccepted) >= _deadband) {
      _lastAccepted = rawNow;
      int lo = min(outLo, outHi), hi = max(outLo, outHi);
      *out = constrain(map(rawNow, _calMin, _calMax, outLo, outHi), lo, hi);
      return true;
    }
    return false;
  }

private:
  uint8_t _pin, _shift;
  int     _deadband, _calMin, _calMax, _lastAccepted;
  long    _ema;                      // стан EMA у масштабі ×2^_shift
};
