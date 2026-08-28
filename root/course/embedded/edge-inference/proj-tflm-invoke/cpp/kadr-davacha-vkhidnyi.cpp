// Кладе ОДИН відлік давача у вхідний тензор, КВАНТУЮЧИ за параметрами моделі.
static inline int8_t quantize_input(float real_value) {
    const float scale = input->params.scale;          // ціна однієї поділки int8
    const int   zp    = input->params.zero_point;     // код, що означає нуль

    int32_t q = (int32_t)lroundf(real_value / scale) + zp;  // справжнє → int8

    // ОБОВ'ЯЗКОВЕ обрізання в діапазон int8: інакше переповнення дасть сміття.
    if (q < -128) q = -128;
    if (q >  127) q =  127;
    return (int8_t)q;
}
