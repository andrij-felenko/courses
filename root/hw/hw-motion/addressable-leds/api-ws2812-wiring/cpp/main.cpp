#include <Adafruit_NeoPixel.h>

#define PIN   5          // GPIO даних (через рівнезсув на DIN стрічки)
#define N     100        // кількість пікселів у стрічці

Adafruit_NeoPixel strip(N, PIN, NEO_GRB + NEO_KHZ800);

void setup() {
    strip.begin();
    strip.setBrightness(40);                          // ОБМЕЖУЄМО яскравість → менше струму!
    strip.setPixelColor(0, strip.Color(255, 0, 0));   // перший піксель — червоний
    strip.show();                                     // вилити кадр у стрічку + скидання (LOW ≥ 50 мкс)
}

void loop() {}
