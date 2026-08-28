#include <WiFi.h>
#include <WiFiUdp.h>

WiFiUDP udp;
IPAddress target(192, 168, 1, 42);   // знаємо IP цілі; MAC — ні, його з'ясує ARP

void setup() {
    Serial.begin(115200);
    WiFi.begin("my-ssid", "my-pass"); // підключення: роутер видасть нам IP по DHCP
    while (WiFi.status() != WL_CONNECTED) delay(200);

    // наша IP — її ПРИЗНАЧИЛА мережа (не вшита в чіп):
    Serial.print("my IP : "); Serial.println(WiFi.localIP());
    // наша MAC — ВШИТА в залізо, стала:
    Serial.print("my MAC: "); Serial.println(WiFi.macAddress());
}

void loop() {
    udp.beginPacket(target, 5000);    // кажемо лише IP+порт цілі
    udp.write((const uint8_t*)"ping", 4);
    udp.endPacket();                  // ТУТ стек сам: ARP цілі (або шлюзу) → MAC → кадр
    delay(1000);
}
