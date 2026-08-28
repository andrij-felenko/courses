#include <WiFi.h>
#include <esp_now.h>

// MAC приймача — його друкує сам приймач у себе в консолі (WiFi.macAddress)
uint8_t peerMac[6] = { 0x24, 0x6F, 0x28, 0x11, 0x22, 0x33 };
const int BTN = 0;   // кнопка на GPIO0

// callback: спрацьовує після КОЖНОГО відправлення й каже лише MAC-статус
void onSent(const uint8_t* mac, esp_now_send_status_t status) {
  // SUCCESS = радіо приймача квитнуло кадр; НЕ = «застосунок обробив»
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "ACK" : "нема ACK");
}

void setup() {
  Serial.begin(115200);
  pinMode(BTN, INPUT_PULLUP);
  WiFi.mode(WIFI_STA);          // радіо вмикаємо, але до мережі НЕ приєднуємось
  esp_now_init();               // піднімаємо ESP-NOW — усе, інфраструктура не потрібна
  esp_now_register_send_cb(onSent);

  esp_now_peer_info_t peer = {};        // опис одноліток
  memcpy(peer.peer_addr, peerMac, 6);   // кому слатимемо — за MAC
  peer.channel = 0;                     // 0 = поточний канал радіо
  peer.encrypt = false;                 // без шифрування (домашній стенд)
  esp_now_add_peer(&peer);              // додати до списку пар
}

void loop() {
  static bool prev = true;
  bool pressed = (digitalRead(BTN) == LOW);
  if (pressed != prev) {                // стан кнопки змінився
    uint8_t cmd = pressed ? 1 : 0;      // один байт: 1 увімкнути, 0 вимкнути
    esp_now_send(peerMac, &cmd, 1);     // відправити кадр саме цьому MAC
    prev = pressed;
  }
  delay(20);                            // проста антидеренчна пауза
}
