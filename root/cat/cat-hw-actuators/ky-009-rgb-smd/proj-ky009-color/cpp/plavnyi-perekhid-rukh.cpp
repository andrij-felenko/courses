// Плавно перейти з (r0,g0,b0) у (r1,g1,b1) за steps кроків.
// wait — пауза між кроками в мілісекундах (менша → швидше).
void fadeTo(uint8_t r0, uint8_t g0, uint8_t b0,
            uint8_t r1, uint8_t g1, uint8_t b1,
            int steps, int wait) {
  for (int i = 0; i <= steps; i++) {
    // частка шляху, порахована в цілих, щоб не тягти float:
    // поточне = старе + (нове − старе) * i / steps
    uint8_t r = r0 + (int)(r1 - r0) * i / steps;
    uint8_t g = g0 + (int)(g1 - g0) * i / steps;
    uint8_t b = b0 + (int)(b1 - b0) * i / steps;
    setColor(r, g, b);
    delay(wait);   // пауза: delay() в Arduino, vTaskDelay(pdMS_TO_TICKS(wait))
                   // в ESP-IDF, HAL_Delay() на STM32 — решта рядків незмінна
  }
}

void loop() {
  fadeTo(255, 0, 0,   0, 0, 255,  100, 8);  // червоний → синій за ~0.8 с
  fadeTo(  0, 0, 255, 0, 0,   0,  100, 8);  // синій → темрява (згасання)
  fadeTo(  0, 0, 0,   0, 255, 0,  100, 8);  // з темряви → зелений
  delay(300);
}
