// DO на D2, AO на A0; DO інвертований (звірено по індикаторному світлодіоду).
KY026 sensor(2, A0, /*invertedDO=*/true, /*debounceMs=*/40);

void setup() {
  Serial.begin(9600);
  sensor.begin();
}

void loop() {
  bool flame = sensor.update();          // стабільний стан, без дрижання
  int  ir    = sensor.strength();        // сира сила жару, якщо треба
  Serial.print(flame ? "ВОГОНЬ  " : "спокій  ");
  Serial.println(ir);
  delay(10);                             // update() любить, щоб її кликали часто
}
