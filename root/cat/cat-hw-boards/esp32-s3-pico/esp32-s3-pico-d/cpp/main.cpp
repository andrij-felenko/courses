#include <WiFi.h>
#include <Adafruit_NeoPixel.h>

Adafruit_NeoPixel led(1, 21, NEO_GRB + NEO_KHZ800);  // 1 діод на GPIO21

void setup() {
  Serial.begin(115200);
  led.begin();
  led.setPixelColor(0, led.Color(0, 40, 0));         // тьмяно-зелений
  led.show();                                        // «плата ожила»

  WiFi.begin("SSID", "пароль");
  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print(".");
  }
  Serial.printf("\nПідключено, IP: %s\n", WiFi.localIP().toString().c_str());
}

void loop() {}
