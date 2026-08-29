#include "flash_logger.h"

#include <string.h>

#define NO_SECTOR 0xFFFFFFFFu

/* ---------- обгортки над HAL ---------- */

static uint32_t sector_addr(const flash_logger_t *l, uint32_t idx)
{
    return l->base_addr + idx * FLASH_SECTOR_SIZE;
}

static bool hal_read(flash_logger_t *l, uint32_t addr, uint8_t *buf, size_t len)
{
    return l->hal.read(addr, buf, len, l->hal.ctx);
}

static bool hal_write(flash_logger_t *l, uint32_t addr, const uint8_t *buf, size_t len)
{
    return l->hal.write(addr, buf, len, l->hal.ctx);
}

static bool hal_erase(flash_logger_t *l, uint32_t idx)
{
    return l->hal.erase_sector(sector_addr(l, idx), l->hal.ctx);
}

static bool is_bad(const flash_logger_t *l, uint32_t idx)
{
    return ((l->bad_mask >> idx) & 1u) != 0u;
}

/* Читання назад і побайтове звіряння. SPI-лінія мовчки б'є біти частіше,
 * ніж хочеться вірити, а «записалося» від HAL означає лише «команду відіслано». */
static bool verify_bytes(flash_logger_t *l, uint32_t addr, const uint8_t *expect, size_t len)
{
    uint8_t chunk[64];
    size_t done = 0;

    while (done < len) {
        size_t n = len - done;
        if (n > sizeof(chunk)) {
            n = sizeof(chunk);
        }
        if (!hal_read(l, addr + done, chunk, n)) {
            return false;
        }
        if (memcmp(chunk, expect + done, n) != 0) {
            return false;
        }
        done += n;
    }
    return true;
}

static bool read_sector_header(flash_logger_t *l, uint32_t idx, sector_header_t *hdr)
{
    uint8_t raw[SECTOR_HEADER_SIZE];
    if (!hal_read(l, sector_addr(l, idx), raw, sizeof(raw))) {
        return false;
    }
    log_decode_sector_header(raw, hdr);
    return true;
}

/* Перехід стану гасить біти на місці — стирати сектор для цього не треба. */
static bool write_sector_state(flash_logger_t *l, uint32_t idx, uint32_t state)
{
    uint8_t raw[4];
    log_put_u32(raw, state);

    const uint32_t addr = sector_addr(l, idx) + SECTOR_STATE_OFFSET;
    if (!hal_write(l, addr, raw, sizeof(raw))) {
        return false;
    }
    return verify_bytes(l, addr, raw, sizeof(raw));
}

/* ---------- дефектні сектори ---------- */

static void mark_bad(flash_logger_t *l, uint32_t idx)
{
    l->bad_mask |= 1u << idx;
    l->pending_bad = idx;

    /* Спроба лишити слід у самому секторі. Вона цілком може не вдатися — саме
     * тому маска дефектів живе в RAM: сектор, який не тримає даних, не втримає
     * і мітку про власну несправність. Після перезавантаження логер натрапить
     * на нього знову, знову не зможе стерти й знову обійде — детерміновано,
     * ціною одного зайвого стирання на завантаження. */
    (void)write_sector_state(l, idx, SECTOR_STATE_DIRTY);
}

static uint32_t next_live_sector(const flash_logger_t *l, uint32_t from)
{
    for (uint32_t i = 1; i <= FLASH_SECTOR_COUNT; ++i) {
        const uint32_t idx = (from + i) % FLASH_SECTOR_COUNT;
        if (!is_bad(l, idx)) {
            return idx;
        }
    }
    return from;
}

/* ---------- відкриття сектора й ротація ---------- */

static bool open_sector(flash_logger_t *l, uint32_t idx, uint32_t erase_count, uint32_t seq)
{
    if (!hal_erase(l, idx)) {
        return false;
    }

    sector_header_t hdr;
    hdr.magic       = LOG_SECTOR_MAGIC;
    hdr.version     = LOG_FORMAT_VERSION;
    hdr.seq_num     = seq;
    hdr.erase_count = erase_count;
    hdr.state       = SECTOR_STATE_ACTIVE;

    uint8_t raw[SECTOR_HEADER_SIZE];
    log_encode_sector_header(&hdr, raw);

    if (!hal_write(l, sector_addr(l, idx), raw, sizeof(raw))) {
        return false;
    }
    return verify_bytes(l, sector_addr(l, idx), raw, sizeof(raw));
}

