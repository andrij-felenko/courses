#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

// --- Налаштування мережі: підставте свої ---
const char* SSID     = "MyHomeWiFi";
const char* PASSWORD  = "supersecret";

// GPIO2: катод світлодіода тут (спосіб B), тож логіка ІНВЕРСНА:
//   LOW  -> світлодіод світить
//   HIGH -> світлодіод гасне
const uint8_t LED = 2;

ESP8266WebServer server(80);   // веб-сервер на 80-му порту

bool ledOn = false;            // поточний стан світлодіода
unsigned long lastToggle = 0;  // коли востаннє перемкнули
const unsigned long BLINK_MS = 1000;  // період блимання, мс

// Обробник кореневої сторінки: віддаємо стан коротким HTML
void handleRoot() {
  unsigned long upSec = millis() / 1000;
  String html = "<!DOCTYPE html><html><head><meta charset='utf-8'>";
  html += "<title>ESP-01</title></head><body>";
  html += "<h2>ESP-01 живий</h2>";
  html += "<p>Працює: " + String(upSec) + " с</p>";
  html += "<p>Світлодіод: " + String(ledOn ? "увімкнено" : "вимкнено") + "</p>";
  html += "</body></html>";
  server.send(200, "text/html; charset=utf-8", html);
}

void setup() {
  // ВАЖЛИВО: 115200 — та сама швидкість, що й у заводському завантажувачі,
  // тож монітор не сипле сміттям одразу після старту.
  Serial.begin(115200);
  delay(10);

  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);      // старт: світлодіод вимкнено (HIGH = гасне)

  Serial.println();
  Serial.print("Приєднуюся до ");
  Serial.println(SSID);

  WiFi.mode(WIFI_STA);          // режим клієнта (station), не точки доступу
  WiFi.begin(SSID, PASSWORD);   // запускаємо приєднання

  // Чекаємо з'єднання, підморгуючи, щоб було видно «я живий, але ще не в мережі»
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(LED, LOW);     // блимнули (LOW = світить)
    delay(100);
    digitalWrite(LED, HIGH);
    delay(400);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("Приєднано. IP: ");
  Serial.println(WiFi.localIP());   // ось цю адресу відкриваємо в браузері

  server.on("/", handleRoot);   // маршрут: корінь -> handleRoot
  server.begin();
  Serial.println("Веб-сервер запущено");
}

void loop() {
  server.handleClient();        // обслуговуємо запити браузера

  // Неблокуюче блимання: без delay(), щоб веб-сервер не «глух» на секунду
  unsigned long now = millis();
  if (now - lastToggle >= BLINK_MS) {
    lastToggle = now;
    ledOn = !ledOn;
    digitalWrite(LED, ledOn ? LOW : HIGH);  // LOW світить (спосіб B)
  }
}
