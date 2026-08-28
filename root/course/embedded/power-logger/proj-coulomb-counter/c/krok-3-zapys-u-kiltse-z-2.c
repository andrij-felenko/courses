#define LOG_PART_LABEL  "log"          // окрема розмічена область під журнал
#define SECTOR_SZ       4096u
#define RECS_PER_SECTOR (SECTOR_SZ / sizeof(log_rec_t))   // 341 запис на сектор

static const esp_partition_t *g_part;   // знайдена область журналу
static uint32_t g_write_off;            // зсув наступного запису в межах області
static uint32_t g_seq;                  // наступний номер запису

// Слот (наскрізний номер запису) → зсув у Flash, перескочивши 4-байтові хвости секторів.
static inline uint32_t slot_off(uint32_t idx) {
    return (idx / RECS_PER_SECTOR) * SECTOR_SZ + (idx % RECS_PER_SECTOR) * sizeof(log_rec_t);
}

// Дописати один запис; стерти сектор лише на його межі.
static esp_err_t ring_append(uint32_t epoch_s, uint32_t charge_mC) {
    // Запис не влазить у хвіст сектора? (4096 не кратне 12 — 341 запис і 4 байти хвоста).
    if ((g_write_off % SECTOR_SZ) + sizeof(log_rec_t) > SECTOR_SZ)
        g_write_off = (g_write_off / SECTOR_SZ + 1) * SECTOR_SZ;   // на початок наступного сектора

    // Вийшли за область журналу — загорнути кільце на початок.
    if (g_write_off + sizeof(log_rec_t) > g_part->size)
        g_write_off = 0;                                  // загорнули по колу

    // На початку кожного сектора — стерти його (повертає в 0xFF), бо NOR пише лише 1→0.
    if (g_write_off % SECTOR_SZ == 0) {
        esp_err_t e = esp_partition_erase_range(g_part, g_write_off, SECTOR_SZ);
        if (e != ESP_OK) return e;
    }

    log_rec_t rec = { .seq = g_seq, .epoch_s = epoch_s, .charge_mC = charge_mC };
    esp_err_t e = esp_partition_write(g_part, g_write_off, &rec, sizeof(rec));
    if (e != ESP_OK) return e;

    g_write_off += sizeof(log_rec_t);
    g_seq++;
    return ESP_OK;
}
