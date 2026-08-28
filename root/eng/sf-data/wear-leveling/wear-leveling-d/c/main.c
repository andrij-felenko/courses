// Кільце з N секторів; у кожному — один запис {seq, value, crc}.
// «Жива» комірка та, у якої найбільший seq; писати треба в наступну за нею.
#define N_SECT     64u            // скільки секторів ділять знос
#define SECT_SIZE  4096u          // розмір сектора Flash, байтів
#define MAGIC      0xC0FFEEu

typedef struct {                  // один слот = одна фізична комірка
    uint32_t magic;               // позначка «тут є валідний запис»
    uint32_t seq;                 // номер покоління: що більший — то свіжіший
    uint32_t value;               // власне корисні дані (наш лічильник)
    uint32_t crc;                 // контроль цілості запису
} record_t;

static uint32_t g_seq;            // seq останнього запису
static uint32_t g_slot;          // індекс сектора з останнім записом

// Знайти найсвіжіший запис серед усіх секторів (виклик раз, на старті).
static bool counter_mount(uint32_t base_addr, uint32_t *out_value) {
    uint32_t best_seq = 0; bool found = false;
    for (uint32_t i = 0; i < N_SECT; i++) {
        record_t r;
        flash_read(base_addr + i * SECT_SIZE, &r, sizeof r);
        if (r.magic != MAGIC) continue;            // порожній/стертий сектор
        if (crc32(&r, sizeof r - 4) != r.crc) continue;  // битий запис — пропустити
        if (!found || r.seq > best_seq) {          // запам'ятати найсвіжіший
            best_seq = r.seq; g_slot = i; *out_value = r.value; found = true;
        }
    }
    g_seq = found ? best_seq : 0;
    if (!found) *out_value = 0;
    return found;
}

// Записати нове значення — у НАСТУПНИЙ сектор по колу (ось і все вирівнювання).
static void counter_save(uint32_t base_addr, uint32_t value) {
    uint32_t next = (g_slot + 1u) % N_SECT;        // ротація: наступний сектор
    uint32_t addr = base_addr + next * SECT_SIZE;
    flash_erase_sector(addr);                      // одне стирання раз на оберт
    record_t r = { MAGIC, g_seq + 1u, value, 0 };  // новий seq — на одиницю більший
    r.crc = crc32(&r, sizeof r - 4);
    flash_write(addr, &r, sizeof r);               // дописуємо у вільну комірку
    g_slot = next; g_seq += 1u;                    // тепер «жива» комірка — ця
}
