#include "link.h"

#include <math.h>
#include <string.h>

static void put_u32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)v;
    p[1] = (uint8_t)(v >> 8);
    p[2] = (uint8_t)(v >> 16);
    p[3] = (uint8_t)(v >> 24);
}

static uint32_t get_u32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static void put_i16(uint8_t *p, int16_t v) {
    p[0] = (uint8_t)((uint16_t)v);
    p[1] = (uint8_t)((uint16_t)v >> 8);
}

static int16_t get_i16(const uint8_t *p) {
    return (int16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static uint16_t crc16(const uint8_t *d, size_t n) {
    uint16_t crc = 0xFFFFU;
    for (size_t i = 0; i < n; i++) {
        crc ^= (uint16_t)((uint16_t)d[i] << 8);
        for (int b = 0; b < 8; b++) {
            crc = (crc & 0x8000U) ? (uint16_t)((uint16_t)(crc << 1) ^ 0x1021U) : (uint16_t)(crc << 1);
        }
    }
    return crc;
}

// Мітка автентичності. У виробі тут AES-CMAC або Poly1305 із ключем у
// захищеній пам'яті; для заняття беремо keyed FNV-1a — важливе не саме
// перетворення, а те, ЩО перевірка стоїть перед годуванням мертвої руки.
static uint32_t auth_tag(const uint8_t *d, size_t n, uint32_t key) {
    uint32_t h = 2166136261u ^ key;
    for (size_t i = 0; i < n; i++) {
        h ^= d[i];
        h *= 16777619u;
    }
    h ^= key;
    h *= 16777619u;
    return h;
}

static float clampf(float v, float lo, float hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

// Розкладка кадру: [0] тип · [1..4] сесія · [5..8] номер · [9..12] час
// відправника · [13..14] тяга · [15..16] кермо · [17] резерв ·
// [18..21] мітка автентичності · [22..23] CRC-16.
static size_t build(uint8_t *buf, size_t cap, uint8_t type, uint32_t key, uint32_t session,
                    uint32_t seq, uint32_t t_ms, float throttle, float steering) {
    if (cap < LINK_FRAME_SIZE) return 0U;
    memset(buf, 0, LINK_FRAME_SIZE);
    buf[0] = type;
    put_u32(buf + 1, session);
    put_u32(buf + 5, seq);
    put_u32(buf + 9, t_ms);
    put_i16(buf + 13, (int16_t)lrintf(clampf(throttle, -1.0f, 1.0f) * 10000.0f));
    put_i16(buf + 15, (int16_t)lrintf(clampf(steering, -1.0f, 1.0f) * 10000.0f));
    buf[17] = 0U;
    put_u32(buf + 18, auth_tag(buf, 18U, key));
    uint16_t c = crc16(buf, 22U);
    buf[22] = (uint8_t)c;
    buf[23] = (uint8_t)(c >> 8);
    return LINK_FRAME_SIZE;
}

void link_init(link_t *l, uint32_t key) {
    memset(l, 0, sizeof *l);
    l->key = key;
}

void link_drop_session(link_t *l) {
    l->established = false;
    l->session_id = 0U;
    l->last_seq = 0U;
}

bool link_established(const link_t *l) { return l->established; }

link_status_t link_accept(link_t *l, const uint8_t *frame, size_t len,
                          uint32_t now_ms, link_command_t *out) {
    if (len != LINK_FRAME_SIZE) return LINK_ERR_LENGTH;

    uint16_t crc = (uint16_t)((uint16_t)frame[22] | ((uint16_t)frame[23] << 8));
    if (crc != crc16(frame, 22U)) { l->rej_crc++; return LINK_ERR_CRC; }
    if (get_u32(frame + 18) != auth_tag(frame, 18U, l->key)) { l->rej_auth++; return LINK_ERR_AUTH; }

    uint8_t  type    = frame[0];
    uint32_t session = get_u32(frame + 1);
    uint32_t seq     = get_u32(frame + 5);
    uint32_t t_ms    = get_u32(frame + 9);

    if (type == LINK_TYPE_HELLO) {
        // Нова сесія стирає все, що лишилося від старої: номери кадрів більше
        // не дійсні, а команди, застряглі в буферах передавача, — тим паче.
        l->session_id = session;
        l->last_seq = seq;
        l->established = true;
        l->clock_bias = (int32_t)(t_ms - now_ms);
        l->accepted++;

        out->type = type;
        out->session_id = session;
        out->seq = seq;
        out->t_ms = t_ms;
        out->throttle = 0.0f;
        out->steering = 0.0f;
        return LINK_OK;
    }
    if (type != LINK_TYPE_CMD) return LINK_ERR_TYPE;

    if (!l->established || session != l->session_id) { l->rej_session++; return LINK_ERR_SESSION; }
    if ((int32_t)(seq - l->last_seq) <= 0) { l->rej_replay++; return LINK_ERR_REPLAY; }

    // Вік команди міряємо в часовій шкалі відправника: зсув його годинника
    // ми запам'ятали на рукостисканні, а свій монотонний час підтягуємо
    // окремо й повільно, тому мішати їх тут не можна.
    int32_t age = (int32_t)((uint32_t)((int32_t)now_ms + l->clock_bias) - t_ms);
    if (age > (int32_t)LINK_MAX_AGE_MS) { l->rej_stale++; return LINK_ERR_STALE; }

    l->last_seq = seq;
    l->accepted++;

    out->type = type;
    out->session_id = session;
    out->seq = seq;
    out->t_ms = t_ms;
    out->throttle = (float)get_i16(frame + 13) / 10000.0f;
    out->steering = (float)get_i16(frame + 15) / 10000.0f;
    return LINK_OK;
}

size_t link_encode_hello(uint8_t *buf, size_t cap, uint32_t key,
                         uint32_t session_id, uint32_t t_ms) {
    return build(buf, cap, LINK_TYPE_HELLO, key, session_id, 0U, t_ms, 0.0f, 0.0f);
}

size_t link_encode_command(uint8_t *buf, size_t cap, uint32_t key, uint32_t session_id,
                           uint32_t seq, uint32_t t_ms, float throttle, float steering) {
    return build(buf, cap, LINK_TYPE_CMD, key, session_id, seq, t_ms, throttle, steering);
}

const char *link_status_name(link_status_t st) {
    switch (st) {
    case LINK_OK:           return "прийнято";
    case LINK_ERR_LENGTH:   return "хибна довжина";
    case LINK_ERR_TYPE:     return "невідомий тип";
    case LINK_ERR_CRC:      return "CRC не збігся";
    case LINK_ERR_AUTH:     return "мітка автентичності хибна";
    case LINK_ERR_SESSION:  return "чужа або скасована сесія";
    case LINK_ERR_REPLAY:   return "повтор старого кадру";
    case LINK_ERR_STALE:    return "команда застаріла";
    default:                return "?";
    }
}
