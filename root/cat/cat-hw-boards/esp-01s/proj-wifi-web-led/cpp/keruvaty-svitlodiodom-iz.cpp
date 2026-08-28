#include <ESP8266WiFi.h>

const char* SSID = "ВашаМережа";
const char* PASS = "ВашПароль";

const int LED = 2;                       // GPIO2, активний НИЗЬКИЙ

WiFiServer server(80);                   // сервер на 80-му порту (HTTP)

void setup() {
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);               // старт: погашено

  Serial.begin(115200);
  Serial.println();

  WiFi.mode(WIFI_STA);
  WiFi.begin(SSID, PASS);
  while (WiFi.status() != WL_CONNECTED) { delay(200); Serial.print("."); }

  Serial.println();
  Serial.print("Відкрий у браузері: http://");
  Serial.println(WiFi.localIP());        // ось цю адресу — в адресний рядок

  server.begin();                        // почати слухати з'єднання
}

void loop() {
  WiFiClient client = server.accept();   // хтось під'єднався?
  if (!client) return;                   // ні — виходимо, спробуємо в наступному циклі

  // читаємо ПЕРШИЙ рядок запиту — у ньому весь потрібний нам зміст:
  //   "GET /on HTTP/1.1"  →  шлях "/on"
  String req = client.readStringUntil('\r');
  client.readStringUntil('\n');          // дочитати кінець рядка

  // за шляхом вирішуємо, що робити зі світлодіодом
  // (пам'ятаємо: LOW = світиться, HIGH = гасне)
  bool on;
  if (req.indexOf("/on") != -1) {
    digitalWrite(LED, LOW);              // увімкнути
    on = true;
  } else if (req.indexOf("/off") != -1) {
    digitalWrite(LED, HIGH);             // вимкнути
    on = false;
  } else {
    on = (digitalRead(LED) == LOW);      // просто "/" — лишити як є, показати стан
  }

  // проковтуємо решту заголовків запиту, поки браузер їх шле
  while (client.available()) client.read();

  // ── відповідь: спершу HTTP-заголовок, потім HTML-сторінка ──
  client.print(
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html; charset=utf-8\r\n"
    "Connection: close\r\n"
    "\r\n");                             // порожній рядок = кінець заголовків

  client.print("<!DOCTYPE html><html><head><meta charset='utf-8'>");
  client.print("<meta name='viewport' content='width=device-width'>");
  client.print("<title>ESP-01S</title></head><body>");
  client.print("<h2>Світлодіод зараз: ");
  client.print(on ? "<b>увімкнено</b>" : "<b>вимкнено</b>");
  client.print("</h2>");
  client.print("<p><a href='/on'>Увімкнути</a> &nbsp; ");
  client.print("<a href='/off'>Вимкнути</a></p>");
  client.print("</body></html>");

  client.stop();                         // закрити з'єднання
}
