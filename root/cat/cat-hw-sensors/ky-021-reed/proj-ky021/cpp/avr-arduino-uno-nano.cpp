#include <avr/sleep.h>
#include <avr/interrupt.h>

const uint8_t PIN_REED = 2;              // INT0

inline bool magnetPresent(uint8_t pin) { return digitalRead(pin) == LOW; }

void onWake() {
  // порожньо: сам факт переривання будить чип; діло робимо в loop()
}

void goToSleep() {
  ADCSRA &= ~(1 << ADEN);                // вимкнути АЦП — інакше він їсть струм і уві сні
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);   // найглибший сон, тактовий генератор стане
  cli();                                  // без переривань, поки готуємось (без гонки)
  sleep_enable();
  // у power-down доступний лише РІВЕНЬ. Озброюємось на НИЗЬКИЙ (пін LOW).
  // зараз магніту нема → пін HIGH → умова не виконана, тож чип спокійно засне;
  // переривання вистрелить згодом, коли геркон замкне пін у LOW.
  attachInterrupt(digitalPinToInterrupt(PIN_REED), onWake, LOW);
  sei();                                  // тепер переривання дозволені
  sleep_cpu();                            // ← ЧИП ЗАСИНАЄ ТУТ

  // ---- прокинулись (геркон замкнув пін у LOW): продовжуємо звідси ----
  sleep_disable();
  detachInterrupt(digitalPinToInterrupt(PIN_REED));
}

void setup() {
  pinMode(PIN_REED, INPUT);              // підтяжка на платі тримає рівні чіткими
  Serial.begin(9600);
  Serial.println("старт: засинаю, чекаю на замикання геркона");
  Serial.flush();
  goToSleep();                           // одразу в сон — до першого замикання
}

void loop() {
  // сюди виконання потрапляє ЩОЙНО прокинулись: геркон замкнувся
  Serial.println("прокинувся: геркон замкнувся (магніт поряд)!");
  Serial.flush();                        // дочекатись, поки байти підуть у порт
  // ... тут корисне діло: тривога по радіо, інкремент лічби, запис часу ...

  // поки магніт біля геркона (пін LOW), у power-down лягати НЕ МОЖНА:
  // рівневе переривання підняло б нас миттєво. Чекаємо, доки магніт поїде.
  while (magnetPresent(PIN_REED)) delay(20);

  goToSleep();                           // магніт поїхав (пін HIGH) — спимо далі
}
