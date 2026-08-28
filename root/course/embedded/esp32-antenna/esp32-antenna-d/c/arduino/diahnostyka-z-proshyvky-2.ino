#include <WiFi.h>

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
}

void loop() {
  int found = WiFi.scanNetworks();   // блокуючий скан усіх каналів
  Serial.printf("знайдено мереж: %d\n", found);

  int strong = 0;                    // скільки з них гучніші за −80 dBm
  for (int i = 0; i < found; i++) {
    int rssi = WiFi.RSSI(i);
    if (rssi > -80) strong++;
    Serial.printf("  %-24s  %4d dBm  ch%d\n",
                  WiFi.SSID(i).c_str(), rssi, WiFi.channel(i));
  }
  Serial.printf("з них упевнених (> −80 dBm): %d\n\n", strong);

  WiFi.scanDelete();                 // звільнити пам'ять результатів
  delay(5000);
}
