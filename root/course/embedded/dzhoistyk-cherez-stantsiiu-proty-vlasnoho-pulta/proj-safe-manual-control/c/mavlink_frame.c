#include "mavlink_frame.h"

#include <string.h>

enum {
    ST_IDLE = 0, ST_LEN, ST_INCOMPAT, ST_COMPAT, ST_SEQ, ST_SYSID, ST_COMPID,
    ST_MSGID1, ST_MSGID2, ST_MSGID3, ST_PAYLOAD, ST_CRC1, ST_CRC2
};

/* CRC-16/MCRF4XX — той самий поліном, що в mavlink_helpers.h. */
static void crc_acc(uint16_t *crc, uint8_t b)
{
    uint8_t tmp = b ^ (uint8_t)(*crc & 0xFFu);
    tmp ^= (uint8_t)(tmp << 4);
    *crc = (uint16_t)((*crc >> 8) ^ ((uint16_t)tmp << 8) ^ ((uint16_t)tmp << 3) ^ ((uint16_t)tmp >> 4));
}

/* CRC_EXTRA і канонічна довжина — з XML діалекту common. Без CRC_EXTRA кадр
 * узагалі не перевірити, тому невідомий msgid чесно відкидаємо. */
static bool msg_info(uint32_t msgid, uint8_t *crc_extra, uint8_t *canon_len)
{
    switch (msgid) {
    case MAV_MSG_HEARTBEAT:      *crc_extra = 50;  *canon_len = 9;  return true;
    case MAV_MSG_MANUAL_CONTROL: *crc_extra = 243; *canon_len = 11; return true;
    case MAV_MSG_COMMAND_LONG:   *crc_extra = 152; *canon_len = 33; return true;
    case MAV_MSG_COMMAND_ACK:    *crc_extra = 143; *canon_len = 3;  return true;
    default: return false;
    }
}

static uint16_t rd_u16(const uint8_t *p) { return (uint16_t)(p[0] | ((uint16_t)p[1] << 8)); }
static int16_t  rd_i16(const uint8_t *p) { return (int16_t)rd_u16(p); }

static uint32_t rd_u32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static float rd_f32(const uint8_t *p)
{
    uint32_t v = rd_u32(p);
    float f;
    memcpy(&f, &v, sizeof(f));
    return f;
}

static void wr_u16(uint8_t *p, uint16_t v) { p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8); }
static void wr_i16(uint8_t *p, int16_t v)  { wr_u16(p, (uint16_t)v); }

static void wr_u32(uint8_t *p, uint32_t v)
{
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8); p[2] = (uint8_t)(v >> 16); p[3] = (uint8_t)(v >> 24);
}

static void wr_f32(uint8_t *p, float f)
{
    uint32_t v;
    memcpy(&v, &f, sizeof(v));
    wr_u32(p, v);
}

void mav_parser_init(mav_parser_t *p)
{
    memset(p, 0, sizeof(*p));
    p->state = ST_IDLE;
}

static void enter_payload(mav_parser_t *p)
{
    p->idx = 0;
    memset(p->payload, 0, sizeof(p->payload)); /* обрізані нулі відновлюються тут */
    p->state = (p->len == 0) ? ST_CRC1 : ST_PAYLOAD;
}

bool mav_parse_byte(mav_parser_t *p, uint8_t b, mav_frame_t *out)
{
    if (p->skip) {           /* хвіст підпису кадру v2 — тіло вже віддано */
        p->skip--;
        return false;
    }

    switch (p->state) {
    case ST_IDLE:
        if (b == MAV_STX_V2 || b == MAV_STX_V1) {
            p->is_v2    = (b == MAV_STX_V2);
            p->crc      = 0xFFFFu;
            p->incompat = 0;
            p->compat   = 0;
            p->state    = ST_LEN;
        }
        return false;

    case ST_LEN:
        p->len = b;
        crc_acc(&p->crc, b);
        p->state = p->is_v2 ? ST_INCOMPAT : ST_SEQ;
        return false;

    case ST_INCOMPAT:
        p->incompat = b;
        crc_acc(&p->crc, b);
        /* Прапорець 0x01 — підпис, його ми вміємо пропустити. Будь-який інший
         * означає кадр, якого ми не розуміємо: специфікація вимагає відкинути. */
        if (b & (uint8_t)~0x01u) {
            p->stat_unsupported++;
            p->state = ST_IDLE;
            return false;
        }
        p->state = ST_COMPAT;
        return false;

    case ST_COMPAT:
        p->compat = b;
        crc_acc(&p->crc, b);
        p->state = ST_SEQ;
        return false;

    case ST_SEQ:
        p->seq = b;
        crc_acc(&p->crc, b);
        p->state = ST_SYSID;
        return false;

    case ST_SYSID:
        p->sysid = b;
        crc_acc(&p->crc, b);
        p->state = ST_COMPID;
        return false;

    case ST_COMPID:
        p->compid = b;
        crc_acc(&p->crc, b);
        p->state = ST_MSGID1;
        return false;

    case ST_MSGID1:
        p->msgid = b;
        crc_acc(&p->crc, b);
        if (p->is_v2) {
            p->state = ST_MSGID2;
        } else {
            enter_payload(p); /* у v1 ідентифікатор однобайтовий */
        }
        return false;

    case ST_MSGID2:
        p->msgid |= (uint32_t)b << 8;
        crc_acc(&p->crc, b);
        p->state = ST_MSGID3;
        return false;

    case ST_MSGID3:
        p->msgid |= (uint32_t)b << 16;
        crc_acc(&p->crc, b);
        enter_payload(p);
        return false;

    case ST_PAYLOAD:
        p->payload[p->idx++] = b;
        crc_acc(&p->crc, b);
        if (p->idx >= p->len)
            p->state = ST_CRC1;
        return false;

    case ST_CRC1:
        p->rx_crc = b;
        p->state  = ST_CRC2;
        return false;

    case ST_CRC2: {
        uint8_t extra = 0, canon = 0;
        uint16_t crc;
        bool known;

        p->rx_crc |= (uint16_t)b << 8;
        p->state = ST_IDLE;
        if (p->is_v2 && (p->incompat & 0x01u))
            p->skip = MAV_SIGNATURE_LEN;

        known = msg_info(p->msgid, &extra, &canon);
        if (!known) {
            p->stat_unknown++;
            return false;
        }

        crc = p->crc;
        crc_acc(&crc, extra);
        if (crc != p->rx_crc) {
            p->stat_crc_err++;
            return false;
        }

        out->sysid  = p->sysid;
        out->compid = p->compid;
        out->seq    = p->seq;
        out->msgid  = p->msgid;
        out->len    = p->len;
        memcpy(out->payload, p->payload, sizeof(out->payload));
        p->stat_ok++;
        return true;
    }

    default:
        p->state = ST_IDLE;
        return false;
    }
}