/* Закриває поточний сектор і відкриває наступний живий за кільцем.
 * Порядок саме такий: спершу FULL на старому, потім стирання нового.
 * Знеструмлення посередині лишає щонайбільше один ACTIVE, а не два. */
static log_status_t rotate_sector(flash_logger_t *l)
{
    if (!is_bad(l, l->active_sector)) {
        (void)write_sector_state(l, l->active_sector, SECTOR_STATE_FULL);
    }

    uint32_t idx = l->active_sector;

    for (uint32_t attempt = 0; attempt < FLASH_SECTOR_COUNT; ++attempt) {
        idx = (idx + 1) % FLASH_SECTOR_COUNT;
        if (is_bad(l, idx)) {
            continue;
        }

        uint32_t erase_count = 0;
        sector_header_t old;
        if (read_sector_header(l, idx, &old) && old.magic == LOG_SECTOR_MAGIC) {
            erase_count = old.erase_count;
        }

        if (!open_sector(l, idx, erase_count + 1, l->seq_num + 1)) {
            mark_bad(l, idx);
            continue;
        }

        l->seq_num += 1;
        l->active_sector = idx;
        l->write_offset = SECTOR_HEADER_SIZE;

        /* Голова наздогнала хвіст: щойно стертий сектор і був найстарішим
         * невивантаженим. Хвіст виштовхуємо вперед — свіжі дані важливіші
         * за старі, і система не спиняється. */
        if (l->tail_sector == idx) {
            l->tail_sector = next_live_sector(l, idx);
        }
        return LOG_OK;
    }

    return LOG_ERR_HAL; /* усе кільце дефектне — писати нікуди */
}

/* ---------- сканування записів ---------- */

/* Лінійний прохід сектором до першого кадру, який не сходиться. Повертає зсув
 * цього кадру: саме туди стане покажчик запису після відновлення. */
static uint32_t scan_records(flash_logger_t *l, uint32_t idx, uint32_t *out_count)
{
    uint32_t offset = SECTOR_HEADER_SIZE;
    uint32_t count = 0;
    const uint32_t base = sector_addr(l, idx);
    uint8_t raw[RECORD_MAX_SIZE];

    while (offset + RECORD_HEADER_SIZE + RECORD_CRC_SIZE <= FLASH_SECTOR_SIZE) {
        uint8_t head[RECORD_HEADER_SIZE];
        if (!hal_read(l, base + offset, head, sizeof(head))) {
            break;
        }
        if (log_get_u16(head) != LOG_RECORD_MAGIC) {
            break; /* чисті 0xFF або сміття — далі даних немає */
        }

        const uint8_t total = head[2];
        if (total < RECORD_HEADER_SIZE + RECORD_CRC_SIZE) {
            break;
        }
        if (offset + total > FLASH_SECTOR_SIZE) {
            break; /* довжина обіцяє більше, ніж лишилося сектора */
        }
        if (!hal_read(l, base + offset, raw, total)) {
            break;
        }

        record_header_t hdr;
        if (!log_decode_record(raw, total, &hdr, NULL, NULL)) {
            break; /* CRC не зійшлася: недописаний кадр, тут і кінець даних */
        }

        offset += total;
        count += 1;
    }

    if (out_count != NULL) {
        *out_count = count;
    }
    return offset;
}

/* ---------- ініціалізація ---------- */

