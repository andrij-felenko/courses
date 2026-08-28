// ESP32 (Arduino-ESP32 2.x): три канали LEDC під три кольори KY-016
const uint8_t PIN_R = 25, PIN_G = 26, PIN_B = 27;   // на ESP32 підійде майже будь-який GPIO
const uint8_t CH_R = 0,  CH_G = 1,  CH_B = 2;       // три апаратні канали LEDC
const uint32_t PWM_FREQ = 5000;                      // 5 кГц — поза чутністю, без мерехтіння
const uint8_t  PWM_BITS = 8;                         // 8-бітна роздільність → duty 0..255

const bool COMMON_ANODE = false;

static inline uint8_t level(uint8_t v) {
  return COMMON_ANODE ? (uint8_t)(255 - v) : v;
}

void setColor(uint8_t r, uint8_t g, uint8_t b) {
  ledcWrite(CH_R, level(gamma8(r)));   // на ESP32 пишемо в КАНАЛ, не в пін
  ledcWrite(CH_G, level(gamma8(g)));
  ledcWrite(CH_B, level(gamma8(b)));
}

void setup() {
  ledcSetup(CH_R, PWM_FREQ, PWM_BITS);   // 1) налаштувати канал: частота + роздільність
  ledcSetup(CH_G, PWM_FREQ, PWM_BITS);
  ledcSetup(CH_B, PWM_FREQ, PWM_BITS);
  ledcAttachPin(PIN_R, CH_R);            // 2) прив'язати канал до фізичного піна
  ledcAttachPin(PIN_G, CH_G);
  ledcAttachPin(PIN_B, CH_B);
  setColor(255, 90, 0);
}

void loop() {}
