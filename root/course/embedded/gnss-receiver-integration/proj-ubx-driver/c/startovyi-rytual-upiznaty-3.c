typedef enum { GEN_UNKNOWN, GEN_M8, GEN_M9_M10 } ubx_gen_t;
static ubx_gen_t g_gen;

// MON-VER повертає ASCII-рядки; серед розширень є "PROTVER=xx.yy".
// Протокол ≥ 27 → покоління M9/M10 (ключ-значення); менше → M8 (легасі CFG).
// (Спрощено: у бойовому коді ще й ловлять MOD=... з назвою модуля.)
static void detect_from_monver(const uint8_t *buf, uint16_t len) {
    for (uint16_t i = 0; i + 8 <= len; i++) {
        if (memcmp(buf + i, "PROTVER=", 8) == 0) {
            int major = 0;
            for (uint16_t j = i + 8; j < len && buf[j] >= '0' && buf[j] <= '9'; j++)
                major = major * 10 + (buf[j] - '0');
            g_gen = (major >= 27) ? GEN_M9_M10 : GEN_M8;
            return;
        }
    }
}
