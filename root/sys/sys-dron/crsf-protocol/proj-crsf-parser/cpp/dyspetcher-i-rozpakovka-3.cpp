// 10 байтів статистики лінка у фіксованому порядку (специфікація CRSF).
static void crsf_parse_link(const uint8_t *p) {
    g_link.up_rssi1 = p[0];           // висхідний RSSI, антена 1 (−дБм)
    g_link.up_rssi2 = p[1];           // висхідний RSSI, антена 2 (−дБм)
    g_link.up_lq    = p[2];           // висхідна якість лінка (%)
    g_link.up_snr   = (int8_t)p[3];   // висхідний SNR (дБ, ЗНАКОВИЙ!)
    g_link.ant      = p[4];           // активна антена (0 / 1)
    g_link.rf_mode  = p[5];           // радіорежим (профіль швидкості)
    g_link.up_power = p[6];           // потужність передавача (enum)
    g_link.dn_rssi  = p[7];           // низхідний RSSI (−дБм)
    g_link.dn_lq    = p[8];           // низхідна якість лінка (%)
    g_link.dn_snr   = (int8_t)p[9];   // низхідний SNR (дБ, ЗНАКОВИЙ!)
}
