// Порахувати частоту LCO для заданої ємності tune (0..15).
// Повертає виміряну частоту в Гц (уже помножену на дільник).
// TIM2 налаштовано в CubeMX як лічильник ЗОВНІШНЬОГО такту з піна IRQ
// (Clock Source = ETR2 / TI1) — залізо рахує фронти саме, без такту процесора.
static uint32_t MeasureLco(uint8_t tune) {
    uint8_t r;
    as3935_read(0x08, &r);
    as3935_write(0x08, (r & 0xF0) | (tune & 0x0F));   // TUN_CAP: 0, 8, 16 … 120 пФ
    as3935_read(0x08, &r);
    as3935_write(0x08, r | 0x80);                     // DISP_LCO=1 → LCO на пін IRQ
    HAL_Delay(2);                                     // дати сигналу устоятися

    __HAL_TIM_SET_COUNTER(&htim2, 0);
    HAL_TIM_Base_Start(&htim2);
    HAL_Delay(100);                                   // вікно 100 мс
    HAL_TIM_Base_Stop(&htim2);
    uint32_t edges = __HAL_TIM_GET_COUNTER(&htim2);

    as3935_read(0x08, &r);
    as3935_write(0x08, r & ~0xE0);                    // ПРИБРАТИ гетеродин з піна!

    // edges за 0.1 с → ·10, щоб дістати за секунду; дільник LCO_FDIV = 16
    return edges * 10U * 16U;
}

// Перебрати 16 ємностей, знайти ту, де частота найближча до 500 кГц.
static uint8_t FindBestCaps(void) {
    const int32_t target = 500000;                    // 500 кГц
    uint8_t best = 0;
    int32_t bestErr = INT32_MAX;
    for (uint8_t tune = 0; tune < 16; tune++) {
        int32_t f = (int32_t)MeasureLco(tune);
        int32_t err = f > target ? f - target : target - f;   // |f − 500 кГц|
        printf("tune=%u  f=%ld  промах=%ld\r\n", tune, (long)f, (long)err);
        if (err < bestErr) { bestErr = err; best = tune; }
    }
    printf("Найкраща ємність: tune=%u (%u пФ)\r\n", best, best * 8);
    return best;
}
