void cc_reader_poll(void) {
    if (st == ST_DETACHED) {
        // Шукаємо появу: міряємо ОБИДВІ ноги, бо ще не знаємо, котру встромили.
        uint16_t v1 = CFG.read_mv(CC_LINE_1);
        uint16_t v2 = CFG.read_mv(CC_LINE_2);
        if (v1 < CC_PRESENT_MV && v2 < CC_PRESENT_MV) return;  // обидві висять — чекаємо далі

        // Котрась ожила — фіксуємо активну лінію ОДИН раз і входимо в дебаунс.
        active = (v1 >= v2) ? CC_LINE_1 : CC_LINE_2;
        st = ST_DEBOUNCING;
        ring_reset(&ring);
        cand = CC_NONE; cand_n = 0;
        return;  // саме вимірювання активної лінії зробимо вже наступним проходом
    }

    // ST_DEBOUNCING або ST_ATTACHED: читаємо ЛИШЕ активну лінію.
    uint16_t mv = ring_push(&ring, CFG.read_mv(active));

    // Активна лінія впала під поріг присутності → кабель зник.
    if (mv < CC_PRESENT_MV) { go_detached(); return; }

    cc_level_t lvl = decode(mv, level);   // гістерезис від поточного сталого рівня

    // Дебаунс: рівень визнаємо лише після CC_STABLE_N однакових поспіль.
    if (lvl == cand) {
        if (cand_n < CC_STABLE_N) cand_n++;
    } else {
        cand = lvl; cand_n = 1;           // рівень смикнувся — рахуємо наново
    }
    if (cand_n < CC_STABLE_N) return;     // ще не впевнені — нічого не міняємо

    // Кандидат став сталим. Що це для машини станів?
    if (st == ST_DEBOUNCING) {
        if (cand == CC_NONE) return;      // «нема» не вважаємо під'єднанням — чекаємо рівня
        level = cand;
        st = ST_ATTACHED;
        emit(CC_EV_ATTACHED);             // АЖ ТЕПЕР: рівень сталий і дійсний
    } else { // ST_ATTACHED
        if (cand != level) {              // джерело переуклало контракт на ходу
            level = cand;
            emit(CC_EV_LEVEL);
        }
    }
}

cc_level_t cc_reader_level(void)  { return level; }
cc_line_t  cc_reader_active(void) { return active; }
bool       cc_reader_attached(void){ return st == ST_ATTACHED; }
