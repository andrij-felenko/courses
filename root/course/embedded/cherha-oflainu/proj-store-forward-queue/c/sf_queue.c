#include "sf_queue.h"

#include <string.h>

typedef enum {
    REC_OK = 0,
    REC_BLANK,   /* стерта область: далі в цьому секторі записів немає */
    REC_CORRUPT, /* чужа преамбула, немислима довжина або битий CRC    */
    REC_IO,      /* носій не відповів                                  */
} rec_state_t;

/* Порівняння номерів через знакову різницю: коли лічильник колись
 * перекотиться через 2^32, «більший» лишиться більшим. */
static inline bool seq_after(uint32_t a, uint32_t b)
{
    return (int32_t)(a - b) > 0;
}

static inline uint32_t next_sector(const sf_queue_t *q, uint32_t s)
{
    return (s + 1u) % q->sector_count;
}

static inline uint32_t sector_addr(const sf_queue_t *q, uint32_t s)
{
    return q->base_addr + s * q->sector_size;
}

static inline bool is_empty(const sf_queue_t *q)
{
    return q->tail_sector == q->head_sector && q->tail_offset >= q->head_offset;
}

/* Скільки байтів від хвоста до вказаної точки кільця. */
static uint32_t pos_from_tail(const sf_queue_t *q, uint32_t sec, uint32_t off)
{
    const uint32_t d = (sec + q->sector_count - q->tail_sector) % q->sector_count;
    return d * q->sector_size + off;
}

/* Курсор історії мусить лишатися між хвостом і головою. Витіснення
 * сектора або пакетна квитанція можуть його обігнати — тоді він просто
 * стає на хвіст і читає ще раз. */
static void sync_drain(sf_queue_t *q)
{
    const uint32_t drain = pos_from_tail(q, q->drain_sector, q->drain_offset);
    const uint32_t head = pos_from_tail(q, q->head_sector, q->head_offset);

    if (drain < q->tail_offset || drain > head) {
        q->drain_sector = q->tail_sector;
        q->drain_offset = q->tail_offset;
    }
}

/* ---------------------------------------------------------------- носій */

static rec_state_t read_record(sf_queue_t *q, uint32_t sec, uint32_t off, sf_record_t *out)
{
    const uint32_t addr = sector_addr(q, sec) + off;

    if (off + SF_HEADER_SIZE > q->sector_size) {
        return REC_BLANK; /* у хвості сектора не влізе навіть заголовок */
    }

    if (q->flash->read(q->flash->ctx, addr, q->scratch, SF_HEADER_SIZE) != SF_FLASH_OK) {
        q->stats.flash_errors++;
        return REC_IO;
    }

    /* Стерті одиниці — не пошкодження, а межа записаного. */
    if (sf_frame_is_blank(q->scratch, SF_HEADER_SIZE)) {
        return REC_BLANK;
    }

    sf_header_t hdr;
    if (!sf_frame_parse_header(q->scratch, &hdr)) {
        return REC_CORRUPT;
    }

    const uint32_t stride = sf_frame_stride(hdr.payload_len);
    if (off + stride > q->sector_size) {
        return REC_CORRUPT; /* довжина обіцяє більше, ніж лишилось у секторі */
    }

    if (q->flash->read(q->flash->ctx, addr, q->scratch, stride) != SF_FLASH_OK) {
        q->stats.flash_errors++;
        return REC_IO;
    }
    if (!sf_frame_check_crc(q->scratch, hdr.payload_len)) {
        return REC_CORRUPT;
    }

    out->hdr = hdr;
    out->payload = q->scratch + SF_HEADER_SIZE;
    out->stride = stride;
    out->sector = sec;
    out->offset = off;
    return REC_OK;
}

/* Чи вільна ділянка під новий кадр. Перерваний запис лишає по собі
 * нулі там, де черга чекає одиниць: дозапис поверх них дав би кадр,
 * який ніколи не зійдеться за CRC. */
