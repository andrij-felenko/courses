// Оптимізована інтерполяція двох каналів (R та B) за допомогою інструкцій CMSIS-DSP
static inline void interp_dual_channel_simd(
    uint32_t p00_rb, uint32_t p10_rb,
    uint32_t p01_rb, uint32_t p11_rb,
    int32_t w00, int32_t w10, int32_t w01, int32_t w11,
    uint8_t *out_r, uint8_t *out_b)
{
    // w_pair0 = [w10 | w00], w_pair1 = [w11 | w01]
    uint32_t w_pair0 = ((uint32_t)(uint16_t)w10 << 16) | (uint16_t)w00;
    uint32_t w_pair1 = ((uint32_t)(uint16_t)w11 << 16) | (uint16_t)w01;

    // Розпакування червоного каналу: r_pair0 = [r10 | r00], r_pair1 = [r11 | r01]
    uint32_t r_pair0 = ((p10_rb & 0xFF) << 16) | (p00_rb & 0xFF);
    uint32_t r_pair1 = ((p11_rb & 0xFF) << 16) | (p01_rb & 0xFF);

    // Паралельне множення та накопичення
    int32_t acc_r = 32768; // Біас округлення
    acc_r = __SMLAD(r_pair0, w_pair0, acc_r);
    acc_r = __SMLAD(r_pair1, w_pair1, acc_r);
    *out_r = (uint8_t)(acc_r >> 16);

    // Розпакування синього каналу: b_pair0 = [b10 | b00], b_pair1 = [b11 | b01]
    uint32_t b_pair0 = (p10_rb & 0xFF0000) | ((p00_rb & 0xFF0000) >> 16);
    uint32_t b_pair1 = (p11_rb & 0xFF0000) | ((p01_rb & 0xFF0000) >> 16);

    int32_t acc_b = 32768;
    acc_b = __SMLAD(b_pair0, w_pair0, acc_b);
    acc_b = __SMLAD(b_pair1, w_pair1, acc_b);
    *out_b = (uint8_t)(acc_b >> 16);
}
