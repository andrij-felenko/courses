// Викликати кожен запис у порядку від найстарішого до найновішого.
typedef void (*dump_sink_t)(const log_rec_t *rec, void *ctx);

void ring_dump(dump_sink_t sink, void *ctx) {
    uint32_t slots = (g_part->size / SECTOR_SZ) * RECS_PER_SECTOR;   // дійсні слоти, без хвостів

    // Знайти найстаріший дійсний запис: найменший seq серед незагорнутих.
    // Проста й надійна стратегія: зібрати всі дійсні, віддати за зростанням seq.
    // Для дрібного кільця двопрохідний скан дешевший за сортування в RAM.
    uint32_t min_seq = 0xFFFFFFFFu;
    bool any = false;
    for (uint32_t i = 0; i < slots; i++) {
        log_rec_t r; esp_partition_read(g_part, slot_off(i), &r, sizeof(r));
        if (r.seq == 0xFFFFFFFFu) continue;
        if (!any || r.seq < min_seq) { min_seq = r.seq; any = true; }
    }
    if (!any) return;                              // журнал порожній

    // Віддавати поспіль зростаючі seq, читаючи кожен прямо з Flash.
    for (uint32_t sq = min_seq; sq != g_seq; sq++) {
        for (uint32_t i = 0; i < slots; i++) {
            log_rec_t r; esp_partition_read(g_part, slot_off(i), &r, sizeof(r));
            if (r.seq == sq) { sink(&r, ctx); break; }
        }
    }
}
