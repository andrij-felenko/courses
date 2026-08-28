// ── FlameFlicker: детектор пульсації полумʼя за перетинами середнього ──────
// Ідея: полумʼя мерехтить на ~2..20 Гц; сонце/лампа світять рівно.
// Рахуємо, скільки разів за вікно сигнал AO перетнув своє повільне середнє
// знизу вгору → це частота мерехтіння в Гц. Є пульсація в смузі → вогонь.
class FlameFlicker {
public:
  FlameFlicker(uint8_t pinAO, float loFlickHz = 2.0f, float hiFlickHz = 20.0f)
    : _pinAO(pinAO), _lo(loFlickHz), _hi(hiFlickHz) {}

  void begin() {
    _mean = analogRead(_pinAO);   // старт середнього — з поточного рівня
    _prevAbove = false;
    _crossings = 0;
    _winStart  = millis();
    _lastFreq  = 0.0f;
  }

  // Кликати ДУЖЕ часто (ціль ~200 Гц вибірки). Раз на вікно оновлює частоту.
  void sample() {
    int v = analogRead(_pinAO);

    // Повільне середнє (експоненційне згладжування): йде за рівнем, не за пульсом.
    // alpha малий → середнє «важке», реагує на секунди, ігнорує пульс на 10 Гц.
    const float alpha = 0.02f;
    _mean += alpha * (v - _mean);

    // Перетин середнього знизу вгору — як тригер Шмітта, з зоною нечутливості
    // проти шуму: рахуємо перехід, лише коли сигнал піднявся вище (_mean+_hyst);
    // повторно «зводимося» тільки після падіння нижче (_mean-_hyst). У самій
    // зоні між порогами стан НЕ міняється — тому дрібний шум не накручує лічильник.
    if (!_prevAbove && v > _mean + _hyst) {   // піднялися вище верхнього порога
      _crossings++;
      _prevAbove = true;                      // взвели — до падіння нижче не рахуємо
    } else if (_prevAbove && v < _mean - _hyst) {
      _prevAbove = false;                     // впали нижче нижнього — знову готові
    }

    // Раз на вікно — переводимо кількість перетинів у частоту.
    uint32_t now = millis();
    uint32_t dt  = now - _winStart;
    if (dt >= _windowMs) {
      _lastFreq = (_crossings * 1000.0f) / dt;   // перетинів за секунду = Гц
      _crossings = 0;
      _winStart  = now;
    }
  }

  float freq()   const { return _lastFreq; }                 // Гц мерехтіння
  bool  flame()  const { return _lastFreq >= _lo && _lastFreq <= _hi; }
  int   level()  const { return (int)_mean; }                // середній рівень ІЧ

private:
  uint8_t  _pinAO;
  float    _lo, _hi;
  float    _mean = 0;
  float    _hyst = 8.0f;      // зона нечутливості (сирі одиниці АЦП)
  bool     _prevAbove = false;
  uint16_t _crossings = 0;
  uint32_t _winStart  = 0;
  const uint16_t _windowMs = 1000;   // вікно виміру частоти
  float    _lastFreq = 0.0f;
};
