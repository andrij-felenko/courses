// ESP32, новий LEDC API (core 3.x).
const uint8_t PIN_R = 25, PIN_G = 26, PIN_B = 27;
const int PWM_FREQ = 5000;
const int PWM_BITS = 8;

void setup() {
  ledcAttach(PIN_R, PWM_FREQ, PWM_BITS);  // пін + частота + роздільність одним викликом
  ledcAttach(PIN_G, PWM_FREQ, PWM_BITS);
  ledcAttach(PIN_B, PWM_FREQ, PWM_BITS);
}

void setColor(uint8_t r, uint8_t g, uint8_t b) {
  ledcWrite(PIN_R, gamma8[r]);  // тепер пишемо прямо в ПІН
  ledcWrite(PIN_G, gamma8[g]);
  ledcWrite(PIN_B, gamma8[b]);
}
