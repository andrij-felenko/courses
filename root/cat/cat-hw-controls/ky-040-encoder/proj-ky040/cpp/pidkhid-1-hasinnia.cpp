const uint8_t PIN_CLK = 2;
const uint8_t PIN_DT  = 3;

volatile long          counter    = 0;
volatile unsigned long lastEdgeUs = 0;      // час останнього зарахованого краю

void onClkFall() {
  unsigned long now = micros();
  // ігноруємо все, що ближче за 2 мс до попереднього краю — це брязкіт
  if (now - lastEdgeUs < 2000UL) return;
  lastEdgeUs = now;

  if (digitalRead(PIN_DT) == HIGH) counter++;   // DT ще «1» → за годинниковою
  else                             counter--;    // DT уже «0» → проти
}
