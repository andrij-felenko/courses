#include <Adafruit_NeoPixel.h>

#define WS2812_PIN   8
#define WS2812_COUNT 1

Adafruit_NeoPixel pixel(WS2812_COUNT, WS2812_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  pixel.begin();       // ініціалізація
  pixel.setBrightness(40);   // 0..255, глобальний масштаб яскравості
  pixel.show();        // погасити стартово (буфер порожній)
}

void loop() {
  pixel.setPixelColor(0, pixel.Color(0, 255, 0));  // зелений
  pixel.show();                                    // відправити
  delay(400);

  pixel.setPixelColor(0, 0);   // 0 = чорний = згас
  pixel.show();
  delay(400);
}
