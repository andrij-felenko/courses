// Пройти сирий буфер лога довжиною len, згодовуючи записи диспетчеру.
static void parse_log(const uint8_t *buf, size_t len) {
    size_t i = 0;
    while (i + 3 <= len) {
        // 1) синхронізація: стоїмо на маркері?
        if (buf[i] != HEAD_BYTE1 || buf[i + 1] != HEAD_BYTE2) {
            i++;                        // ні — повземо вперед, шукаючи маркер
            continue;
        }
        uint8_t type = buf[i + 2];

        // 2) яка довжина цього запису?
        size_t rec_len;
        if (type == LOG_FORMAT_MSG)
            rec_len = 3 + 2 + 4 + 16 + 64;   // FMT — фіксовані 89 байтів
        else if (fmt_table[type].length)
            rec_len = fmt_table[type].length; // з вивченого креслення
        else {
            i++;                        // креслення ще нема — крок на байт і далі
            continue;
        }

        if (i + rec_len > len) break;   // хвіст обірваний — виходимо

        feed_record(buf + i);           // цілий запис — у диспетчер
        i += rec_len;                   // стрибок рівно на довжину запису
    }
}