static bool area_is_blank(sf_queue_t *q, uint32_t sec, uint32_t off, uint32_t len)
{
    uint8_t probe[64];
    uint32_t addr = sector_addr(q, sec) + off;

    while (len > 0u) {
        const uint32_t chunk = (len < sizeof(probe)) ? len : (uint32_t)sizeof(probe);

        if (q->flash->read(q->flash->ctx, addr, probe, chunk) != SF_FLASH_OK) {
            q->stats.flash_errors++;
            return false;
        }
        if (!sf_frame_is_blank(probe, chunk)) {
            return false;
        }
        addr += chunk;
        len -= chunk;
    }
    return true;
}

/* ------------------------------------------------------------- рух хвоста */

static void roll_tail(sf_queue_t *q)
{
    q->tail_sector = next_sector(q, q->tail_sector);
    q->tail_offset = 0;
    sync_drain(q);
}

/* Хвіст упхнувся в нечитабельне. Перескочити всередині сектора нема як:
 * межі наступного кадру ми знаємо тільки з попереднього заголовка. Тому
 * жертвуємо рештою сектора — це дешевше за вічне заклинювання черги. */
static void skip_bad_tail(sf_queue_t *q)
{
    q->stats.corrupt_records++;
    if (q->tail_sector != q->head_sector) {
        roll_tail(q);
    } else {
        q->tail_offset = q->head_offset;
        sync_drain(q);
    }
}

/* Просунути хвіст по всіх квитованих кадрах підряд. Тільки суцільно:
 * перший неквитований кадр зупиняє рух, навіть якщо за ним лежать
 * квитовані живою колією. */
static void advance_tail(sf_queue_t *q)
{
    const uint32_t guard = q->sector_count * (q->sector_size / SF_HEADER_SIZE) + 8u;

    for (uint32_t step = 0; step < guard; step++) {
        sf_record_t rec;

        if (is_empty(q)) {
            sf_ackset_prune_below(&q->ack, q->next_seq);
            return;
        }

        switch (read_record(q, q->tail_sector, q->tail_offset, &rec)) {
        case REC_IO:
            return;
        case REC_BLANK:
            if (q->tail_sector == q->head_sector) {
                return;
            }
            roll_tail(q);
            continue;
        case REC_CORRUPT:
            skip_bad_tail(q);
            continue;
        case REC_OK:
        default:
            break;
        }

        if (!sf_ackset_contains(&q->ack, rec.hdr.seq)) {
            /* Дійшли до найстарішого неквитованого — далі хвіст не йде. */
            sf_ackset_prune_below(&q->ack, rec.hdr.seq);
            return;
        }

        q->tail_offset += rec.stride;
        sf_ackset_prune_below(&q->ack, rec.hdr.seq + 1u);

        if (q->tail_offset + SF_HEADER_SIZE > q->sector_size &&
            q->tail_sector != q->head_sector) {
            roll_tail(q);
        } else {
            sync_drain(q);
        }
    }
}

/* --------------------------------------------------------------- ініціація */

