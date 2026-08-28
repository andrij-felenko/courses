const uint8_t PIN_PUMP = 8;    // ніжка керує реле помпи

const int LEVEL_ON  = 80;      // рівень вище цього → УВІМКНУТИ помпу (верхній поріг)
const int LEVEL_OFF = 60;      // рівень нижче цього → ВИМКНУТИ помпу (нижній поріг)

bool pumpOn = false;           // поточний стан помпи — частина рішення!

void updatePump(int level) {
  if (!pumpOn && level > LEVEL_ON)       pumpOn = true;    // води багато — качаємо
  else if (pumpOn && level < LEVEL_OFF)  pumpOn = false;   // води мало — стоп
  // якщо рівень між порогами — жодна умова не спрацює, стан лишається

  digitalWrite(PIN_PUMP, pumpOn ? HIGH : LOW);
}
