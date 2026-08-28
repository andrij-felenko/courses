#include <ESP8266WiFi.h>

const char* SSID = "ВашаМережа";        // ім'я вашої Wi-Fi
const char* PASS = "ВашПароль";         // пароль WPA/WPA2

const int LED = 2;                       // GPIO2, активний НИЗЬКИЙ

void setup() {
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);               // погашено

  Serial.begin(115200);                  // щоб бачити діагностику
  Serial.println();

  WiFi.mode(WIFI_STA);                   // режим клієнта (station), не точки доступу
  WiFi.begin(SSID, PASS);                // почати під'єднання

  Serial.print("Під'єднуюсь до ");
  Serial.print(SSID);

  // чекаємо мережу, блимаючи LED, поки статус не стане «під'єднано»
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(LED, LOW);              // блимнути (LOW = світиться)
    delay(100);
    digitalWrite(LED, HIGH);
    delay(100);
    Serial.print(".");
  }

  digitalWrite(LED, LOW);                // у мережі — лишаємо LED засвіченим
  Serial.println(" готово!");
  Serial.print("IP-адреса: ");
  Serial.println(WiFi.localIP());        // ось за цією адресою нас видно в мережі
}

void loop() {
  // поки нічого — уся робота попереду, у веб-сервері
}
