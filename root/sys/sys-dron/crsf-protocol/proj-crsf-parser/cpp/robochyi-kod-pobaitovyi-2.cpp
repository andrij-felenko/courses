// ── Константи протоколу ──────────────────────────────────────────────────────
#define CRSF_SYNC_BYTE   0xC8   // байт-старт (він же адреса польотного контролера)
#define CRSF_LEN_MIN     2      // мінімум поля довжини: тип(1) + CRC(1)
#define CRSF_LEN_MAX     62     // максимум: кадр 64 − старт(1) − довжина(1)
#define CRSF_FRAME_MAX   64     // повний кадр разом зі стартом і CRC

// Типи кадрів, які розбираємо
#define CRSF_TYPE_LINK_STATISTICS   0x14
#define CRSF_TYPE_RC_CHANNELS_PACKED 0x16

// ── Стани автомата ───────────────────────────────────────────────────────────
typedef enum {
    ST_SYNC = 0,   // шукаємо байт-старт 0xC8
    ST_LEN,        // читаємо й перевіряємо поле довжини
    ST_BODY        // добираємо тип + дані + CRC
} CrsfState;

typedef struct {
    CrsfState state;
    uint8_t   buf[CRSF_FRAME_MAX]; // сюди складаємо кадр (без байта-старту)
    uint8_t   need;   // скільки байтів має бути в тілі (== поле довжини)
    uint8_t   got;    // скільки байтів тіла вже назбирали
} CrsfParser;

void crsf_parser_reset(CrsfParser *p) {
    p->state = ST_SYNC;
    p->need = 0;
    p->got  = 0;
}
