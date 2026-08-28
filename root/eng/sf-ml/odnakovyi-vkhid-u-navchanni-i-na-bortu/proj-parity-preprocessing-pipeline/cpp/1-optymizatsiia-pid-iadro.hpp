// Векторизована функція білінійного змішування двох каналів
inline void interp_dual_channel_simd(
    uint32_t p00_rb, uint32_t p10_rb,
    uint32_t p01_rb, uint32_t p11_rb,
    int32_t w00, int32_t w10, int32_t w01, int32_t w11,
    uint8_t& out_r, uint8_t& out_b) noexcept
{
    const uint32_t w_pair0 = (static_cast<uint32_t>(static_cast<uint16_t>(w10)) << 16) | static_cast<uint16_t>(w00);
    const uint32_t w_pair1 = (static_cast<uint32_t>(static_cast<uint16_t>(w11)) << 16) | static_cast<uint16_t>(w01);

    const uint32_t r_pair0 = ((p10_rb & 0xFF) << 16) | (p00_rb & 0xFF);
    const uint32_t r_pair1 = ((p11_rb & 0xFF) << 16) | (p01_rb & 0xFF);

    int32_t acc_r = 32768;
    acc_r = __SMLAD(r_pair0, w_pair0, acc_r);
    acc_r = __SMLAD(r_pair1, w_pair1, acc_r);
    out_r = static_cast<uint8_t>(acc_r >> 16);

    const uint32_t b_pair0 = (p10_rb & 0xFF0000) | ((p00_rb & 0xFF0000) >> 16);
    const uint32_t b_pair1 = (p11_rb & 0xFF0000) | ((p01_rb & 0xFF0000) >> 16);

    int32_t acc_b = 32768;
    acc_b = __SMLAD(b_pair0, w_pair0, acc_b);
    acc_b = __SMLAD(b_pair1, w_pair1, acc_b);
    out_b = static_cast<uint8_t>(acc_b >> 16);
}
