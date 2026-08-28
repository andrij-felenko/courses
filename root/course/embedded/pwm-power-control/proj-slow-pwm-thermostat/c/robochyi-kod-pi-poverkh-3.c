float sensor_read_temperature(void) {
    // Приклад: NTC-термістор через дільник, кілька відліків АЦП і усереднення.
    const int N = 8;
    int32_t acc = 0;
    for (int i = 0; i < N; i++) acc += adc_read_raw();   // 12-біт відлік
    float raw = (float)acc / N;

    // → напруга → опір термістора → температура (спрощено, реальне — таблиця/Стейнгарт).
    float v = raw / 4095.0f * 3.3f;
    float r_ntc = R_FIXED * v / (3.3f - v);
    float temp = ntc_resistance_to_celsius(r_ntc);       // ваша калібрувальна функція
    return temp;
}
