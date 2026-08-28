uint32_t read_idcode(void) {
    uint32_t id = 0;
    for (int i = 0; i < 32; i++) {
        // TMS=0 усі 31 крок, TMS=1 на останньому — виходимо зі Shift-DR.
        uint8_t last = (i == 31);
        uint8_t bit  = tap_clock(last, 0);   // засуваємо 0, ловимо біт коду
        id |= (uint32_t)bit << i;            // IDCODE іде молодшим бітом уперед
    }
    return id;                                // напр. 0x4BA00477 — ядро ARM
}
