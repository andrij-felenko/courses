// ESP32 (Arduino-core): ШІМ на 25 кГц (вище чутного — обмотка не пищить), 8-біт роздільність
const uint8_t  SOL_PIN   = 5;
const uint8_t  SOL_CH    = 0;        // канал LEDC
const uint32_t PWM_FREQ  = 25000;    // 25 кГц — поза чутним діапазоном
const uint8_t  PWM_BITS  = 8;        // роздільність шпаруватості: 0..255

void solenoidSetup() {
    ledcSetup(SOL_CH, PWM_FREQ, PWM_BITS);
    ledcAttachPin(SOL_PIN, SOL_CH);
}

void solenoidPeak()  { ledcWrite(SOL_CH, 255); }  // повний струм на втягування
void solenoidHold()  { ledcWrite(SOL_CH, 90);  }  // ≈35% — тихе утримання
void solenoidOff()   { ledcWrite(SOL_CH, 0);   }  // відпустити
