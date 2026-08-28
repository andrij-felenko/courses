// Варіант методів для ESP32 (Arduino-ESP32 core 3.x).
// LEDC: 5 кГц — вище звукового діапазону (реле/мотор не «пищать»),
// 8-бітна розрядність → шпаруватість теж 0…255, як і analogWrite.
void Switch::begin_pwm(uint32_t freq_hz = 5000, uint8_t bits = 8) {
    ledcAttach(pin_, freq_hz, bits);   // прив'язати вивід, задати частоту й розрядність
    analog(0);                         // старт: вимкнено
}

void Switch::analog(uint8_t duty8) {
    ledcWrite(pin_, active_low_ ? (255 - duty8) : duty8);
}
