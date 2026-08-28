// плавний перехід поточного кольору A → цільового B за час ~ (steps * wait) мс
void fade(uint8_t rA, uint8_t gA, uint8_t bA,
          uint8_t rB, uint8_t gB, uint8_t bB,
          uint16_t steps, uint16_t wait) {
  for (uint16_t i = 0; i <= steps; i++) {
    float t = (float)i / steps;                 // 0.0 → 1.0
    uint8_t r = rA + (int)((rB - rA) * t);      // лінійна інтерполяція каналу
    uint8_t g = gA + (int)((gB - gA) * t);
    uint8_t b = bA + (int)((bB - bA) * t);
    setColor(r, g, b);
    delay(wait);                                // пауза між кадрами
  }
}

void loop() {
  fade(255, 90, 0,  0, 120, 255,  60, 12);   // помаранчевий → блакитний, ~0.7 с
  fade(0, 120, 255,  255, 90, 0,  60, 12);   // і назад
}
