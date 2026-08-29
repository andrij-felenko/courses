#include <string.h>

#include "node.h"
#include "devices.h"
#include "flashlog.h"

#define RECORD_SIZE   ((uint16_t)sizeof(telemetry_record_t))
#define PAGES_PER_SECTOR (FLASH_SECTOR_SIZE / FLASH_PAGE_SIZE)
#define ERASE_LIMIT_MS   500u    /* паспортний максимум 400 мс плюс запас */
#define PROGRAM_LIMIT_MS 10u     /* паспортний максимум 3 мс             */

static uint32_t next_sector(uint32_t addr)
{
    uint32_t sector = (addr / FLASH_SECTOR_SIZE + 1u) % FLASH_SECTOR_COUNT;
    return sector * FLASH_SECTOR_SIZE;
}

static bool slot_is_erased(const uint8_t *raw)
{
    for (uint16_t i = 0; i < RECORD_SIZE; i++) {
        if (raw[i] != 0xFFu) return false;
    }
    return true;
}

static bool record_is_valid(const telemetry_record_t *rec)
{
    return crc16_modbus((const uint8_t *)rec, (uint16_t)(RECORD_SIZE - 2u)) == rec->crc16;
}

/* Дешева перевірка «сектор чистий»: перший слот увесь у одиницях. Повного
 * доказу вона не дає, але логер пише сектор строго з початку — якщо перший
 * слот незайманий, незайманий і весь сектор. */
static bool sector_is_erased(uint32_t sector_addr)
{
    uint8_t raw[RECORD_SIZE];

    if (!flash_read(sector_addr, raw, RECORD_SIZE)) return false;
    return slot_is_erased(raw);
}

static void start_erase(flash_log_t *log, uint32_t sector_addr)
{
    if (flash_sector_erase_start(sector_addr)) {
        log->state = LOG_ERASING;
        log->op_started_ms = millis();
        log->sectors_erased++;
    } else {
        log->write_errors++;
        log->last_write_ok = false;
    }
}

/* ── Монтування: пошук голови кільця ─────────────────────────────────────── */

bool flashlog_mount(flash_log_t *log, telemetry_record_t *newest)
{
    memset(log, 0, sizeof(*log));
    memset(log->page_buf, 0xFF, sizeof(log->page_buf));
    log->last_write_ok = true;

    if (!flash_present()) {
        return false;
    }

    /* Крок 1. Заголовок кожного сектора — перший запис у ньому. Найновіший
     * сектор той, чий заголовок має найбільшу мітку часу; кільце пише
     * послідовно, тому за ним іде або чистий сектор, або найстаріші дані. */
    uint32_t best_sector = 0;
    uint32_t best_time = 0;
    bool     any_valid = false;

    for (uint32_t s = 0; s < FLASH_SECTOR_COUNT; s++) {
        if ((s & 0xFFu) == 0u) {
            watchdog_kick();          /* скан 16 МБ триває довше двох секунд */
        }

        telemetry_record_t head;
        if (!flash_read(s * FLASH_SECTOR_SIZE, (uint8_t *)&head, RECORD_SIZE)) {
            return false;
        }
        if (slot_is_erased((const uint8_t *)&head) || !record_is_valid(&head)) {
            continue;
        }
        if (!any_valid || head.timestamp >= best_time) {
            best_time = head.timestamp;
            best_sector = s;
            any_valid = true;
        }
    }

    if (!any_valid) {
        /* Чистий чип або чип із самим сміттям: починаємо з нуля. */
        log->write_addr = 0;
        if (!sector_is_erased(0)) {
            start_erase(log, 0);
        }
        log->mounted = true;
        return true;
    }

    /* Крок 2. Усередині знайденого сектора шукаємо першу вільну сторінку
     * і заразом останній справжній запис — з нього продовжимо нумерацію. */
    uint32_t sector_addr = best_sector * FLASH_SECTOR_SIZE;
    uint32_t free_page = PAGES_PER_SECTOR;   /* «вільної немає» */

    for (uint32_t p = 0; p < PAGES_PER_SECTOR; p++) {
        uint32_t page_addr = sector_addr + p * FLASH_PAGE_SIZE;
        uint8_t  page[FLASH_PAGE_SIZE];

        if (!flash_read(page_addr, page, FLASH_PAGE_SIZE)) return false;

        if (slot_is_erased(page)) {
            free_page = p;
            break;
        }
        for (uint32_t r = 0; r < RECORDS_PER_PAGE; r++) {
            const telemetry_record_t *rec =
                (const telemetry_record_t *)&page[r * RECORD_SIZE];

            if (slot_is_erased((const uint8_t *)rec)) break;
            if (!record_is_valid(rec)) continue;

            log->records_total++;
            if (newest != NULL) {
                *newest = *rec;
            }
        }
    }

    if (free_page < PAGES_PER_SECTOR) {
        log->write_addr = sector_addr + free_page * FLASH_PAGE_SIZE;
    } else {
        /* Сектор дописаний до кінця — переходимо на наступний по кільцю. */
        log->write_addr = next_sector(sector_addr);
        if (!sector_is_erased(log->write_addr)) {
            start_erase(log, log->write_addr);
        }
    }

    /* Крок 3. Сектор попереду має бути чистим ще до того, як туди дійде
     * запис: інакше перша ж сторінка нового сектора чекатиме стирання. */
    if (log->state == LOG_IDLE) {
        uint32_t ahead = next_sector(log->write_addr);
        if (!sector_is_erased(ahead)) {
            start_erase(log, ahead);
        }
    }

    log->mounted = true;
    return true;
}

