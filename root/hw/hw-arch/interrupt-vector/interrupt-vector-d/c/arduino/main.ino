volatile bool pressed = false;        // volatile: ISR і цикл бачать ту саму змінну

void IRAM_ATTR onButton() {           // IRAM_ATTR: код обробника тримати в RAM
  pressed = true;                     // одна дешева дія — і все
}

void setup() {
  Serial.begin(115200);
  pinMode(0, INPUT_PULLUP);           // підтяжка догори: у спокої вхід високий
  attachInterrupt(digitalPinToInterrupt(0), onButton, FALLING);
}

void loop() {
  if (pressed) {                      // важку роботу робимо ТУТ, поза ISR
    pressed = false;
    Serial.println("кнопку натиснуто");
  }
}
