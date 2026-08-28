// Кут серво через ширину імпульсу. Частота розширювача виставлена на 50 Гц,
// тож весь період = 4096 кроків = 20 мс, крок ≈ 4.883 мкс.
void servo_set_us(uint8_t ch, uint16_t pulse_us) {
    // скільки кроків лічильника вкладається в pulse_us
    uint16_t count = (uint16_t)((uint32_t)pulse_us * 4096u / 20000u);
    pwm_set_duty(ch, count);          // ON=0, OFF=count
}

servo_set_us(3, 1500);                // центр  → ≈ 307
servo_set_us(3, 1000);                // край   → ≈ 205
servo_set_us(3, 2000);                // край   → ≈ 410
