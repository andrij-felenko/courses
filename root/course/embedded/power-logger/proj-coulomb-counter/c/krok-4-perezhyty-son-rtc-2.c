// Відновити голову кільця проходом по Flash: найновіший запис — де seq найбільший.
static void ring_recover_head(uint32_t *out_off, uint32_t *out_seq) {
    uint32_t best_seq = 0;          // найбільший побачений seq
    uint32_t best_off = 0;          // зсув запису з найбільшим seq
    bool found = false;
    uint32_t slots = (g_part->size / SECTOR_SZ) * RECS_PER_SECTOR;   // дійсні слоти, без хвостів

    for (uint32_t i = 0; i < slots; i++) {
        log_rec_t rec;
        uint32_t off = slot_off(i);                      // слот → зсув, перескочивши хвости
        esp_partition_read(g_part, off, &rec, sizeof(rec));
        if (rec.seq == 0xFFFFFFFFu) continue;            // стерта комірка — пропустити
        if (!found || rec.seq > best_seq) {              // новіший запис
            best_seq = rec.seq;
            best_off = off;
            found = true;
        }
    }

    if (!found) {                    // кільце ще зовсім порожнє
        *out_off = 0;
        *out_seq = 0;
    } else {                         // писати — відразу за найновішим записом
        *out_off = best_off + sizeof(log_rec_t);
        if (*out_off + sizeof(log_rec_t) > g_part->size) *out_off = 0;
        *out_seq = best_seq + 1;
    }
}