uint8_t mav_pack_heartbeat(uint8_t *p, const mav_heartbeat_t *m)
{
    wr_u32(p, m->custom_mode);
    p[4] = m->type;
    p[5] = m->autopilot;
    p[6] = m->base_mode;
    p[7] = m->system_status;
    p[8] = m->mavlink_version;
    return 9;
}

uint8_t mav_pack_manual_control(uint8_t *p, const mav_manual_control_t *m)
{
    wr_i16(p + 0, m->x);
    wr_i16(p + 2, m->y);
    wr_i16(p + 4, m->z);
    wr_i16(p + 6, m->r);
    wr_u16(p + 8, m->buttons);
    p[10] = m->target;
    return 11;
}

uint8_t mav_pack_command_long(uint8_t *p, const mav_command_long_t *m)
{
    int i;
    for (i = 0; i < 7; ++i)
        wr_f32(p + i * 4, m->param[i]);
    wr_u16(p + 28, m->command);
    p[30] = m->target_system;
    p[31] = m->target_component;
    p[32] = m->confirmation;
    return 33;
}

uint8_t mav_pack_command_ack(uint8_t *p, const mav_command_ack_t *m)
{
    wr_u16(p, m->command);
    p[2] = m->result;
    return 3;
}

void mav_unpack_heartbeat(const mav_frame_t *f, mav_heartbeat_t *m)
{
    m->custom_mode     = rd_u32(f->payload);
    m->type            = f->payload[4];
    m->autopilot       = f->payload[5];
    m->base_mode       = f->payload[6];
    m->system_status   = f->payload[7];
    m->mavlink_version = f->payload[8];
}

void mav_unpack_manual_control(const mav_frame_t *f, mav_manual_control_t *m)
{
    m->x       = rd_i16(f->payload + 0);
    m->y       = rd_i16(f->payload + 2);
    m->z       = rd_i16(f->payload + 4);
    m->r       = rd_i16(f->payload + 6);
    m->buttons = rd_u16(f->payload + 8);
    m->target  = f->payload[10];
}

void mav_unpack_command_long(const mav_frame_t *f, mav_command_long_t *m)
{
    int i;
    for (i = 0; i < 7; ++i)
        m->param[i] = rd_f32(f->payload + i * 4);
    m->command          = rd_u16(f->payload + 28);
    m->target_system    = f->payload[30];
    m->target_component = f->payload[31];
    m->confirmation     = f->payload[32];
}

size_t mav_encode(uint8_t *buf, size_t cap, uint8_t sysid, uint8_t compid,
                  uint8_t seq, uint32_t msgid, const uint8_t *payload, uint8_t len)
{
    uint8_t  extra = 0, canon = 0;
    uint16_t crc = 0xFFFFu;
    size_t   n = 0;
    uint8_t  i;

    if (!msg_info(msgid, &extra, &canon))
        return 0;

    /* Обрізання хвостових нулів — правило кадру v2; щонайменше один байт лишається. */
    while (len > 1 && payload[len - 1] == 0)
        len--;

    if (cap < (size_t)len + 12u)
        return 0;

    buf[n++] = MAV_STX_V2;
    buf[n++] = len;
    buf[n++] = 0; /* incompat_flags: без підпису */
    buf[n++] = 0; /* compat_flags */
    buf[n++] = seq;
    buf[n++] = sysid;
    buf[n++] = compid;
    buf[n++] = (uint8_t)(msgid & 0xFFu);
    buf[n++] = (uint8_t)((msgid >> 8) & 0xFFu);
    buf[n++] = (uint8_t)((msgid >> 16) & 0xFFu);
    for (i = 0; i < len; ++i)
        buf[n++] = payload[i];

    for (i = 1; i < n; ++i)   /* CRC рахується з байта довжини, STX не входить */
        crc_acc(&crc, buf[i]);
    crc_acc(&crc, extra);

    buf[n++] = (uint8_t)(crc & 0xFFu);
    buf[n++] = (uint8_t)(crc >> 8);
    return n;
}
