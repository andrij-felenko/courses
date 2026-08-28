int wl_mount(void) {
    ec_hdr_t     *eh = (ec_hdr_t *)pbuf;
    commit_hdr_t  ch, rh;
    uint8_t       ec_ok[N_PHYS];
    uint64_t      ec_sum = 0;
    uint32_t      ec_cnt = 0, mean;

    for (uint32_t i = 0; i < N_LOG;  i++) map[i]  = NO_BLOCK;
    for (uint16_t b = 0; b < N_PHYS; b++) hpos[b] = NO_BLOCK;
    heap_n = 0; seq_next = 0; op_count = 0;

    // ── прохід 1: лічильники стирань ──
    for (uint16_t b = 0; b < N_PHYS; b++) {
        state[b] = BS_FREE; ec_ok[b] = 0; ec[b] = 0;
        if (flash_read_page(b, EC_PAGE, pbuf) != 0) { state[b] = BS_BAD; continue; }
        if (eh->magic == EC_MAGIC && crc32(eh, sizeof *eh - 4) == eh->crc) {
            ec[b] = eh->ec; ec_ok[b] = 1;
            ec_sum += eh->ec; ec_cnt++;
        }
        // інакше: живлення зникло МІЖ стиранням і записом заголовка —
        // лічильник цього блоку втрачено назавжди, відновити нізвідки
    }
    // втраченому лічильнику даємо середній по чипу: так блок не виглядатиме
    // ні підозріло молодим (і не збиратиме на себе весь знос), ні передчасно старим
    mean = ec_cnt ? (uint32_t)(ec_sum / ec_cnt) : 0;
    for (uint16_t b = 0; b < N_PHYS; b++)
        if (!ec_ok[b] && state[b] != BS_BAD) ec[b] = mean;

    // ── прохід 2: хто чим володіє; суперечки вирішує seq ──
    for (uint16_t b = 0; b < N_PHYS; b++) {
        if (state[b] == BS_BAD) continue;
        if (read_commit_hdr(b, &ch) != 0) continue;     // коміту нема → блок вільний
        if (ch.lba >= N_LOG) continue;                  // сміття від чужого формату
        if (ch.seq >= seq_next) seq_next = ch.seq + 1;  // продовжимо нумерацію звідси

        uint16_t rival = map[ch.lba];
        if (rival == NO_BLOCK) { map[ch.lba] = b; state[b] = BS_USED; continue; }

        // ДВА блоки на одну адресу: зрив між комітом і стиранням старого.
        if (read_commit_hdr(rival, &rh) != 0) continue;
        if (ch.seq > rh.seq) { map[ch.lba] = b; state[b] = BS_USED; state[rival] = BS_FREE; }
        else                 { state[b] = BS_FREE; }
    }

    // ── прохід 3: усе, що не зайняте, — у пул ──
    for (uint16_t b = 0; b < N_PHYS; b++) {
        if (state[b] != BS_FREE) continue;
        if (!block_is_clean(b)) { free_block(b); continue; }   // недописаний запис — стерти
        if (!ec_ok[b] && write_ec_hdr(b, ec[b]) != 0) { free_block(b); continue; }
        heap_push(b);                                          // чистий — просто у пул
    }
    return 0;
}
