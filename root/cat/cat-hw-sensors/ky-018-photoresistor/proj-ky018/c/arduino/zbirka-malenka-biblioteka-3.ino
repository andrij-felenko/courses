LightSensor sensor(34, 0.2f, 30, 45);   // GPIO34 — канал ADC1 (див. розділ про ESP32!)

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);             // 0..4095 (типове для ESP32)
  sensor.begin(4095);                   // 12-бітний АЦП
  sensor.calibrate(5);
}

void loop() {
  sensor.update();
  Serial.printf("яскравість %u %%  %s\n",
                sensor.percent(), sensor.isDark() ? "ТЕМНО" : "світло");
  delay(50);
}
