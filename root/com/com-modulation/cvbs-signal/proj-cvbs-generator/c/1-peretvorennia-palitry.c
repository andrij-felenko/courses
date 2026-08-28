typedef struct {
    uint8_t dac_samples[4]; /* Чотири фазові відліки ЦАП для одного пікселя */
} cvbs_color_entry_t;

void cvbs_build_color_lut(cvbs_color_entry_t *color_lut, uint8_t r, uint8_t g, uint8_t b) {
    /* 1. Розрахунок Y, U, V у шкалі IRE */
    float y_ire = 0.299f * r + 0.587f * g + 0.114f * b;
    float u_ire = 0.492f * (b - y_ire);
    float v_ire = 0.877f * (r - y_ire);

    /* 2. Обчислення чотирьох дискретних відліків піднесучої C(t) */
    /* t=0 (0°): C = V; t=1 (90°): C = U; t=2 (180°): C = -V; t=3 (270°): C = -U */
    float c0 =  v_ire;
    float c1 =  u_ire;
    float c2 = -v_ire;
    float c3 = -u_ire;

    /* 3. Сумування Y + C та конверсія в коди ЦАП */
    color_lut->dac_samples[0] = cvbs_ire_to_dac((int16_t)(y_ire + c0));
    color_lut->dac_samples[1] = cvbs_ire_to_dac((int16_t)(y_ire + c1));
    color_lut->dac_samples[2] = cvbs_ire_to_dac((int16_t)(y_ire + c2));
    color_lut->dac_samples[3] = cvbs_ire_to_dac((int16_t)(y_ire + c3));
}