log_status_t flash_logger_init(flash_logger_t *logger, const flash_hal_t *hal, uint32_t base_addr)
{
    memset(logger, 0, sizeof(*logger));
    logger->hal = *hal;
    logger->base_addr = base_addr;
    logger->pending_bad = NO_SECTOR;

    uint32_t active = NO_SECTOR;
    uint32_t active_seq = 0;
    uint32_t newest = NO_SECTOR;
    uint32_t newest_seq = 0;
    uint32_t tail = NO_SECTOR;
    uint32_t tail_seq = 0xFFFFFFFFu;

    for (uint32_t i = 0; i < FLASH_SECTOR_COUNT; ++i) {
        sector_header_t hdr;
        if (!read_sector_header(logger, i, &hdr)) {
            return LOG_ERR_HAL;
        }
        if (hdr.magic != LOG_SECTOR_MAGIC || hdr.version != LOG_FORMAT_VERSION) {
            continue; /* сектор ще не наш: чистий, чужий або побитий заголовок */
        }

        if (hdr.state != SECTOR_STATE_ERASED &&
            (newest == NO_SECTOR || hdr.seq_num > newest_seq)) {
            newest = i;
            newest_seq = hdr.seq_num;
        }

        if (hdr.state == SECTOR_STATE_ACTIVE) {
            /* Двох активних бути не мало б, але якщо кристал прокинувся
             * з половинним записом стану — беремо новіший, старіший закриваємо. */
            if (active == NO_SECTOR || hdr.seq_num > active_seq) {
                if (active != NO_SECTOR) {
                    (void)write_sector_state(logger, active, SECTOR_STATE_FULL);
                }
                active = i;
                active_seq = hdr.seq_num;
            } else {
                (void)write_sector_state(logger, i, SECTOR_STATE_FULL);
            }
        }

        if ((hdr.state == SECTOR_STATE_ACTIVE || hdr.state == SECTOR_STATE_FULL) &&
            hdr.seq_num < tail_seq) {
            tail_seq = hdr.seq_num;
            tail = i;
        }
    }

    if (active != NO_SECTOR) {
        logger->active_sector = active;
        logger->seq_num = newest_seq;
        logger->write_offset = scan_records(logger, active, NULL);
    } else {
        /* Активного немає: або кристал чистий, або живлення зникло між
         * закриттям старого сектора й відкриттям нового. Відкриваємо той,
         * що йде за найновішим, — так порядок номерів лишається зростаючим. */
        const uint32_t start = (newest == NO_SECTOR) ? 0u : (newest + 1u) % FLASH_SECTOR_COUNT;
        logger->seq_num = newest_seq;

        bool opened = false;
        for (uint32_t i = 0; i < FLASH_SECTOR_COUNT && !opened; ++i) {
            const uint32_t idx = (start + i) % FLASH_SECTOR_COUNT;

            uint32_t erase_count = 0;
            sector_header_t hdr;
            if (read_sector_header(logger, idx, &hdr) && hdr.magic == LOG_SECTOR_MAGIC) {
                erase_count = hdr.erase_count;
            }

            if (open_sector(logger, idx, erase_count + 1, logger->seq_num + 1)) {
                logger->seq_num += 1;
                logger->active_sector = idx;
                logger->write_offset = SECTOR_HEADER_SIZE;
                opened = true;
            } else {
                mark_bad(logger, idx);
            }
        }
        if (!opened) {
            return LOG_ERR_HAL;
        }

        /* Стерли те, що було хвостом, — хвіст їде далі. */
        if (tail == logger->active_sector) {
            tail = next_live_sector(logger, logger->active_sector);
        }
    }

    logger->tail_sector = (tail == NO_SECTOR) ? logger->active_sector : tail;
    return LOG_OK;
}

/* ---------- запис ---------- */

/* Про дефектний сектор треба сказати в самому журналі — інакше на сервері
 * розрив нумерації виглядатиме як загублений зв'язок. Запис іде вже в новий,
 * робочий сектор; прапорець ловить рекурсію, якщо і він виявиться битим. */
static void report_bad_sector(flash_logger_t *l)
{
    if (l->pending_bad == NO_SECTOR || l->in_service_write) {
        return;
    }

    uint8_t payload[4];
    log_put_u32(payload, l->pending_bad);

    l->pending_bad = NO_SECTOR;
    l->in_service_write = true;
    (void)flash_logger_write(l, LOG_LEVEL_ERROR, LOG_MODULE_LOGGER,
                             l->last_timestamp_ms, LOG_TOKEN_BAD_SECTOR,
                             payload, sizeof(payload));
    l->in_service_write = false;
}

