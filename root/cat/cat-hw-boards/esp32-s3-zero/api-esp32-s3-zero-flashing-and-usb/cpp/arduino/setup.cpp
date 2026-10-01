#include <Adafruit_NeoPixel.h>

#define RGB_LED_PIN 21
#define NUM_LEDS     1

Adafruit_NeoPixel pixels(NUM_LEDS, RGB_LED_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
    pixels.begin();
    pixels.clear();
}

void setRGBColor(uint8_t red, uint8_t green, uint8_t blue) {
    pixels.setPixelColor(0, pixels.Color(red, green, blue));
    pixels.show();
}
