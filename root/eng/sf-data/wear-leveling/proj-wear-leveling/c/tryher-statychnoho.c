static int read_commit_hdr(uint16_t b, commit_hdr_t *out) {
    commit_hdr_t *h = (commit_hdr_t *)pbuf;
    if (flash_read_page(b, COMMIT_PAGE, pbuf) != 0) return -1;
    if (h->magic != COMMIT_MAGIC) return -1;
    if (crc32(h, sizeof *h - 4) != h->crc) return -1;
    *out = *h;                             // копія: pbuf зараз знадобиться під дані
    return 0;
}

// Рідкісний крок: один прохід по чипу і, якщо розкид завеликий, одне перенесення.
static void static_wl_step(void) {
    uint16_t src = NO_BLOCK, dst = NO_BLOCK;
    uint32_t src_ec = 0xFFFFFFFFu, dst_ec = 0;
    commit_hdr_t ch;
    uint32_t crc = CRC32_INIT;

    if (heap_n <= WL_RESERVE) return;      // останні вільні блоки — не наші

    for (uint16_t b = 0; b < N_PHYS; b++) {
        if (state[b] == BS_USED && ec[b] < src_ec) { src_ec = ec[b]; src = b; }
        if (state[b] == BS_FREE && ec[b] > dst_ec) { dst_ec = ec[b]; dst = b; }
    }
    if (src == NO_BLOCK || dst == NO_BLOCK) return;
    if (dst_ec - src_ec < WL_THRESHOLD) return;    // розкид у нормі — не чіпаємо

    if (read_commit_hdr(src, &ch) != 0) return;    // звідси візьмемо lba холодних даних
    heap_take(hpos[dst]);                          // ціль виходить із вільного пулу

    for (uint16_t p = 0; p < DATA_PAGES; p++) {
        if (flash_read_page(src, DATA_PAGE + p, pbuf) != 0)  goto drop_dst;
        crc = crc32_update(crc, pbuf, PAGE_SIZE);
        if (flash_write_page(dst, DATA_PAGE + p, pbuf) != 0) goto bad_dst;
    }
    if ((crc ^ 0xFFFFFFFFu) != ch.data_crc) goto drop_dst;   // холодне зіпсувалося

    ch.seq = seq_next++;                   // новий номер — щоб виграв у старої копії
    ch.crc = crc32(&ch, sizeof ch - 4);
    memset(pbuf, 0xFF, PAGE_SIZE);
    memcpy(pbuf, &ch, sizeof ch);
    if (flash_write_page(dst, COMMIT_PAGE, pbuf) != 0) goto bad_dst;

    map[ch.lba] = dst;                     // холодні дані живуть тепер на зношеному
    state[dst]  = BS_USED;
    free_block(src);                       // а молодий іде працювати в пул
    return;

drop_dst:
    free_block(dst);                       // без коміту dst — просто сміття: стерти й у пул
    return;
bad_dst:
    state[dst] = BS_BAD;
}
