// Сторож порога з гістерезисом: вмикається на ON, вимикається на OFF (OFF < ON).
struct Hysteresis {
  float onLevel;      // поріг вмикання
  float offLevel;     // поріг вимикання (нижчий!)
  bool  state = false;

  // Подати нове значення, повернути стан тривоги.
  bool update(float value) {
    if (!state && value >= onLevel)  state = true;   // піднялись вище — вмикаємось
    if ( state && value <= offLevel) state = false;  // впали нижче — відпускаємо
    return state;                                    // між порогами — не міняємось
  }
};

// Наприклад, стерегти за ppm-еквівалентом LPG: тривога від 350, відбій нижче 250.
Hysteresis lpgWatch = { 350.0f, 250.0f };
