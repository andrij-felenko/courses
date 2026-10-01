#include <ESP8266WiFi.h>

WiFiClient client;
uint8_t telemetryBuffer[512];
size_t bufferIndex = 0;

void configureSocket() {
  // Вимикаємо алгоритм Нагла для зменшення затримки latency
  client.setNoDelay(true);
}

void sendAggregatedSample(uint8_t sample) {
  telemetryBuffer[bufferIndex++] = sample;
  // Відправляємо накопичений payload при заповненні буфера
  if (bufferIndex >= sizeof(telemetryBuffer)) {
    client.write(telemetryBuffer, bufferIndex);
    bufferIndex = 0;
  }
}
