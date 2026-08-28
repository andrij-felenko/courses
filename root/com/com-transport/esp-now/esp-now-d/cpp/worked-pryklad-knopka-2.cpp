#include <WiFi.h>
#include <esp_now.h>

const int LAMP = 2;   // лампа на GPIO2

// callback: стек гукає його на КОЖЕН вхідний кадр ESP-NOW
void onRecv(const esp_now_recv_info_t* info, const uint8_t* data, int len) {
  if (len < 1) return;                  // порожній кадр — ігноруємо
  digitalWrite(LAMP, data[0] ? HIGH : LOW);   // перший байт керує лампою
}

void setup() {
  Serial.begin(115200);
  pinMode(LAMP, OUTPUT);
  WiFi.mode(WIFI_STA);
  Serial.println(WiFi.macAddress());    // ← цей MAC вписуємо в peerMac передавача
  esp_now_init();
  esp_now_register_recv_cb(onRecv);     // усе: тепер кадри приходять у onRecv
}

void loop() {
  // порожньо: уся робота — у callback, коли приходить кадр
}
