// ULN2003: клацаємо реле раз на секунду через канал 1.
// Нога 8 → IN1 (вивід 1 чипа). Реле: +5V → обмотка → OUT1 (вивід 16).
// COM (вивід 9) → +5V живлення реле — обов'язково, це вмикає гасильний діод.
const int RELAY_CH = 8;   // нога МК, що керує входом каналу 1

void setup() {
  pinMode(RELAY_CH, OUTPUT);
}

void loop() {
  digitalWrite(RELAY_CH, HIGH);   // «1» на IN1 → OUT1 сідає на землю → реле спрацьовує
  delay(1000);
  digitalWrite(RELAY_CH, LOW);    // «0» → OUT1 відпускається → реле відпускає
  delay(1000);
}