sf_err_t sf_queue_init(sf_queue_t *q, const sf_flash_dev_t *flash, uint32_t base_addr,
                       uint32_t sector_count, const sf_lock_t *lock)
{
    if (flash == 0 || sector_count < 2u || flash->sector_size < SF_RECORD_MAX) {
        return SF_E_PARAM;
    }
    if (base_addr + sector_count * flash->sector_size > flash->capacity) {
        return SF_E_PARAM;
    }

    memset(q, 0, sizeof(*q));
    q->flash = flash;
    q->base_addr = base_addr;
    q->sector_count = sector_count;
    q->sector_size = flash->sector_size;
    q->next_seq = 1u;
    if (lock != 0) {
        q->lock = *lock;
    }
    sf_ackset_reset(&q->ack);

    /* Сканування: у кожному секторі кадри лежать підряд від нуля, тому
     * перший же розрив (стерта область, битий CRC, обірваний хвіст)
     * закінчує сектор. Голова — за кадром із найбільшим номером. */
    bool found = false;
    uint32_t highest_seq = 0;
    uint32_t head_sec = 0;
    uint32_t head_off = 0;

    for (uint32_t s = 0; s < sector_count; s++) {
        uint32_t off = 0;

        for (;;) {
            sf_record_t rec;
            const rec_state_t st = read_record(q, s, off, &rec);

            if (st == REC_IO) {
                return SF_E_IO;
            }
            if (st != REC_OK) {
                break;
            }

            q->stats.recovered_records++;
            if (!found || seq_after(rec.hdr.seq, highest_seq)) {
                found = true;
                highest_seq = rec.hdr.seq;
                head_sec = s;
                head_off = off + rec.stride;
            }
            off += rec.stride;
        }
    }

    if (!found) {
        /* Чистий кристал або суцільне сміття. Стираємо перший сектор —
         * і починаємо журнал з нуля. */
        if (q->flash->erase_sector(q->flash->ctx, sector_addr(q, 0)) != SF_FLASH_OK) {
            q->stats.flash_errors++;
            return SF_E_IO;
        }
        q->stats.sectors_erased++;
        return SF_OK;
    }

    q->head_sector = head_sec;
    q->head_offset = head_off;
    q->next_seq = highest_seq + 1u;

    /* Хвіст — найстарші дані, тобто перший сектор із валідним кадром,
     * якщо йти по кільцю ВІД голови вперед. */
    q->tail_sector = head_sec;
    q->tail_offset = 0;
    for (uint32_t i = 1; i < sector_count; i++) {
        const uint32_t s = (head_sec + i) % sector_count;
        sf_record_t rec;

        if (read_record(q, s, 0, &rec) == REC_OK) {
            q->tail_sector = s;
            q->tail_offset = 0;
            break;
        }
    }

    q->drain_sector = q->tail_sector;
    q->drain_offset = q->tail_offset;

    /* Квитанції живуть в ОЗП і знеструмлення не переживають. Тому все,
     * що лежить у флеші, після старту вважається недоставленим, і частина
     * кадрів поїде вдруге. Дублі відсіює сервер за номером — це чесніша
     * ціна, ніж витрачати цикли стирання на позначки «доставлено». */
    return SF_OK;
}

/* -------------------------------------------------------------------- запис */

/* Перехід на наступний сектор: за потреби витісняє хвіст і стирає
 * сектор наперед, щоб push уже мав куди писати. */
static sf_err_t roll_head(sf_queue_t *q, sf_priority_t prio)
{
    const uint32_t next = next_sector(q, q->head_sector);

    if (next == q->tail_sector) {
        if (prio == SF_PRIORITY_LOW) {
            /* Високочастотний шум не вартий того, щоб затерти історію. */
            q->stats.dropped_full++;
            return SF_E_FULL;
        }
        q->tail_sector = next_sector(q, q->tail_sector);
        q->tail_offset = 0;
        q->stats.sectors_evicted++;
        sync_drain(q);

        sf_record_t rec;
        if (read_record(q, q->tail_sector, q->tail_offset, &rec) == REC_OK) {
            sf_ackset_prune_below(&q->ack, rec.hdr.seq);
        }
    }

    if (q->flash->erase_sector(q->flash->ctx, sector_addr(q, next)) != SF_FLASH_OK) {
        q->stats.flash_errors++;
        return SF_E_IO;
    }
    q->stats.sectors_erased++;

    q->head_sector = next;
    q->head_offset = 0;
    sync_drain(q);
    return SF_OK;
}