/* ── Накопичення й скидання сторінок ─────────────────────────────────────── */

bool flashlog_append(flash_log_t *log, const telemetry_record_t *rec)
{
    if (!log->mounted) return false;

    if (log->page_pending) {
        /* Дамо автомату шанс дожати попередню сторінку просто зараз. */
        flashlog_poll(log);
        if (log->page_pending) {
            log->write_errors++;
            log->last_write_ok = false;
            return false;
        }
    }

    memcpy(&log->page_buf[log->page_used], rec, RECORD_SIZE);
    log->page_used += RECORD_SIZE;
    log->page_records++;
    log->records_total++;

    if (log->page_records >= RECORDS_PER_PAGE) {
        /* Хвіст сторінки лишається 0xFF: він і є ознакою «далі порожньо». */
        log->page_pending = true;
    }
    return true;
}

void flashlog_poll(flash_log_t *log)
{
    if (!log->mounted) return;

    if (log->state != LOG_IDLE) {
        if (flash_busy()) {
            uint32_t limit = (log->state == LOG_ERASING) ? ERASE_LIMIT_MS : PROGRAM_LIMIT_MS;

            if ((millis() - log->op_started_ms) > limit) {
                /* Чип не звільнився за паспортний час — це вже не затримка,
                 * а несправність. Далі не пишемо, сторожовий таймер вирішить. */
                log->write_errors++;
                log->last_write_ok = false;
                log->state = LOG_IDLE;
            }
            return;
        }

        bool ok = flash_last_op_ok();
        log_state_t finished = log->state;

        log->state = LOG_IDLE;
        if (!ok) {
            log->write_errors++;
        }
        log->last_write_ok = ok;

        if (finished == LOG_PROGRAMMING) {
            uint32_t prev = log->write_addr;

            log->write_addr += FLASH_PAGE_SIZE;
            if (log->write_addr >= FLASH_TOTAL_SIZE) {
                log->write_addr = 0;                 /* кільце замкнулося */
            }

            /* Перейшли на перший запис нового сектора — час стерти той, що
             * за ним. Попереду ще шістнадцять сторінок, тобто близько трьох
             * хвилин: жоден запис на стирання не чекатиме. */
            if ((prev / FLASH_SECTOR_SIZE) != (log->write_addr / FLASH_SECTOR_SIZE)) {
                start_erase(log, next_sector(log->write_addr));
                events_push(NODE_EVENT_FLASH_IDLE);
                return;
            }
        }
        events_push(NODE_EVENT_FLASH_IDLE);
    }

    if (log->state == LOG_IDLE && log->page_pending) {
        if (flash_page_program_start(log->write_addr, log->page_buf, FLASH_PAGE_SIZE)) {
            log->state = LOG_PROGRAMMING;
            log->op_started_ms = millis();
            log->page_pending = false;
            log->page_used = 0;
            log->page_records = 0;
            memset(log->page_buf, 0xFF, sizeof(log->page_buf));
        } else if (!flash_busy()) {
            log->write_errors++;
            log->last_write_ok = false;
            log->page_pending = false;      /* сторінку втрачено, буфер звільняємо */
            log->page_used = 0;
            log->page_records = 0;
            memset(log->page_buf, 0xFF, sizeof(log->page_buf));
        }
    }
}

bool flashlog_idle(const flash_log_t *log)
{
    return log->state == LOG_IDLE && !log->page_pending;
}
