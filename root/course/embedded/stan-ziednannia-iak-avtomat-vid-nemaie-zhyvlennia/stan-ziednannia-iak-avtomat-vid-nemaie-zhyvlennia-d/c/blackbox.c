#include "blackbox.h"

#include "modem_hal.h"

#include <string.h>

#define BLACKBOX_MAGIC 0x424C4B31u /* "BLK1" */

_Static_assert(sizeof(fsm_transition_log_t) == BLACKBOX_REC_SZ,
               "запис журналу мусить лишатися 16-байтовим");

typedef struct {
    uint32_t             magic;
    uint8_t              head;  /* куди ляже наступний запис */
    uint8_t              count; /* скільки записів чинні */
    uint16_t             crc;
    fsm_transition_log_t rec[BLACKBOX_DEPTH];
} blackbox_nv_t;

static blackbox_nv_t s_nv;

static uint16_t crc16(const uint8_t *data, size_t len)
{
    uint16_t crc = 0xFFFFu;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000u) ? (uint16_t)((crc << 1) ^ 0x1021u) : (uint16_t)(crc << 1);
        }
    }
    return crc;
}

static uint16_t nv_crc(void)
{
    uint16_t crc = crc16((const uint8_t *)s_nv.rec, sizeof(s_nv.rec));
    uint8_t tail[2] = { s_nv.head, s_nv.count };
    return (uint16_t)(crc ^ crc16(tail, sizeof(tail)));
}

static void nv_reset(void)
{
    memset(&s_nv, 0, sizeof(s_nv));
    s_nv.magic = BLACKBOX_MAGIC;
}

void blackbox_init(void)
{
    if (!hal_nv_read(&s_nv, sizeof(s_nv))) {
        nv_reset();
        return;
    }
    /* Перший запуск або зіпсована комірка: краще порожній журнал, ніж сміття. */
    if (s_nv.magic != BLACKBOX_MAGIC || s_nv.head >= BLACKBOX_DEPTH ||
        s_nv.count > BLACKBOX_DEPTH || s_nv.crc != nv_crc()) {
        nv_reset();
    }
}

void blackbox_record(uint8_t from_state, uint8_t to_state, uint8_t event_id,
                     uint8_t retry_count, int8_t rssi_dbm, uint16_t cme_code,
                     uint16_t vbat_mv)
{
    fsm_transition_log_t *r = &s_nv.rec[s_nv.head];

    r->timestamp_ms = hal_now_ms();
    r->from_state = from_state;
    r->to_state = to_state;
    r->event_id = event_id;
    r->retry_count = retry_count;
    r->rssi_dbm = rssi_dbm;
    r->cme_error_code = cme_code;
    r->voltage_vbat_mv = vbat_mv;
    r->reserved[0] = 0;
    r->reserved[1] = 0;

    s_nv.head = (uint8_t)((s_nv.head + 1u) % BLACKBOX_DEPTH);
    if (s_nv.count < BLACKBOX_DEPTH) {
        s_nv.count++;
    }
    /* Кільце переповнилося — найстаріший запис затерто, і це нормально:
       цікавить остання аварія, а не вся історія приладу. */
}

void blackbox_flush(void)
{
    s_nv.crc = nv_crc();
    (void)hal_nv_write(&s_nv, sizeof(s_nv));
}

/* На дроті розкладку структури не припускаємо: пакуємо поле за полем. */
static void pack_rec(uint8_t *p, const fsm_transition_log_t *r)
{
    p[0] = (uint8_t)(r->timestamp_ms & 0xFFu);
    p[1] = (uint8_t)((r->timestamp_ms >> 8) & 0xFFu);
    p[2] = (uint8_t)((r->timestamp_ms >> 16) & 0xFFu);
    p[3] = (uint8_t)((r->timestamp_ms >> 24) & 0xFFu);
    p[4] = r->from_state;
    p[5] = r->to_state;
    p[6] = r->event_id;
    p[7] = r->retry_count;
    p[8] = (uint8_t)r->rssi_dbm;
    p[9] = (uint8_t)(r->cme_error_code & 0xFFu);
    p[10] = (uint8_t)(r->cme_error_code >> 8);
    p[11] = (uint8_t)(r->voltage_vbat_mv & 0xFFu);
    p[12] = (uint8_t)(r->voltage_vbat_mv >> 8);
    p[13] = 0;
    p[14] = 0;
    p[15] = 0;
}

static uint8_t oldest_index(void)
{
    return (uint8_t)((s_nv.head + BLACKBOX_DEPTH - s_nv.count) % BLACKBOX_DEPTH);
}

size_t blackbox_export(uint8_t *buf, size_t cap)
{
    size_t n = 0;
    uint8_t idx = oldest_index();

    for (uint8_t i = 0; i < s_nv.count; ++i) {
        if (n + BLACKBOX_REC_SZ > cap) {
            break; /* решта поїде наступним кадром */
        }
        pack_rec(buf + n, &s_nv.rec[idx]);
        n += BLACKBOX_REC_SZ;
        idx = (uint8_t)((idx + 1u) % BLACKBOX_DEPTH);
    }
    return n;
}

void blackbox_mark_sent(size_t bytes)
{
    uint8_t sent = (uint8_t)(bytes / BLACKBOX_REC_SZ);

    if (sent >= s_nv.count) {
        s_nv.count = 0;
    } else {
        s_nv.count = (uint8_t)(s_nv.count - sent);
    }
    blackbox_flush();
}

uint8_t blackbox_count(void)
{
    return s_nv.count;
}
