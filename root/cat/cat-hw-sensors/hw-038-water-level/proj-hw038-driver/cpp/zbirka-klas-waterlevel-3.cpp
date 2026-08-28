// таблиця під ESP32: відліки 0..4095, зібрані на СВОЇЙ воді при 3.3 В
const CalPoint TABLE[] = {
  {120, 0}, {900, 25}, {1800, 50}, {2700, 75}, {3400, 100}
};

WaterLevel sensor(25, 34, 26,      // живлення GPIO25, сигнал GPIO34 (ADC1!), помпа GPIO26
                  TABLE, 5,
                  80, 60);

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);        // 0..4095 (типове для ESP32)
  sensor.begin();
}

void loop() {
  int level = sensor.update();
  Serial.printf("рівень %d %%  %s\n", level, sensor.isPumpOn() ? "ПОМПА ON" : "помпа off");
  delay(2000);
}
