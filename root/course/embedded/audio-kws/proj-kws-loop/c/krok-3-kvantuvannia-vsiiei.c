// input->data.int8 / output->data.int8 та їх params — з інтерпретатора TFLite Micro,
// налаштованого як у бойовому харнесі (model_init один раз при старті).
extern signed char  *g_input_i8;   // вхідний тензор: N_FRAMES*N_MEL комірок int8
extern signed char  *g_output_i8;  // вихідний тензор: N_CLASS комірок int8
extern float g_in_scale;  extern int g_in_zp;    // масштаб/нуль входу (з навчання)
extern float g_out_scale; extern int g_out_zp;   // масштаб/нуль виходу
extern bool  tflm_invoke(void);                    // обгортка над interp->Invoke()

// Розгортає кільце (з початком у head) у лінійний int8-вхід, кличе мережу,
// повертає N_CLASS ймовірностей у probs[]. Серце проходу.
static bool kws_invoke(float probs[N_CLASS]) {
    // 1+3. РОЗГОРТАННЯ + КВАНТУВАННЯ в один прохід.
    int idx = 0;                                   // біжучий індекс у лінійному вході
    for (int i = 0; i < N_FRAMES; i++) {
        int src = (head + i) % N_FRAMES;           // i-й за ЧАСОМ стовпчик — ось тут
        for (int m = 0; m < N_MEL; m++) {
            // справжнє → int8: ділимо на масштаб, зсуваємо нульовою точкою
            int32_t q = (int32_t)lroundf(ring[src][m] / g_in_scale) + g_in_zp;
            if (q < -128) q = -128;                // ОБРІЗАННЯ: без нього
            if (q >  127) q =  127;                // зашкал обгорнеться по колу
            g_input_i8[idx++] = (signed char)q;
        }
    }

    // 2. Один прохід графа (детермінований, без алокацій) — деталі в харнесі.
    if (!tflm_invoke()) return false;              // kTfLiteError → чесно вгору

    // Вихід моделі — теж int8; повертаємо в звичні ймовірності 0…1.
    for (int c = 0; c < N_CLASS; c++)
        probs[c] = g_out_scale * (g_output_i8[c] - g_out_zp);   // деквантування
    return true;
}
