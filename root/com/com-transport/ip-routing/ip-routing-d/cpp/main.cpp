#include <WiFi.h>

// статична конфігурація: задаємо погляд пристрою на мережу
IPAddress ip     (192, 168, 1, 42);    // моя адреса
IPAddress mask   (255, 255, 255, 0);   // маска /24 — хто «свої»
IPAddress gateway(192, 168, 1, 1);     // шлюз — куди дівати «чужих» (default route)
IPAddress dns    (192, 168, 1, 1);

void setup() {
    Serial.begin(115200);
    WiFi.config(ip, gateway, mask, dns);   // ← цим трьома числами описано ВСЮ маршрутизацію вузла
    WiFi.begin("my-ssid", "my-pass");
    while (WiFi.status() != WL_CONNECTED) delay(200);

    // далі ми лише кажемо КУДИ (IP цілі) — а стек сам вирішить «прямо чи через шлюз»:
    //   ціль & mask == ip & mask  →  свій сегмент, шле прямо
    //   інакше                     →  кадр на MAC шлюза (gateway), пакет — на кінцеву IP
}

void loop() {
    // напр. WiFiClient до будь-якої IP: стек сам накладе маску, вибере рядок,
    // знайде MAC потрібного сусіда (цілі або шлюзу) і відправить кадр.
}
