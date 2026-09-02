#include "logstore.h"

#include <math.h>
#include <string.h>

static void encode(const log_record_t *r, uint8_t *b) {
    memcpy(b + 0, &r->t_ms, 4);
    b[4] = r->event;
    b[5] = r->critical;
    memcpy(b + 6, &r->count, 2);
    memcpy(b + 8, &r->min, 4);
    memcpy(b + 12, &r->max, 4);
    memcpy(b + 16, &r->avg, 4);
    memcpy(b + 20, &r->rms, 4);
}

static void decode(const uint8_t *b, log_record_t *r) {
    memcpy(&r->t_ms, b + 0, 4);
    r->event = b[4];
    r->critical = b[5];
    memcpy(&r->count, b + 6, 2);
    memcpy(&r->min, b + 8, 4);
    memcpy(&r->max, b + 12, 4);
    memcpy(&r->avg, b + 16, 4);
    memcpy(&r->rms, b + 20, 4);
}

// Записи цього сектора зараз зникнуть: покажчик зливу не має на них указувати.
static void discard_sector(logstore_t *s, uint16_t sector) {
    while (s->read_idx < s->write_idx &&
           (uint16_t)((s->read_idx % LOG_RING_CAPACITY) / LOG_SLOTS_PER_SECTOR) == sector) {
        s->read_idx++;
        s->overwritten++;
    }
}

static void ring_put(logstore_t *s, const log_record_t *r) {
    uint32_t pos = s->write_idx % LOG_RING_CAPACITY;
    uint16_t sector = (uint16_t)(pos / LOG_SLOTS_PER_SECTOR);
    uint16_t slot   = (uint16_t)(pos % LOG_SLOTS_PER_SECTOR);

    if (slot == 0U && s->dirty[sector]) {
        // Фонове завдання не встигло — стираємо просто зараз. Це 40–100 мс
        // блокування пам'яті посеред реального часу, тому такі випадки рахуємо.
        discard_sector(s, sector);
        if (plat_flash_erase(sector) != FLASH_OK) {
            s->dropped++;
            s->write_idx += LOG_SLOTS_PER_SECTOR;
            return;
        }
        s->dirty[sector] = false;
        s->blocking_erases++;
        if (s->preerase_target == sector) s->preerase_target = LOG_NO_TARGET;
    }

    uint8_t buf[LOG_RECORD_SIZE];
    encode(r, buf);
    if (plat_flash_write(sector, (uint16_t)(slot * LOG_RECORD_SIZE), buf, LOG_RECORD_SIZE) != FLASH_OK) {
        s->dropped++;
    } else {
        s->dirty[sector] = true;
        s->written++;
    }
    s->write_idx++;

    // Читач відстав більше ніж на повне коло: те, чого він не встиг злити,
    // фізично вже затерто, тож покажчик зливу підтягуємо до живих записів.
    if (s->write_idx - s->read_idx > LOG_RING_CAPACITY) {
        s->overwritten += (s->write_idx - s->read_idx) - LOG_RING_CAPACITY;
        s->read_idx = s->write_idx - LOG_RING_CAPACITY;
    }

    // Сектор заповнено на 80% — замовляємо стирання наступного у фон.
    if ((uint32_t)(slot + 1U) * 100U >= LOG_SLOTS_PER_SECTOR * LOG_PREERASE_PERCENT) {
        uint16_t next = (uint16_t)((sector + 1U) % LOG_RING_SECTORS);
        if (s->dirty[next]) s->preerase_target = next;
    }
}

static void blackbox_put(logstore_t *s, const log_record_t *r) {
    uint32_t pos = s->bb_idx % LOG_BLACKBOX_CAPACITY;
    uint16_t sector = (uint16_t)(LOG_RING_SECTORS + pos / LOG_SLOTS_PER_SECTOR);
    uint16_t slot   = (uint16_t)(pos % LOG_SLOTS_PER_SECTOR);

    if (slot == 0U && s->dirty[sector]) {
        // Пул теж скінченний, але його витісняє лише сам пул: рутинне кільце
        // сюди не дотягується ніколи, скільки б телеметрії не набігло.
        if (plat_flash_erase(sector) != FLASH_OK) {
            s->dropped++;
            s->bb_idx += LOG_SLOTS_PER_SECTOR;
            return;
        }
        s->dirty[sector] = false;
    }

    uint8_t buf[LOG_RECORD_SIZE];
    encode(r, buf);
    if (plat_flash_write(sector, (uint16_t)(slot * LOG_RECORD_SIZE), buf, LOG_RECORD_SIZE) != FLASH_OK) {
        s->dropped++;
    } else {
        s->dirty[sector] = true;
        s->written++;
    }
    s->bb_idx++;
}

// Пул чорної скриньки переживає перезавантаження: шукаємо перший вільний слот
// і дописуємо далі, а не стираємо докази попередньої аварії.
static uint32_t blackbox_scan(logstore_t *s) {
    uint32_t used = 0U;
    for (uint32_t pos = 0U; pos < LOG_BLACKBOX_CAPACITY; pos++) {
        uint16_t sector = (uint16_t)(LOG_RING_SECTORS + pos / LOG_SLOTS_PER_SECTOR);
        uint16_t slot   = (uint16_t)(pos % LOG_SLOTS_PER_SECTOR);
        uint8_t marker;
        if (plat_flash_read(sector, (uint16_t)(slot * LOG_RECORD_SIZE + 4U), &marker, 1U) != FLASH_OK) break;
        if (marker == 0xFFU) break;   // стерта комірка — тут пул закінчився
        s->dirty[sector] = true;
        used = pos + 1U;
    }
    return used;
}

