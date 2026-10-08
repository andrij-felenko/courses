#include <Arduino.h>
#include <FastLED.h>

#define NUM_LEDS 300
#define DATA_PIN 5
#define MAX_VOLTS 5
#define MAX_MILLIAMPS 8000 // Максимально допустимий струм інжекції: 8 Ампер

CRGB leds[NUM_LEDS];

void setup() {
    // Ініціалізація адресованої стрічки WS2812B
    FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);
    
    // Апаратний ліміт потужності: FastLED масштабує яскравість,
    // якщо сумарний струм кадру перевищує 8000 мА при 5 В
    FastLED.setMaxPowerInVoltsAndMilliamps(MAX_VOLTS, MAX_MILLIAMPS);
    FastLED.setBrightness(255);
}

void loop() {
    // Заповнення стрічки яскравим білим кольором
    fill_solid(leds, NUM_LEDS, CRGB::White);
    
    // Розрахунок та автокорекція яскравості перед відправкою даних
    FastLED.show();
    delay(20);
}
