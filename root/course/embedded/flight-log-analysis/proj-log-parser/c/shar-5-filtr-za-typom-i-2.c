static AttSeries g_att;   // сюди складаємо криві ATT

static void feed_record(const uint8_t *rec) {
    uint8_t msg_type = rec[2];

    if (msg_type == LOG_FORMAT_MSG) { learn_format(rec); return; }

    const MsgFormat *f = &fmt_table[msg_type];
    if (f->length == 0) return;                 // креслення ще нема — пропуск

    if (strcmp(f->name, "ATT") == 0)            // ← ФІЛЬТР за типом повідомлення
        collect_att(f, rec, &g_att);
    // інші типи (GPS, BAT, VIBE…) — тут можна додати свої збирачі
}
