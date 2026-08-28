int wl_write(uint32_t lba, const void *data) {
    commit_hdr_t *c;
    uint16_t old, nb;

    if (lba >= N_LOG) return -1;

    nb = heap_pop_min();                   // найменш зношений вільний блок
    if (nb == NO_BLOCK) return -1;         // пул порожній — це вже робота збирача сміття
    // блок уже стертий і вже має EC-заголовок: їх поставив free_block

    for (uint16_t p = 0; p < DATA_PAGES; p++)
        if (flash_write_page(nb, DATA_PAGE + p,
                             (const uint8_t *)data + p * PAGE_SIZE) != 0) goto bad;

    memset(pbuf, 0xFF, PAGE_SIZE);
    c = (commit_hdr_t *)pbuf;
    c->magic    = COMMIT_MAGIC;
    c->lba      = lba;
    c->seq      = seq_next++;              // кожен запис — з новим, більшим номером
    c->data_crc = crc32(data, DATA_SIZE);
    c->crc      = crc32(c, sizeof *c - 4);

    // КОМІТ. До цього рядка блок — сміття; після нього — власник lba.
    if (flash_write_page(nb, COMMIT_PAGE, pbuf) != 0) goto bad;

    old = map[lba];
    map[lba] = nb;                         // таблиця в RAM; у флеші її нема й не треба
    state[nb] = BS_USED;

    if (old != NO_BLOCK) free_block(old);  // старий більше нікому не потрібен

    if (++op_count % WL_CHECK_EVERY == 0) static_wl_step();
    return 0;

bad:
    state[nb] = BS_BAD;                    // блок підвів — викидаємо його назавжди
    return -1;
}
