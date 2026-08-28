// Тут «не впізнано» — це просто невдача власного декодера: RMT віддав сирі
// символи, а таблиця протоколу не зійшлася. Дамп робимо самі.
if (!nec_decode(frame.received_symbols, frame.num_symbols, &addr, &cmd)) {
    ESP_LOGW(TAG, "протокол не впізнано, символів: %d", frame.num_symbols);
    for (size_t i = 0; i < frame.num_symbols; i++) {
        const rmt_symbol_word_t *s = &frame.received_symbols[i];
        ESP_LOGW(TAG, "  %c%u  %c%u",                    // рівень і тривалість, мкс
                 s->level0 ? '+' : '-', (unsigned)s->duration0,
                 s->level1 ? '+' : '-', (unsigned)s->duration1);
    }
}