log_status_t flash_logger_write(flash_logger_t *logger, log_level_t level, uint8_t module_id,
                                uint32_t timestamp_ms, uint32_t token_id,
                                const uint8_t *payload, uint8_t payload_len)
{
    uint8_t frame[RECORD_MAX_SIZE];
    record_header_t hdr;
    hdr.length       = 0; /* заповнить кодувальник */
    hdr.level        = (uint8_t)level;
    hdr.module_id    = module_id;
    hdr.timestamp_ms = timestamp_ms;
    hdr.token_id     = token_id;

    const size_t total = log_encode_record(&hdr, payload, payload_len, frame, sizeof(frame));
    if (total == 0) {
        return LOG_ERR_TOO_BIG;
    }

    if (!logger->in_service_write) {
        logger->last_timestamp_ms = timestamp_ms;
    }

    for (uint32_t attempt = 0; attempt < FLASH_SECTOR_COUNT; ++attempt) {
        if (logger->write_offset + total > FLASH_SECTOR_SIZE) {
            const log_status_t st = rotate_sector(logger);
            if (st != LOG_OK) {
                return st;
            }
        }

        const uint32_t addr = sector_addr(logger, logger->active_sector) + logger->write_offset;

        if (!hal_write(logger, addr, frame, total)) {
            /* Кристал відмовив на записі — сектор дефектний. */
            mark_bad(logger, logger->active_sector);
            logger->write_offset = FLASH_SECTOR_SIZE; /* змусити ротацію на наступному колі */
            continue;
        }

        if (!verify_bytes(logger, addr, frame, total)) {
            /* Прочиталося не те, що писали. Найчастіша причина — під нами
             * лежать байти кадру, обірваного знеструмленням: NOR уміє лише
             * гасити біти, тож поверх сміття валідного кадру не покласти.
             * Сектор закриваємо як FULL і йдемо в наступний. Дефектним його
             * не звемо: кристал команду виконав, винні старі байти. */
            (void)write_sector_state(logger, logger->active_sector, SECTOR_STATE_FULL);
            logger->write_offset = FLASH_SECTOR_SIZE;
            continue;
        }

        logger->write_offset += (uint32_t)total;
        report_bad_sector(logger);
        return LOG_OK;
    }

    return LOG_ERR_HAL;
}

uint32_t flash_logger_free_space(const flash_logger_t *logger)
{
    if (logger->write_offset >= FLASH_SECTOR_SIZE) {
        return 0;
    }
    return FLASH_SECTOR_SIZE - logger->write_offset;
}

/* ---------- вивантаження ---------- */

log_status_t flash_logger_read_batch(flash_logger_t *logger, uint8_t *out, size_t out_cap,
                                     uint32_t *out_sector, size_t *out_len, uint32_t *out_records)
{
    for (uint32_t i = 0; i < FLASH_SECTOR_COUNT; ++i) {
        const uint32_t idx = (logger->tail_sector + i) % FLASH_SECTOR_COUNT;
        if (is_bad(logger, idx)) {
            continue;
        }

        sector_header_t hdr;
        if (!read_sector_header(logger, idx, &hdr)) {
            return LOG_ERR_HAL;
        }
        if (hdr.magic != LOG_SECTOR_MAGIC || hdr.state != SECTOR_STATE_FULL) {
            continue; /* чистий, вже вивантажений або ще активний */
        }

        const uint32_t end = scan_records(logger, idx, out_records);
        const size_t len = end - SECTOR_HEADER_SIZE;
        if (len > out_cap) {
            return LOG_ERR_TOO_BIG;
        }

        /* Віддаємо сирі кадри як вони лежать: розбирає їх сервер, у якого є
         * таблиця токенів. Модем передає рівно ці байти, без переупакування. */
        if (!hal_read(logger, sector_addr(logger, idx) + SECTOR_HEADER_SIZE, out, len)) {
            return LOG_ERR_HAL;
        }

        logger->tail_sector = idx;
        if (out_sector != NULL) {
            *out_sector = idx;
        }
        if (out_len != NULL) {
            *out_len = len;
        }
        return LOG_OK;
    }

    return LOG_ERR_EMPTY;
}

log_status_t flash_logger_commit_tail(flash_logger_t *logger, uint32_t sector_idx)
{
    if (sector_idx >= FLASH_SECTOR_COUNT) {
        return LOG_ERR_RANGE;
    }
    if (sector_idx == logger->active_sector) {
        return LOG_OK; /* активний ще росте, ховати його зарано */
    }

    if (!write_sector_state(logger, sector_idx, SECTOR_STATE_DIRTY)) {
        mark_bad(logger, sector_idx);
        return LOG_ERR_HAL;
    }

    if (sector_idx == logger->tail_sector) {
        logger->tail_sector = next_live_sector(logger, sector_idx);
    }
    return LOG_OK;
}
