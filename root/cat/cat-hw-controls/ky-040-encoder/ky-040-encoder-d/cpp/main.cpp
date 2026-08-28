const uint8_t PIN_CLK = 2;       // квадратурна доріжка A
const uint8_t PIN_DT  = 3;       // квадратурна доріжка B
const uint8_t PIN_SW  = 4;       // кнопка під валом

volatile long counter = 0;       // накопичене значення (змінюється в перериванні)

void onClkFall() {
  // спрацювало на спадному краї CLK: у цю мить рівень DT каже напрям
  if (digitalRead(PIN_DT) == HIGH) counter++;   // DT ще «1» → за годинниковою
  else                             counter--;   // DT уже «0» → проти
}

void setup() {
  pinMode(PIN_CLK, INPUT);       // на платі вже є підтяжка на CLK
  pinMode(PIN_DT,  INPUT);       // і на DT
  pinMode(PIN_SW,  INPUT_PULLUP);// а на кнопці підтяжки НЕМА — вмикаємо внутрішню
  attachInterrupt(digitalPinToInterrupt(PIN_CLK), onClkFall, FALLING);
  Serial.begin(9600);
}

void loop() {
  static long shown = 0;
  if (counter != shown) {        // друкуємо, лише коли значення змінилось
    shown = counter;
    Serial.println(shown);
  }
  if (digitalRead(PIN_SW) == LOW) counter = 0;   // натиск = скидання (LOW, бо pull-up)
}
