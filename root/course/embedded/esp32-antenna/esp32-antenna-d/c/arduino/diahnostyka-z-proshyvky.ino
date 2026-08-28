#include <WiFi.h>

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.begin("my-ssid", "my-pass");

  while (WiFi.status() != WL_CONNECTED) {
    delay(200);
    Serial.print('.');
  }
  Serial.printf("\nПідключено, RSSI = %d dBm\n", WiFi.RSSI());
}

void loop() {
  // антенний «стетоскоп»: 10 замірів RSSI з інтервалом,
  // щоб побачити середнє й розкид — рука/метал одразу видно
  long sum = 0;
  int  n   = 10;
  for (int i = 0; i < n; i++) {
    sum += WiFi.RSSI();
    delay(100);
  }
  Serial.printf("середній RSSI за %d замірів: %ld dBm\n", n, sum / n);
  delay(1000);
}
