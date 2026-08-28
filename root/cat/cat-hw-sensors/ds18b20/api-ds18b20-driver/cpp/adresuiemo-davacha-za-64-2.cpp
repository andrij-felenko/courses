// Коди конкретних давачів, зчитані попереднім скетчем і підписані фізично.
DeviceAddress SENSOR_TANK = { 0x28, 0xFF, 0x64, 0x1E, 0x8A, 0x12, 0x03, 0xDC };
DeviceAddress SENSOR_PIPE = { 0x28, 0xAA, 0x1B, 0x55, 0x0C, 0x00, 0x00, 0x9F };

void loop() {
  sensors.requestTemperatures();                    // виміряти всім одразу

  float tTank = sensors.getTempC(SENSOR_TANK);      // забрати за КОДОМ, не індексом
  float tPipe = sensors.getTempC(SENSOR_PIPE);

  if (tTank != DEVICE_DISCONNECTED_C)
    Serial.printf("Бак:  %.2f C\n", tTank);
  if (tPipe != DEVICE_DISCONNECTED_C)
    Serial.printf("Труба: %.2f C\n", tPipe);

  delay(1000);
}