void logstore_init(logstore_t *s) {
    memset(s, 0, sizeof *s);
    s->preerase_target = LOG_NO_TARGET;

    for (uint16_t i = 0; i < LOG_RING_SECTORS; i++) {
        if (plat_flash_erase(i) != FLASH_OK) s->dropped++;
        s->dirty[i] = false;
    }
    s->bb_idx = blackbox_scan(s);
}

void logstore_sample(logstore_t *s, uint32_t t_ms, float value, uint32_t offline_ms) {
    // Дворівнева політика: онлайн пишемо мінімум (усе й так летить в ефір),
    // перші 10 с офлайну — повні 50 Гц, далі згортаємо секунду в одну пачку.
    uint16_t need;
    if (offline_ms == 0U)         need = 25U;
    else if (offline_ms < 10000U) need = 1U;
    else                          need = (uint16_t)(1000U / LOG_SAMPLE_PERIOD_MS);

    if (s->win_count == 0U) {
        s->win_start_ms = t_ms;
        s->w_min = value;
        s->w_max = value;
        s->w_sum = 0.0f;
        s->w_sq  = 0.0f;
    }
    if (value < s->w_min) s->w_min = value;
    if (value > s->w_max) s->w_max = value;
    s->w_sum += value;
    s->w_sq  += value * value;
    s->win_count++;

    if (s->win_count >= need) {
        float n = (float)s->win_count;
        log_record_t r;
        r.t_ms = s->win_start_ms;
        r.event = LOG_EV_SAMPLE;
        r.critical = 0U;
        r.count = s->win_count;
        r.min = s->w_min;
        r.max = s->w_max;
        r.avg = s->w_sum / n;
        r.rms = sqrtf(s->w_sq / n);
        ring_put(s, &r);
        s->win_count = 0U;
    }
}

void logstore_event(logstore_t *s, uint32_t t_ms, uint8_t event, bool critical) {
    log_record_t r;
    r.t_ms = t_ms;
    r.event = event;
    r.critical = critical ? 1U : 0U;
    r.count = 0U;
    r.min = 0.0f;
    r.max = 0.0f;
    r.avg = 0.0f;
    r.rms = 0.0f;

    // Критична подія лягає в захищений пул і, копією, у чергу на злив.
    if (critical) blackbox_put(s, &r);
    ring_put(s, &r);
}

void logstore_background(logstore_t *s) {
    if (s->preerase_target == LOG_NO_TARGET) return;
    uint16_t target = s->preerase_target;
    s->preerase_target = LOG_NO_TARGET;

    discard_sector(s, target);
    if (plat_flash_erase(target) == FLASH_OK) s->dirty[target] = false;
    else s->dropped++;
}

size_t logstore_drain(logstore_t *s, size_t budget_bytes) {
    size_t sent_total = 0U;

    while (s->read_idx < s->write_idx && budget_bytes >= LOG_RECORD_SIZE) {
        uint32_t pos = s->read_idx % LOG_RING_CAPACITY;
        uint16_t sector = (uint16_t)(pos / LOG_SLOTS_PER_SECTOR);
        uint16_t slot   = (uint16_t)(pos % LOG_SLOTS_PER_SECTOR);

        uint8_t buf[LOG_RECORD_SIZE];
        if (plat_flash_read(sector, (uint16_t)(slot * LOG_RECORD_SIZE), buf, LOG_RECORD_SIZE) != FLASH_OK) {
            s->read_idx++;   // битий слот пропускаємо, злив на ньому не спиняється
            continue;
        }
        if (plat_radio_send(buf, LOG_RECORD_SIZE) < LOG_RECORD_SIZE) {
            break;           // канал не прийняв — покажчик лишаємо, спробуємо потім
        }
        s->read_idx++;
        budget_bytes -= LOG_RECORD_SIZE;
        sent_total += LOG_RECORD_SIZE;
    }
    return sent_total;
}

uint32_t logstore_pending(const logstore_t *s) { return s->write_idx - s->read_idx; }

uint32_t logstore_blackbox_count(const logstore_t *s) {
    return (s->bb_idx < LOG_BLACKBOX_CAPACITY) ? s->bb_idx : LOG_BLACKBOX_CAPACITY;
}

bool logstore_blackbox_get(const logstore_t *s, uint32_t index, log_record_t *out) {
    uint32_t count = logstore_blackbox_count(s);
    if (index >= count) return false;

    uint32_t pos = (s->bb_idx - count + index) % LOG_BLACKBOX_CAPACITY;
    uint16_t sector = (uint16_t)(LOG_RING_SECTORS + pos / LOG_SLOTS_PER_SECTOR);
    uint16_t slot   = (uint16_t)(pos % LOG_SLOTS_PER_SECTOR);

    uint8_t buf[LOG_RECORD_SIZE];
    if (plat_flash_read(sector, (uint16_t)(slot * LOG_RECORD_SIZE), buf, LOG_RECORD_SIZE) != FLASH_OK) return false;
    if (buf[4] == 0xFFU) return false;   // слот стерто разом із сектором пулу
    decode(buf, out);
    return true;
}
