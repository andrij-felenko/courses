// ESP32, старий LEDC API (core 2.x). Живлення логіки — 3.3 В!
const uint8_t PIN_R = 25, PIN_G = 26, PIN_B = 27;
const int CH_R = 0, CH_G = 1, CH_B = 2;   // три незалежні канали LEDC
const int PWM_FREQ = 5000;                // 5 кГц — вище за поріг мерехтіння
const int PWM_BITS = 8;                   // 8-бітна роздільність → 0…255, як звикли

void setup() {
  ledcSetup(CH_R, PWM_FREQ, PWM_BITS);    // налаштувати канал: частота + роздільність
  ledcSetup(CH_G, PWM_FREQ, PWM_BITS);
  ledcSetup(CH_B, PWM_FREQ, PWM_BITS);
  ledcAttachPin(PIN_R, CH_R);             // прив'язати пін до каналу
  ledcAttachPin(PIN_G, CH_G);
  ledcAttachPin(PIN_B, CH_B);
}

void setColor(uint8_t r, uint8_t g, uint8_t b) {
  ledcWrite(CH_R, gamma8[r]);   // пишемо В КАНАЛ, не в пін
  ledcWrite(CH_G, gamma8[g]);
  ledcWrite(CH_B, gamma8[b]);
}
