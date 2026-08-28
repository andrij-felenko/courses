// ЯК НЕ ТРЕБА. Опитування ноги PPS у циклі.
uint8_t prev = 0;
for (;;) {
    uint8_t now = (GPIOA->IDR >> PPS_PIN) & 1u;   // прочитати рівень ноги
    if (now && !prev) {                            // побачили наростання 0→1
        uint32_t t = TIM2->CNT;                    // "оце момент фронту"
        handle_pps(t);
    }
    prev = now;
    do_other_work();                               // і ще купа справ у тому ж циклі
}
