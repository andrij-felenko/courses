// KY-012 активний зумер.  S → пін 8;  − → GND;  середній штир — нікуди.
const int BUZZER = 8;

void setup() {
  pinMode(BUZZER, OUTPUT);   // сигнальний штир — як звичайний вихід
}

void loop() {
  digitalWrite(BUZZER, HIGH); // подали одиницю → транзистор відкрився → пищить (~2.5 кГц)
  delay(200);                 // 0.2 с звуку
  digitalWrite(BUZZER, LOW);  // забрали → тиша
  delay(1800);                // 1.8 с паузи — виходить «біп» раз на 2 секунди
}
