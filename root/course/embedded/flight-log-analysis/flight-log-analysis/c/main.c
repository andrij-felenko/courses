// Кожен запис починається з маркера 0xA3 0x95 і байта-типу.
// FMT-запис (type == 0x80) описує решту типів: скільки байтів,
// які поля. DATA-записи розбираємо вже за вивченим кресленням.

typedef struct {
    uint8_t  type;         // числовий код повідомлення (напр. ATT)
    uint8_t  length;       // скільки байтів займає один такий запис
    char     name[5];      // "ATT", "GPS", "BAT"...
    char     fmt[17];      // рядок типів полів: "Qff...", де Q=uint64, f=float
} MsgFormat;

static MsgFormat fmt_table[256];   // креслення за кодом типу

void feed_record(const uint8_t *rec) {
    uint8_t msg_type = rec[2];     // байти [0],[1] — маркер 0xA3,0x95

    if (msg_type == 0x80) {        // це креслення FMT — запам'ятовуємо
        MsgFormat f;
        f.type   = rec[3];
        f.length = rec[4];
        memcpy(f.name, rec + 5, 4);  f.name[4] = 0;
        memcpy(f.fmt,  rec + 9, 16); f.fmt[16] = 0;
        fmt_table[f.type] = f;       // тепер знаємо, як читати цей тип
        return;
    }

    MsgFormat *f = &fmt_table[msg_type];   // креслення для цього рядка
    if (f->length == 0) return;            // креслення ще не бачили — пропуск
    decode_by_format(f, rec + 3);          // розбираємо поля за f->fmt
}
