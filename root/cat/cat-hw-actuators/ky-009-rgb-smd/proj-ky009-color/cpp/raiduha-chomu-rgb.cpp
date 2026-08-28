// H (відтінок): 0…359 градусів. S, V: 0…255.
// Пише готовий колір у setColor. Формула — класичне HSV→RGB.
void setHSV(int h, uint8_t s, uint8_t v) {
  h %= 360;                 // загорнути в коло на випадок h ≥ 360 або < 0
  if (h < 0) h += 360;

  uint8_t region = h / 60;          // який із 6 секторів кола (0…5)
  uint8_t rem    = (h % 60) * 255 / 60;  // положення в секторі, 0…255

  // допоміжні рівні (стандартні p, q, t для HSV→RGB)
  uint8_t p = (uint16_t)v * (255 - s) / 255;
  uint8_t q = (uint16_t)v * (255 - (uint16_t)s * rem / 255) / 255;
  uint8_t t = (uint16_t)v * (255 - (uint16_t)s * (255 - rem) / 255) / 255;

  uint8_t r, g, b;
  switch (region) {
    case 0:  r = v; g = t; b = p; break;  // червоний → жовтий
    case 1:  r = q; g = v; b = p; break;  // жовтий → зелений
    case 2:  r = p; g = v; b = t; break;  // зелений → блакитний
    case 3:  r = p; g = q; b = v; break;  // блакитний → синій
    case 4:  r = t; g = p; b = v; break;  // синій → пурпуровий
    default: r = v; g = p; b = q; break;  // пурпуровий → червоний
  }
  setColor(r, g, b);
}

// Райдуга по колу: H повзе 0…359 і знову.
void loop() {
  for (int h = 0; h < 360; h++) {
    setHSV(h, 255, 255);   // повна насиченість і яскравість
    delay(15);             // ~5.4 с на повне коло; менше → швидше
                           // (vTaskDelay(pdMS_TO_TICKS(15)) в ESP-IDF, HAL_Delay(15) на STM32)
  }
}