static sf_err_t push_locked(sf_queue_t *q, uint8_t type, sf_priority_t prio, uint64_t ts_ms,
                            const void *payload, uint16_t len, uint32_t *out_seq)
{
    const uint32_t stride = sf_frame_stride(len);

    if (q->head_offset + stride > q->sector_size) {
        const sf_err_t err = roll_head(q, prio);
        if (err != SF_OK) {
            return err;
        }
    } else if (!area_is_blank(q, q->head_sector, q->head_offset, stride)) {
        /* Місце під головою не чисте: попередній запис обірвався на
         * півслові. Дописувати туди не можна — кидаємо решту сектора. */
        q->stats.corrupt_records++;
        const sf_err_t err = roll_head(q, prio);
        if (err != SF_OK) {
            return err;
        }
    }

    sf_header_t hdr;
    hdr.magic = SF_MAGIC;
    hdr.type = type;
    hdr.flags = (uint8_t)prio & SF_FLAGS_PRIORITY_MASK;
    hdr.seq = q->next_seq;
    hdr.timestamp_ms = ts_ms;
    hdr.payload_len = len;
    hdr.reserved = 0;

    sf_frame_pack(q->scratch, &hdr, payload);

    const uint32_t addr = sector_addr(q, q->head_sector) + q->head_offset;
    if (q->flash->program(q->flash->ctx, addr, q->scratch, stride) != SF_FLASH_OK) {
        /* Кадр не доїхав у кристал цілим. Голову НЕ рухаємо: наступне
         * сканування побачить у цьому місці розрив і зупиниться там,
         * а push помітить нечисту область і перескочить сектор. */
        q->stats.flash_errors++;
        return SF_E_IO;
    }

    q->head_offset += stride;
    q->next_seq++;
    q->stats.records_written++;
    q->stats.bytes_written += stride;

    if (out_seq != 0) {
        *out_seq = hdr.seq;
    }
    return SF_OK;
}

sf_err_t sf_queue_push(sf_queue_t *q, uint8_t type, sf_priority_t prio, uint64_t ts_ms,
                       const void *payload, uint16_t len, uint32_t *out_seq)
{
    if (payload == 0 || len == 0u || len > SF_MAX_PAYLOAD) {
        return SF_E_PARAM;
    }

    sf_lock_enter(&q->lock);
    const sf_err_t err = push_locked(q, type, prio, ts_ms, payload, len, out_seq);
    sf_lock_exit(&q->lock);
    return err;
}

/* ---------------------------------------------------------------- вивантаження */

static sf_err_t peek_locked(sf_queue_t *q, sf_record_t *out)
{
    for (uint32_t step = 0; step < q->sector_count + 1u; step++) {
        if (is_empty(q)) {
            return SF_E_EMPTY;
        }

        switch (read_record(q, q->tail_sector, q->tail_offset, out)) {
        case REC_OK:
            return SF_OK;
        case REC_IO:
            return SF_E_IO;
        case REC_BLANK:
            if (q->tail_sector == q->head_sector) {
                return SF_E_EMPTY;
            }
            roll_tail(q);
            break;
        case REC_CORRUPT:
        default:
            /* Битий кадр у хвості не має права заклинити чергу назавжди. */
            skip_bad_tail(q);
            break;
        }
    }
    return SF_E_EMPTY;
}

sf_err_t sf_queue_peek_tail(sf_queue_t *q, sf_record_t *out)
{
    sf_lock_enter(&q->lock);
    const sf_err_t err = peek_locked(q, out);
    sf_lock_exit(&q->lock);
    return err;
}

static bool drain_at_head(const sf_queue_t *q)
{
    return q->drain_sector == q->head_sector && q->drain_offset >= q->head_offset;
}

static void roll_drain(sf_queue_t *q)
{
    q->drain_sector = next_sector(q, q->drain_sector);
    q->drain_offset = 0;
}

