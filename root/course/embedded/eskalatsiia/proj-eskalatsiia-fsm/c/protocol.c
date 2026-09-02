#include "protocol.h"

#include <string.h>

/* Фіксована частина кадру запиту:
   magic(1) ver(1) flags(1) query_id(2) timestamp(4) deadline(2) trigger(1)
   position(12) velocity(12) options_count(1) = 37 байтів. */
#define ESC_QUERY_FIXED 37u
#define ESC_REPLY_LEN   11u  /* magic ver query_id(2) option(1) gcs_time(4) crc(2) */

uint16_t esc_crc16(const uint8_t* data, size_t len)
{
    /* CRC-16/CCITT-FALSE: поліном 0x1021, початкове 0xFFFF */
    uint16_t crc = 0xFFFFu;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000u) ? (uint16_t)((uint16_t)(crc << 1) ^ 0x1021u)
                                  : (uint16_t)(crc << 1);
        }
    }
    return crc;
}

/* ---- курсор запису: усі переповнення ловляться прапорцем ok ---- */

typedef struct {
    uint8_t* p;
    size_t   cap;
    size_t   n;
    bool     ok;
} EscWr;

static void w8(EscWr* w, uint8_t v)
{
    if (!w->ok) return;
    if (w->n + 1u > w->cap) { w->ok = false; return; }
    w->p[w->n++] = v;
}

static void w16(EscWr* w, uint16_t v)
{
    w8(w, (uint8_t)(v & 0xFFu));
    w8(w, (uint8_t)(v >> 8));
}

static void w32(EscWr* w, uint32_t v)
{
    w16(w, (uint16_t)(v & 0xFFFFu));
    w16(w, (uint16_t)(v >> 16));
}

static void wf32(EscWr* w, float v)
{
    uint32_t bits;
    memcpy(&bits, &v, sizeof bits);   /* IEEE-754 little-endian по дроту */
    w32(w, bits);
}

static void wbuf(EscWr* w, const uint8_t* src, size_t len)
{
    for (size_t i = 0; i < len; ++i) w8(w, src[i]);
}

/* ---- курсор читання ---- */

typedef struct {
    const uint8_t* p;
    size_t         len;
    size_t         n;
    bool           ok;
} EscRd;

static uint8_t r8(EscRd* r)
{
    if (!r->ok) return 0;
    if (r->n + 1u > r->len) { r->ok = false; return 0; }
    return r->p[r->n++];
}

static uint16_t r16(EscRd* r)
{
    uint16_t lo = r8(r);
    uint16_t hi = r8(r);
    return (uint16_t)(lo | (uint16_t)(hi << 8));
}

static uint32_t r32(EscRd* r)
{
    uint32_t lo = r16(r);
    uint32_t hi = r16(r);
    return lo | (hi << 16);
}

static float rf32(EscRd* r)
{
    uint32_t bits = r32(r);
    float v;
    memcpy(&v, &bits, sizeof v);
    return v;
}

/* Скільки байтів займе кадр запиту (з мініатюрою або без неї) */
static size_t query_size(const EscQuery* q, bool with_roi)
{
    size_t n = ESC_QUERY_FIXED;
    for (uint8_t i = 0; i < q->options_count; ++i) {
        size_t desc = strnlen(q->options[i].description, ESC_DESC_MAX);
        n += 2u + desc + 8u;   /* id, довжина підпису, підпис, дві float-оцінки */
    }
    n += 2u;                                       /* довжина ROI */
    if (with_roi) n += q->roi_size_bytes;
    n += 2u;                                       /* CRC */
    return n;
}

EscWireErr esc_pack_query(const EscQuery* q, uint8_t* out, size_t cap, size_t* written)
{
    if (!q || !out || !written) return ESC_WIRE_ERR_FIELD;
    *written = 0;

    if (q->options_count == 0u || q->options_count > ESC_MAX_OPTIONS) return ESC_WIRE_ERR_FIELD;
    if (q->roi_size_bytes > ESC_ROI_MAX) return ESC_WIRE_ERR_FIELD;

    const size_t limit = (cap < ESC_MTU_BYTES) ? cap : (size_t)ESC_MTU_BYTES;

    /* Мініатюру ріжемо цілком, а не наполовину: обрізаний JPEG декодеру нічого не дасть */
    uint8_t flags   = q->flags;
    bool    with_roi = true;
    size_t  need     = query_size(q, true);
    if (need > limit) {
        with_roi = false;
        flags   |= ESC_FLAG_ROI_DROPPED;
        need     = query_size(q, false);
    }
    if (need > limit) return ESC_WIRE_ERR_NO_ROOM;

    EscWr w = { out, limit, 0u, true };
    w8(&w, ESC_MAGIC_QUERY);
    w8(&w, ESC_WIRE_VERSION);
    w8(&w, flags);
    w16(&w, q->query_id);
    w32(&w, q->timestamp_ms);
    w16(&w, q->deadline_ms);
    w8(&w, (uint8_t)q->trigger_code);
    for (int i = 0; i < 3; ++i) wf32(&w, q->position_xyz[i]);
    for (int i = 0; i < 3; ++i) wf32(&w, q->velocity_xyz[i]);
    w8(&w, q->options_count);
    for (uint8_t i = 0; i < q->options_count; ++i) {
        const EscOption* o = &q->options[i];
        size_t desc = strnlen(o->description, ESC_DESC_MAX);
        w8(&w, o->option_id);
        w8(&w, (uint8_t)desc);
        wbuf(&w, (const uint8_t*)o->description, desc);
        wf32(&w, o->estimated_cost_detour_m);
        wf32(&w, o->risk_score);
    }
    if (with_roi) {
        w16(&w, q->roi_size_bytes);
        wbuf(&w, q->roi_jpeg, q->roi_size_bytes);
    } else {
        w16(&w, 0u);
    }
    if (!w.ok) return ESC_WIRE_ERR_NO_ROOM;

    w16(&w, esc_crc16(out, w.n));
    if (!w.ok) return ESC_WIRE_ERR_NO_ROOM;

    *written = w.n;
    return ESC_WIRE_OK;
}

