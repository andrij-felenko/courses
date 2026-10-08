// Приклад апаратної генерації WS2812B через FastLED в Arduino (C++)
#include <FastLED.h>

#define NUM_LEDS 60
#define DATA_PIN 5

CRGB leds[NUM_LEDS];

void setup() {
    FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);
    FastLED.setBrightness(128);
}

void loop() {
    leds[0] = CRGB::Red;
    FastLED.show(); // Апаратна відправка кадру через DMA
}
