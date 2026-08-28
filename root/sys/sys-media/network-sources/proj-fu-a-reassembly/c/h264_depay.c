/* h264_depay.c — збирання access unit H.264 з RTP-пакетів (RFC 6184).
 *
 * Вхід : RTP-пакети, УЖЕ впорядковані за номерами (це робота буфера джитера).
 * Вихід: byte-stream — NAL-одиниці зі стартовими кодами 00 00 00 01;
 *        один виклик cb() на один access unit.
 *
 * Той самий файл: rtp_view / rtp_parse() і seq_ahead() / ts_ahead() вище.
 */
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

typedef struct {
    const uint8_t *data;
    size_t         len;
    uint32_t       rtp_ts;    /* мітка часу RTP у тиках clock-rate */
    bool           keyframe;  /* усередині є IDR-зріз (тип 5) */
    bool           damaged;   /* під час збирання була дірка в номерах */
} h264_au;

typedef void (*h264_au_cb)(const h264_au *au, void *user);

typedef struct {
    uint8_t   *buf;           /* накопичувач одного кадру — дає користувач */
    size_t     cap, len;
    h264_au_cb cb;
    void      *user;
    uint8_t    want_pt;

    /* стан потоку */
    bool       have_seq;
    uint16_t   last_seq;
    uint32_t   ssrc;
    unsigned   rejects;       /* скільки «старих» пакетів відкинуто поспіль */

    /* нижній поверх: фрагмент FU-A */
    bool       in_fu;
    size_t     nal_start;     /* зсув, з якого почалася поточна NAL-одиниця */

    /* верхній поверх: access unit */
    bool       have_au, pic_started, keyframe, damaged;
    uint32_t   au_ts;
} h264_depay;

void h264_depay_init(h264_depay *s, uint8_t *buf, size_t cap,
                     uint8_t payload_type, h264_au_cb cb, void *user)
{
    memset(s, 0, sizeof(*s));
    s->buf = buf; s->cap = cap;
    s->want_pt = payload_type; s->cb = cb; s->user = user;
}

/* ── накопичувач кадру ──────────────────────────────────────────────────── */

static bool au_put(h264_depay *s, const uint8_t *p, size_t n)
{
    if (s->len + n > s->cap) return false;
    memcpy(s->buf + s->len, p, n);
    s->len += n;
    return true;
}

/* Викинути недозібрану одиницю: відкотити довжину на її початок.
   Усе, що зібралося в кадрі ДО неї, лишається цілим. */
static void nal_abort(h264_depay *s)
{
    if (s->in_fu) { s->len = s->nal_start; s->in_fu = false; s->damaged = true; }
}

static void au_reset(h264_depay *s)
{
    s->len = 0;
    s->in_fu = s->have_au = s->pic_started = s->keyframe = s->damaged = false;
}

static void au_emit(h264_depay *s)
{
    nal_abort(s);                       /* хвіст без кінця декодерові не потрібен */
    if (s->have_au && s->len > 0) {
        h264_au au = { s->buf, s->len, s->au_ts, s->keyframe, s->damaged };
        s->cb(&au, s->user);
    }
    au_reset(s);
}

/* Почати нову NAL-одиницю. body — байти ПІСЛЯ заголовка; перший із них
   потрібен, щоб побачити межу картинки. */
static bool nal_open(h264_depay *s, uint8_t hdr,
                     const uint8_t *body, size_t body_n, uint32_t ts)
{
    static const uint8_t start_code[4] = { 0, 0, 0, 1 };
    unsigned type = hdr & 0x1F;

    /* Службові одиниці 6–9 і зріз, що починається з макроблока 0, належать
       НАСТУПНІЙ картинці — отже, закривають поточну. */
    if (s->pic_started &&
        ((type >= 6 && type <= 9) ||
         ((type == 1 || type == 2 || type == 5) && body_n >= 1 && (body[0] & 0x80))))
        au_emit(s);

    if (!s->have_au) { s->have_au = true; s->au_ts = ts; }

    s->nal_start = s->len;
    if (!au_put(s, start_code, 4) || !au_put(s, &hdr, 1) ||
        !au_put(s, body, body_n)) {
        s->len = s->nal_start;          /* не влізло — цієї одиниці не буде */
        s->damaged = true;
        return false;
    }
    if (type == 1 || type == 2 || type == 5) s->pic_started = true;
    if (type == 5) s->keyframe = true;
    return true;
}

/* ── головний вхід: один RTP-пакет ──────────────────────────────────────── */

void h264_depay_packet(h264_depay *s, const uint8_t *pkt, size_t len)
{
    rtp_view r;
    if (!rtp_parse(pkt, len, &r) || r.pt != s->want_pt)
        return;                          /* не наш формат — мовчки повз */

    if (s->have_seq && r.ssrc != s->ssrc) {   /* у порт полізло друге джерело */
        au_reset(s);
        s->have_seq = false;
    }
    s->ssrc = r.ssrc;

    int step = s->have_seq ? seq_ahead(r.seq, s->last_seq) : 1;

    if (step <= 0) {
        /* Дублікат або пакет, що приплентався після свого кадру. Але й
           стрибок більш ніж на 32768 уперед читається як мінус, тому
           лічимо відкинуті поспіль: кілька підряд — джерело перезапустилося
           і треба взяти новий відлік (RFC 3550, A.1). */
        if (++s->rejects < 8) return;
        au_reset(s);
        step = 1;
    }
    s->rejects  = 0;
    s->last_seq = r.seq;
    s->have_seq = true;

    if (step != 1) {                     /* дірка: тих пакетів уже не буде ніколи */
        nal_abort(s);
        s->damaged = true;
    }

    if (s->have_au) {
        int dt = ts_ahead(r.ts, s->au_ts);
        if (dt < 0) return;              /* пакет старішого кадру — той уже поїхав */
        if (dt > 0) au_emit(s);          /* інша мітка — це вже інший кадр */
    }

    const uint8_t *p = r.pl;
    size_t         n = r.pl_len;
    unsigned    type = p[0] & 0x1F;

    if (type >= 1 && type <= 23) {                  /* одна ціла NAL-одиниця */
        s->in_fu = false;
        nal_open(s, p[0], p + 1, n - 1, r.ts);

    } else if (type == 24) {                        /* STAP-A: кілька дрібних */
        s->in_fu = false;
        for (size_t i = 1; i + 2 <= n; ) {
            size_t sz = ((size_t)p[i] << 8) | p[i + 1];
            i += 2;
            if (sz == 0 || i + sz > n) { s->damaged = true; break; }
            nal_open(s, p[i], p + i + 1, sz - 1, r.ts);
            i += sz;
        }

    } else if (type == 28 && n >= 3) {              /* FU-A: шматок великої */
        bool S = (p[1] & 0x80) != 0;
        bool E = (p[1] & 0x40) != 0;

        if (S) {
            nal_abort(s);                           /* попередній фрагмент без E */
            uint8_t hdr = (uint8_t)((p[0] & 0xE0) | (p[1] & 0x1F));
            s->in_fu = nal_open(s, hdr, p + 2, n - 2, r.ts);
        } else if (s->in_fu) {
            if (!au_put(s, p + 2, n - 2)) nal_abort(s);
            else if (E) s->in_fu = false;           /* одиниця зібралася повністю */
        }
        /* пакет без S, коли фрагмент не почато, — хвіст чужої одиниці: тиша */

    } else {
        s->damaged = true;               /* 25–27, 29 і сміття — не наш випадок */
    }

    if (r.marker)                        /* останній пакет кадру */
        au_emit(s);
}
