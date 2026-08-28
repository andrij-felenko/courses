const uint8_t PIN_BTN = 2;
uint8_t idle;                    // рівень спокою — визначимо на старті
long presses = 0;

void setup() {
  pinMode(PIN_BTN, INPUT);       // KY-004 має підтяжку на платі
  Serial.begin(9600);
  delay(20);                     // дати лінії влягтися
  idle = digitalRead(PIN_BTN);   // що читається у спокої — те й «не натиснуто»
  // idle==LOW → плата pull-down;  idle==HIGH → плата pull-up. Далі байдуже.
}

void loop() {
  static uint8_t last = idle;    // попередній усталений стан
  uint8_t now = digitalRead(PIN_BTN);

  if (now != last) {             // рівень змінився — можливо, натиск або брязкіт
    delay(15);                   // антибрязкіт: чекаємо, поки контакт устоїться
    now = digitalRead(PIN_BTN);  // перечитуємо усталений рівень
    if (now != last) {           // зміна справжня
      last = now;
      if (now != idle) {         // перейшли зі стану спокою — це НАТИСК
        presses++;
        Serial.println(presses);
      }
    }
  }
}
