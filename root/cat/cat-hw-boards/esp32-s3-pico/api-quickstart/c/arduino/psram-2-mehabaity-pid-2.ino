static const int FB_W = 320, FB_H = 240;
uint16_t *fb = nullptr;

void allocFrame() {
  size_t bytes = (size_t)FB_W * FB_H * sizeof(uint16_t);  // 320·240·2 = 153 600 Б
  fb = (uint16_t *) ps_malloc(bytes);                     // явно у PSRAM
  if (!fb) { Serial.println("немає місця під кадр"); return; }

  for (int y = 0; y < FB_H; y++)                          // малюємо як у звичайний масив
    for (int x = 0; x < FB_W; x++)
      fb[y * FB_W + x] = ((x ^ y) & 1) ? 0xFFFF : 0x0000; // шахівниця
}
