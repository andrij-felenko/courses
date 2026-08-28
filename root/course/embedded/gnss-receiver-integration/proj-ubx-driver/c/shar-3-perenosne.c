// Дістати багатобайтове ціле з payload за зсувом, у нативний порядок.
// memcpy НЕ порушує strict aliasing і не залежить від пакування структури.
// Ці читання коректні на LE-платформі (ARM/ESP32). Для повної переносності
// на BE тут була б перестановка байтів — але цільове залізо LE, тож memcpy як є.
static inline uint32_t rd_u32(const uint8_t *b, int off) {
    uint32_t v; memcpy(&v, b + off, 4); return v;
}
static inline int32_t  rd_i32(const uint8_t *b, int off) {
    int32_t v;  memcpy(&v, b + off, 4); return v;
}
static inline uint16_t rd_u16(const uint8_t *b, int off) {
    uint16_t v; memcpy(&v, b + off, 2); return v;
}

// Готовий, уже перерахований і перевірений фікс — саме це віддаємо нагору.
typedef struct {
    double   lat_deg, lon_deg;   // градуси (з int32 × 1e-7)
    double   alt_m;              // метри над рівнем моря
    double   speed_mps;          // м/с (з мм/с)
    double   head_deg;           // курс руху, градуси (з int32 × 1e-5)
    float    hacc_m;             // оцінка горизонтальної похибки, метри
    float    pdop;               // геометричне розмивання (з u16 × 0.01)
    uint8_t  fix_type;           // 0/2/3
    uint8_t  num_sv;
    bool     gnss_fix_ok;
    uint32_t itow_ms;
    uint32_t stamp_ms;           // коли ЦЕЙ фікс прийняв драйвер (для свіжості)
} gnss_fix_t;

// Розібрати сирий payload NAV-PVT у зручні одиниці. Перерахунок масштабів — тут.
static void decode_pvt(const uint8_t *b, uint32_t now_ms, gnss_fix_t *f) {
    f->itow_ms  = rd_u32(b, PVT_iTOW);
    f->fix_type = b[PVT_fixType];
    f->num_sv   = b[PVT_numSV];
    f->gnss_fix_ok = (b[PVT_flags] & 0x01) != 0;   // біт0 байта flags

    // Координати: int32 × 1e-7 → градуси. ДІЛИТИ у double: int32,
    // помножений назад, переповнився б, а результат потрібен дробовий.
    f->lat_deg = (double)rd_i32(b, PVT_lat) * 1e-7;
    f->lon_deg = (double)rd_i32(b, PVT_lon) * 1e-7;
    f->alt_m   = (double)rd_i32(b, PVT_hMSL) / 1000.0;   // мм → м  (див. fixed-point нижче)

    f->speed_mps = (double)rd_i32(b, PVT_gSpeed) / 1000.0;   // мм/с → м/с
    f->head_deg  = (double)rd_i32(b, PVT_headMot) * 1e-5;    // × 1e-5 градуса
    f->hacc_m    = (float)rd_u32(b, PVT_hAcc) / 1000.0f;     // мм → м
    f->pdop      = (float)rd_u16(b, PVT_pDOP) * 0.01f;       // × 0.01

    f->stamp_ms  = now_ms;   // позначка часу прийому — база для перевірки свіжості
}
