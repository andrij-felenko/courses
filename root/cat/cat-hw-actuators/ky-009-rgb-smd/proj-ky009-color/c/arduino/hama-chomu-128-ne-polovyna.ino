uint8_t gamma8[256];

void buildGamma(float g) {          // напр. g = 2.2
  for (int i = 0; i < 256; i++) {
    gamma8[i] = (uint8_t)(pow((float)i / 255.0, g) * 255.0 + 0.5);
  }
}

void setup() {
  pinMode(PIN_R, OUTPUT);
  pinMode(PIN_G, OUTPUT);
  pinMode(PIN_B, OUTPUT);
  buildGamma(2.2);   // порахувати криву один раз на старті
}