EscWireErr esc_unpack_query(const uint8_t* in, size_t len, EscQuery* out)
{
    if (!in || !out) return ESC_WIRE_ERR_FIELD;
    if (len < ESC_QUERY_FIXED + 4u) return ESC_WIRE_ERR_SHORT;
    if (in[0] != ESC_MAGIC_QUERY) return ESC_WIRE_ERR_MAGIC;
    if (in[1] != ESC_WIRE_VERSION) return ESC_WIRE_ERR_VERSION;

    uint16_t got = (uint16_t)(in[len - 2] | ((uint16_t)in[len - 1] << 8));
    if (got != esc_crc16(in, len - 2u)) return ESC_WIRE_ERR_CRC;

    memset(out, 0, sizeof *out);
    EscRd r = { in, len - 2u, 0u, true };
    (void)r8(&r);                       /* magic */
    (void)r8(&r);                       /* version */
    out->flags        = r8(&r);
    out->query_id     = r16(&r);
    out->timestamp_ms = r32(&r);
    out->deadline_ms  = r16(&r);
    out->trigger_code = (EscTrigger)r8(&r);
    for (int i = 0; i < 3; ++i) out->position_xyz[i] = rf32(&r);
    for (int i = 0; i < 3; ++i) out->velocity_xyz[i] = rf32(&r);
    out->options_count = r8(&r);
    if (!r.ok) return ESC_WIRE_ERR_SHORT;
    if (out->options_count == 0u || out->options_count > ESC_MAX_OPTIONS) return ESC_WIRE_ERR_FIELD;

    for (uint8_t i = 0; i < out->options_count; ++i) {
        EscOption* o = &out->options[i];
        o->option_id  = r8(&r);
        uint8_t desc  = r8(&r);
        if (desc > ESC_DESC_MAX) return ESC_WIRE_ERR_FIELD;
        for (uint8_t k = 0; k < desc; ++k) o->description[k] = (char)r8(&r);
        o->description[desc]  = '\0';
        o->estimated_cost_detour_m      = rf32(&r);
        o->risk_score         = rf32(&r);
    }
    out->roi_size_bytes = r16(&r);
    if (!r.ok) return ESC_WIRE_ERR_SHORT;
    if (out->roi_size_bytes > ESC_ROI_MAX) return ESC_WIRE_ERR_FIELD;
    for (uint16_t i = 0; i < out->roi_size_bytes; ++i) out->roi_jpeg[i] = r8(&r);

    return r.ok ? ESC_WIRE_OK : ESC_WIRE_ERR_SHORT;
}

EscWireErr esc_pack_reply(const EscReply* rep, uint8_t* out, size_t cap, size_t* written)
{
    if (!rep || !out || !written) return ESC_WIRE_ERR_FIELD;
    *written = 0;
    if (cap < ESC_REPLY_LEN) return ESC_WIRE_ERR_NO_ROOM;

    EscWr w = { out, cap, 0u, true };
    w8(&w, ESC_MAGIC_REPLY);
    w8(&w, ESC_WIRE_VERSION);
    w16(&w, rep->query_id);
    w8(&w, rep->option_id);
    w32(&w, rep->gcs_time_ms);
    w16(&w, esc_crc16(out, w.n));
    if (!w.ok) return ESC_WIRE_ERR_NO_ROOM;

    *written = w.n;
    return ESC_WIRE_OK;
}

EscWireErr esc_unpack_reply(const uint8_t* in, size_t len, EscReply* out)
{
    if (!in || !out) return ESC_WIRE_ERR_FIELD;
    if (len != ESC_REPLY_LEN) return ESC_WIRE_ERR_SHORT;
    if (in[0] != ESC_MAGIC_REPLY) return ESC_WIRE_ERR_MAGIC;
    if (in[1] != ESC_WIRE_VERSION) return ESC_WIRE_ERR_VERSION;

    uint16_t got = (uint16_t)(in[len - 2] | ((uint16_t)in[len - 1] << 8));
    if (got != esc_crc16(in, len - 2u)) return ESC_WIRE_ERR_CRC;

    EscRd r = { in, len - 2u, 2u, true };  /* magic і версію вже перевірено */
    out->query_id    = r16(&r);
    out->option_id   = r8(&r);
    out->gcs_time_ms = r32(&r);
    return r.ok ? ESC_WIRE_OK : ESC_WIRE_ERR_SHORT;
}

const char* esc_wire_err_str(EscWireErr e)
{
    switch (e) {
        case ESC_WIRE_OK:           return "ok";
        case ESC_WIRE_ERR_SHORT:    return "кадр обірвано";
        case ESC_WIRE_ERR_MAGIC:    return "чужий кадр";
        case ESC_WIRE_ERR_VERSION:  return "інша версія протоколу";
        case ESC_WIRE_ERR_CRC:      return "CRC не збігся";
        case ESC_WIRE_ERR_FIELD:    return "поле поза діапазоном";
        case ESC_WIRE_ERR_NO_ROOM:  return "не влазить у MTU";
    }
    return "?";
}
