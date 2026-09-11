// Ініціалізація апаратного ШІМ на базі мікроконтролера ESP32 (фреймворк Arduino)
// Модуль LEDC дозволяє прямо вказати цільову частоту 20 кГц
const uint8_t MOTOR_PWM_CHANNEL_A = 0;
const uint8_t MOTOR_PWM_CHANNEL_B = 1;
const uint32_t PWM_FREQ_HZ = 20000;
const uint8_t PWM_RESOLUTION_BITS = 10; // Роздільна здатність 10 біт (0..1023)

void esp32_pwm_init(uint8_t pin_in1, uint8_t pin_in2)
{
    // Налаштування першого каналу генератора ШІМ на 20 кГц
    ledcSetup(MOTOR_PWM_CHANNEL_A, PWM_FREQ_HZ, PWM_RESOLUTION_BITS);
    ledcAttachPin(pin_in1, MOTOR_PWM_CHANNEL_A);
    ledcWrite(MOTOR_PWM_CHANNEL_A, 0); // Початковий безпечний рівень 0%

    // Налаштування другого каналу генератора ШІМ на 20 кГц
    ledcSetup(MOTOR_PWM_CHANNEL_B, PWM_FREQ_HZ, PWM_RESOLUTION_BITS);
    ledcAttachPin(pin_in2, MOTOR_PWM_CHANNEL_B);
    ledcWrite(MOTOR_PWM_CHANNEL_B, 0); // Початковий безпечний рівень 0%
}