static sf_err_t drain_locked(sf_queue_t *q, sf_batch_t *batch)
{
    const uint32_t guard = q->sector_count + SF_BATCH_MAX_RECORDS * 2u + 8u;

    batch->count = 0;
    batch->used = 0;
    batch->first_seq = 0;
    batch->last_seq = 0;

    sync_drain(q);

    for (uint32_t step = 0; step < guard && batch->count < SF_BATCH_MAX_RECORDS; step++) {
        sf_record_t rec;

        if (drain_at_head(q)) {
            break; /* історію вичерпано, далі тільки жива колія */
        }

        const rec_state_t st = read_record(q, q->drain_sector, q->drain_offset, &rec);

        if (st == REC_IO) {
            break;
        }
        if (st == REC_BLANK) {
            if (q->drain_sector == q->head_sector) {
                break;
            }
            roll_drain(q);
            continue;
        }
        if (st == REC_CORRUPT) {
            q->stats.corrupt_records++;
            if (q->drain_sector == q->head_sector) {
                q->drain_offset = q->head_offset;
            } else {
                roll_drain(q);
            }
            continue;
        }

        /* Ось воно, розділення колій: кадр, який щойно поїхав живцем
         * і був квитований, історія не читає вдруге. */
        if (sf_ackset_contains(&q->ack, rec.hdr.seq)) {
            q->stats.skipped_live_acked++;
            q->drain_offset += rec.stride;
            continue;
        }

        if (batch->used + rec.hdr.payload_len > SF_BATCH_ARENA) {
            break; /* радіокадр закінчився — решта поїде наступною пачкою */
        }

        sf_batch_item_t *item = &batch->item[batch->count];
        item->seq = rec.hdr.seq;
        item->timestamp_ms = rec.hdr.timestamp_ms;
        item->type = rec.hdr.type;
        item->priority = (uint8_t)sf_frame_priority(&rec.hdr);
        item->len = rec.hdr.payload_len;
        item->offset = (uint16_t)batch->used;

        memcpy(batch->arena + batch->used, rec.payload, rec.hdr.payload_len);
        batch->used += rec.hdr.payload_len;

        if (batch->count == 0u) {
            batch->first_seq = rec.hdr.seq;
        }
        batch->last_seq = rec.hdr.seq;
        batch->count++;

        q->drain_offset += rec.stride;
        if (q->drain_offset + SF_HEADER_SIZE > q->sector_size &&
            q->drain_sector != q->head_sector) {
            roll_drain(q);
        }
    }

    return (batch->count > 0u) ? SF_OK : SF_E_EMPTY;
}

sf_err_t sf_queue_drain_batch(sf_queue_t *q, sf_batch_t *batch)
{
    sf_lock_enter(&q->lock);
    const sf_err_t err = drain_locked(q, batch);
    sf_lock_exit(&q->lock);
    return err;
}

void sf_queue_drain_rewind(sf_queue_t *q)
{
    sf_lock_enter(&q->lock);
    q->drain_sector = q->tail_sector;
    q->drain_offset = q->tail_offset;
    sf_lock_exit(&q->lock);
}

void sf_queue_commit_ack(sf_queue_t *q, uint32_t acked_seq)
{
    sf_lock_enter(&q->lock);
    /* Пакетна квитанція суцільна за визначенням: сервер має все до
     * acked_seq. Нижня межа тут умовна — зайве однаково зріже prune. */
    sf_ackset_add_range(&q->ack, 1u, acked_seq);
    advance_tail(q);
    sf_lock_exit(&q->lock);
}

void sf_queue_ack_live(sf_queue_t *q, uint32_t seq)
{
    sf_lock_enter(&q->lock);
    sf_ackset_add(&q->ack, seq);
    advance_tail(q);
    sf_lock_exit(&q->lock);
}

/* ---------------------------------------------------------------- довідки */

bool sf_queue_is_empty(sf_queue_t *q)
{
    sf_lock_enter(&q->lock);
    const bool empty = is_empty(q);
    sf_lock_exit(&q->lock);
    return empty;
}

uint32_t sf_queue_bytes_pending(sf_queue_t *q)
{
    sf_lock_enter(&q->lock);
    const uint32_t used = pos_from_tail(q, q->head_sector, q->head_offset) - q->tail_offset;
    sf_lock_exit(&q->lock);
    return used;
}
