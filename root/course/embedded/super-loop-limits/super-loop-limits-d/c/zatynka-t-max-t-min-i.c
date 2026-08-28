void loop() {
    uint32_t t0 = micros();
    do_all_steps();                 // усі кроки циклу
    uint32_t dt = micros() - t0;    // тривалість цього оберту (стійке до переповнення micros)

    static uint32_t t_max = 0;
    if (dt > t_max) {               // тримаємо лише найгірший бачений оберт
        t_max = dt;
        Serial.printf("new worst loop: %lu us\n", t_max);
    }
}
