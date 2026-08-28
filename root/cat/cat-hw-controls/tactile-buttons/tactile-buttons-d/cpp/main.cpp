const uint8_t PIN_BTN = 2;    // вивід кнопки; другий вивід — на GND
const uint8_t PIN_LED = 13;

bool ledOn = false;           // поточний стан світлодіода
bool prev  = HIGH;            // попередній рівень піна (HIGH = відпущено)

void setup() {
  pinMode(PIN_BTN, INPUT_PULLUP);  // підтяжка до плюса: спокій = HIGH
  pinMode(PIN_LED, OUTPUT);
}

void loop() {
  bool now = digitalRead(PIN_BTN);        // LOW = натиснуто, HIGH = відпущено
  if (prev == HIGH && now == LOW) {       // спіймали перехід «відпущено → натиснуто»
    ledOn = !ledOn;                       // перемкнули стан на фронті натиску
    digitalWrite(PIN_LED, ledOn);
    delay(20);                            // груба пауза, щоб проскочити брязкіт
  }
  prev = now;
}
