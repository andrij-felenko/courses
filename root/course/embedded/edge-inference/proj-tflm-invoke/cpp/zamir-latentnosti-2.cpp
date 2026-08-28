volatile uint32_t g_last_cycles = 0;   // такти останнього Invoke()

// Один прохід моделі з заміром латентності в тактах ядра.
// Повертає деквантований вихід, або −1 при збої.
float model_run(const float* features_g, int n) {     // ← НА КОЖЕН КАДР
    feed_frame(features_g, n);                         // кадр → int8-тензор

    uint32_t t0 = DWT->CYCCNT;                         // ⏱ старт
    TfLiteStatus s = interp->Invoke();                // один прохід графа
    g_last_cycles = DWT->CYCCNT - t0;                 // ⏱ стоп (різниця в тактах)

    if (s != kTfLiteOk) {                              // ПОВНА обробка помилки
        MicroPrintf("Invoke failed: %d (op missing? bad input?)", s);
        return -1.0f;
    }

    // Вихід — int8; повертаємо в звичне число ТИМ САМИМ містком (деквантування).
    int8_t  raw   = output->data.int8[0];
    float   scale = output->params.scale;
    int     zp    = output->params.zero_point;
    return scale * (raw - zp);                          // ймовірність 0…1
}
