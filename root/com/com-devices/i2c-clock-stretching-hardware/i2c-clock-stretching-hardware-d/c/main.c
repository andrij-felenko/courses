// Коректне переведення SCL у високий рівень з контролем розтягування такту в C
bool i2c_soft_scl_release_and_wait(uint32_t timeout_us) {
    // 1. Відпускаємо лінію в стан Hi-Z (зовнішній резистор підтягує лінію до 3.3В)
    gpio_set_pin_hiz(SCL_PIN);
    
    uint32_t start_time = timer_get_micros();
    
    // 2. Опитуємо реальний стан фізичного виводу через вхідний буфер IDR
    while (gpio_read_pin(SCL_PIN) == 0) {
        // Ведений утримує SCL в нулі (розтягує такт)
        if ((timer_get_micros() - start_time) >= timeout_us) {
            // Ведений перевищив допустимий ліміт часу: фіксуємо аварію шини
            return false; // Помилка таймауту SCL
        }
    }
    
    // 3. Лінія SCL успішно піднялася до 3.3В — продовжуємо такт
    return true;
}
