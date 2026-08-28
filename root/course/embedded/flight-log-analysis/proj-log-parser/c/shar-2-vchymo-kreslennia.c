// Розібрати FMT-запис і покласти креслення в таблицю.
// Розкладка FMT (після 3 байтів шапки, тобто від rec+3):
//   +0  type    (1 байт)  — код типу, який описуємо
//   +1  length  (1 байт)  — повна довжина такого запису
//   +2  name    (4 байти) — ім'я, напр. "ATT\0"
//   +6  format  (16 байтів)— рядок типів, напр. "Qffffff"
//   +22 labels  (64 байти) — імена полів через кому (тут поки не беремо)
static void learn_format(const uint8_t *rec) {
    MsgFormat f;
    memset(&f, 0, sizeof f);
    f.type   = rec[3 + 0];
    f.length = rec[3 + 1];
    memcpy(f.name,   rec + 3 + 2, 4);   f.name[4]    = '\0';
    memcpy(f.format, rec + 3 + 6, 16);  f.format[16] = '\0';
    f.n_fields = (uint8_t)strlen(f.format);
    fmt_table[f.type] = f;              // тепер знаємо, як читати цей тип
}

// Головний диспетчер: FMT — вчимо, решту — віддаємо декодеру.
static void feed_record(const uint8_t *rec) {
    uint8_t msg_type = rec[2];          // rec[0],rec[1] = 0xA3,0x95

    if (msg_type == LOG_FORMAT_MSG) {   // це креслення — запам'ятовуємо
        learn_format(rec);
        return;
    }

    const MsgFormat *f = &fmt_table[msg_type];
    if (f->length == 0) return;         // ПАСТКА 1: креслення ще не бачили — пропуск
    decode_record(f, rec);              // розбираємо дані за кресленням
}
