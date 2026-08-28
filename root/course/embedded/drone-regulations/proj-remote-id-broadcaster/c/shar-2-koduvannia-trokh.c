// Спільний початок будь-якого повідомлення: старший півбайт першого байта —
// тип, молодший — версія протоколу (тут 2). Далі — тіло на своїх зсувах.
static void put_header(uint8_t *m, uint8_t type) {
    m[0] = (uint8_t)((type << 4) | 0x02);   // тип у старші 4 біти, версія 2 — у молодші
}

// int32 → 4 байти буфера в little-endian (як лежить у пам'яті МК).
static void put_i32(uint8_t *p, int32_t v) {
    p[0] = (uint8_t)(v);
    p[1] = (uint8_t)(v >> 8);
    p[2] = (uint8_t)(v >> 16);
    p[3] = (uint8_t)(v >> 24);
}

static void put_u16(uint8_t *p, uint16_t v) {
    p[0] = (uint8_t)(v);
    p[1] = (uint8_t)(v >> 8);
}

// --- Basic ID: хто я. Тип ідентифікатора + сам рядок-ідентифікатор. ---
static void enc_basic_id(uint8_t m[ODID_MSG_SIZE], const char *uas_id) {
    memset(m, 0, ODID_MSG_SIZE);
    put_header(m, MSG_BASIC_ID);
    m[1] = 0x12;                 // тип ID: 1 = серійний номер, тип UA: 2 (напр. мультикоптер)
    // рядок-ідентифікатор із зсуву 2, максимум ODID_ID_LEN, решта лишається нулями
    strncpy((char *)&m[2], uas_id, ODID_ID_LEN);   // хвіст уже занулено через memset
}

// --- Location: де я і як лечу. Тут живуть цілі координати й кодована висота. ---
static void enc_location(uint8_t m[ODID_MSG_SIZE], const gps_fix_t *pos) {
    memset(m, 0, ODID_MSG_SIZE);
    put_header(m, MSG_LOCATION);

    // Байт статусу: старші 4 біти — статус польоту.
    // 2 = «у повітрі». Якщо фіксу нема — 0 = «невідомо», і координати НЕ пишемо.
    if (pos->valid) {
        m[1] = (2 << 4);
        put_i32(&m[5],  enc_deg(pos->lat_deg));   // широта на зсуві 5
        put_i32(&m[9],  enc_deg(pos->lon_deg));   // довгота на зсуві 9
        put_u16(&m[13], enc_alt(pos->alt_m));     // висота (баро) на зсуві 13
        put_u16(&m[15], enc_alt(pos->alt_m));     // висота (гео) — тут спрощено та сама
    } else {
        m[1] = (0 << 4);        // статус «невідомо»; координати лишаються нулями-заглушкою
        // важливо: приймач по статусу 0 знає, що нулям тут вірити НЕ можна
    }
}

// --- Operator ID: чий я. Реєстраційний номер оператора. ---
static void enc_operator(uint8_t m[ODID_MSG_SIZE], const char *operator_id) {
    memset(m, 0, ODID_MSG_SIZE);
    put_header(m, MSG_OPERATOR);
    m[1] = 0x00;                 // тип операторського ID: 0 = звичайний
    strncpy((char *)&m[2], operator_id, ODID_ID_LEN);
}
