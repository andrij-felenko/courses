LightSensor sensor(A0, 0.2f, 30, 45);   // пін A0, α=0.2, пороги 30/45 %

void setup() {
  Serial.begin(9600);
  pinMode(13, OUTPUT);
  sensor.begin(1023);                   // 10-бітний АЦП Uno
  Serial.println("Калібрування: 5 с крутіть освітлення...");
  sensor.calibrate(5);
}

void loop() {
  sensor.update();                      // оновити фільтр
  uint8_t pct = sensor.percent();
  bool dark = sensor.isDark();
  digitalWrite(13, dark ? HIGH : LOW);  // вбудований світлодіод у темряві
  Serial.print("яскравість "); Serial.print(pct); Serial.print(" %  ");
  Serial.println(dark ? "ТЕМНО" : "світло");
  delay(50);
}
