const uint8_t PIN_SW = 2;              // на Uno/Nano переривання лише на пінах 2 і 3!

volatile bool shockFlag = false;       // прапорець «була подія»; volatile — обов'язково

void isrShock() {                       // обробник: викликається апаратно на фронті
  shockFlag = true;                     // лише підняти прапорець — і нічого більше
}

void setup() {
  pinMode(PIN_SW, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_SW), isrShock, FALLING);
  Serial.begin(115200);
}

void loop() {
  if (shockFlag) {
    shockFlag = false;                  // погасити прапорець до наступної події
    Serial.println("прокинулись від струсу!");
    // ... тут — реакція: увімкнути, записати, послати сигнал ...
  }
  // ... а тут МК може заснути до наступного переривання ...
}
