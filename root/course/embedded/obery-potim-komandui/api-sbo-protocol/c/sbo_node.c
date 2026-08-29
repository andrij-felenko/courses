/* Реалізація селектора: замок, таймер знешкодження, фільтр широкомовних
   адрес і коди відмов розділу 5. Уся логіка «чи можна» — тут. */
#include "sbo_node.h"

#include <string.h>

/* Порівняння моментів, стійке до переповнення 32-бітного лічильника мс. */
static bool time_reached(uint32_t now, uint32_t moment)
{
    return (int32_t)(now - moment) >= 0;
}

static uint32_t next_token(struct sbo_node *n)
{
    /* xorshift32: непередбачуваності в межах польоту досить, криптостійкості
       протокол не обіцяє. Нуль зарезервовано під «замка немає». */
    uint32_t x = n->rng;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    if (x == 0) {
        x = 0xA5A5A5A5u;
    }
    n->rng = x;
    return x;
}

static void release(struct sbo_node *n, uint32_t now_ms, bool expired)
{
    if (expired) {
        /* Пам'ятаємо згорілий токен: тоді на запізнілий OPERATE_REQ
           можна відповісти точним ERR_SBO_TIMEOUT_EXPIRED, а не NOT_ARMED. */
        n->expired_token = n->token;
    }
    n->state = SBO_STATE_IDLE;
    n->owner = 0;
    n->comp = 0;
    n->cmd_code = 0;
    n->token = 0;
    n->deadline_ms = 0;
    n->cooldown_until_ms = now_ms + SBO_T_COOLDOWN_MS;
    n->flags &= (uint8_t)~SBO_FLAG_ARMED;
}

void sbo_node_init(struct sbo_node *n, uint8_t node_id, uint32_t seed)
{
    memset(n, 0, sizeof(*n));
    n->node_id = node_id;
    n->state = SBO_STATE_IDLE;
    n->rng = seed ? seed : 0x1234567u;
    n->password[0] = 'S';
    n->password[1] = 'B';
    n->password[2] = 'O';
    n->password[3] = '!';
    n->act.motors_live = true;
    n->act.armed = true;
    n->act.healthy = true;
}

void sbo_node_tick(struct sbo_node *n, uint32_t now_ms)
{
    if (n->state == SBO_STATE_ARMED && time_reached(now_ms, n->deadline_ms)) {
        release(n, now_ms, true);
    }
}

uint16_t sbo_node_remaining_ms(const struct sbo_node *n, uint32_t now_ms)
{
    if (n->state != SBO_STATE_ARMED || time_reached(now_ms, n->deadline_ms)) {
        return 0;
    }
    return (uint16_t)(n->deadline_ms - now_ms);
}

uint8_t sbo_node_heartbeat_flags(const struct sbo_node *n)
{
    return n->flags;
}

/* Складає відповідь. payload_byte < 0 означає порожнє навантаження. */
static size_t emit(struct sbo_node *n, const struct sbo_frame *req, uint8_t type,
                   uint32_t token, uint16_t window_ms, int payload_byte,
                   uint8_t *out, size_t cap)
{
    struct sbo_frame r;
    memset(&r, 0, sizeof(r));
    r.seq = n->seq++;
    r.msg_type = type;
    r.source_id = n->node_id;
    r.target_id = req->source_id;     /* відповідь завжди адресна */
    r.target_comp = req->target_comp;
    r.sbo_state = n->state;
    r.sbo_token = token;
    r.cmd_code = req->cmd_code;
    r.timeout_ms = window_ms;
    if (payload_byte >= 0) {
        r.payload[0] = (uint8_t)payload_byte;
        r.payload_len = 1;
    }
    return sbo_encode(&r, out, cap);
}

static size_t nack(struct sbo_node *n, const struct sbo_frame *req, uint8_t type,
                   uint8_t err, uint8_t *out, size_t cap)
{
    n->flags |= SBO_FLAG_LAST_REJECT;
    n->rejects++;
    return emit(n, req, type, 0, 0, (int)err, out, cap);
}

static bool comp_known(uint8_t comp)
{
    return comp == SBO_COMP_FC || comp == SBO_COMP_ESC || comp == SBO_COMP_NAV;
}

/* Низькорівнева дія. Повертає 0 або код відмови розділу 5. */
static uint8_t actuate(struct sbo_node *n, const struct sbo_frame *f)
{
    if (!n->act.healthy) {
        return ERR_SBO_HARDWARE_FAULT;
    }
    switch (f->cmd_code) {
    case CMD_PING:
        return 0;
    case CMD_REQUEST_TELEMETRY:
        return 0;
    case CMD_EMERGENCY_MOTOR_CUT:
        n->act.motors_live = false;
        n->act.armed = false;
        return 0;
    case CMD_FORCE_DISARM:
        n->act.armed = false;
        return 0;
    case CMD_FLIGHT_MODE_OVERRIDE:
        if (f->payload_len < 1) {
            return ERR_SBO_CMD_MISMATCH;   /* режим не названо */
        }
        n->act.flight_mode = f->payload[0];
        return 0;
    case CMD_REBOOT_AUTOPILOT:
        n->act.reboot_pending = true;
        return 0;
    case CMD_FACTORY_RESET_PARAMS:
        n->act.params_default = true;
        return 0;
    case CMD_PAYLOAD_DROP_ACTUATE:
        if (n->act.payload_dropped) {
            return ERR_SBO_HARDWARE_FAULT; /* замок одноразовий, скидач порожній */
        }
        n->act.payload_dropped = true;
        return 0;
    default:
        return ERR_SBO_CMD_MISMATCH;
    }
}

static size_t on_select(struct sbo_node *n, const struct sbo_frame *f,
                        uint32_t now_ms, uint8_t *out, size_t cap)
{
    if (!sbo_cmd_is_critical(f->cmd_code)) {
        /* Звичайні команди виконуються напряму — селекція для них безглузда. */
        return nack(n, f, SBO_MSG_SELECT_NACK, ERR_SBO_CMD_MISMATCH, out, cap);
    }
    if (!comp_known(f->target_comp)) {
        return nack(n, f, SBO_MSG_SELECT_NACK, ERR_SBO_HARDWARE_FAULT, out, cap);
    }
    if (n->state != SBO_STATE_IDLE) {
        /* Сценарій В: замок уже захоплено, і не важливо ким. */
        return nack(n, f, SBO_MSG_SELECT_NACK, ERR_SBO_BUSY, out, cap);
    }
    if (!time_reached(now_ms, n->cooldown_until_ms)) {
        /* T_cooldown: захисна пауза між селекціями одного вузла. */
        return nack(n, f, SBO_MSG_SELECT_NACK, ERR_SBO_BUSY, out, cap);
    }
    if (!n->act.healthy) {
        return nack(n, f, SBO_MSG_SELECT_NACK, ERR_SBO_HARDWARE_FAULT, out, cap);
    }

    const uint16_t window = sbo_clamp_window(f->timeout_ms);
    n->owner = f->source_id;
    n->comp = f->target_comp;
    n->cmd_code = f->cmd_code;
    n->token = next_token(n);
    n->deadline_ms = now_ms + window;
    n->state = SBO_STATE_ARMED;
    n->flags |= SBO_FLAG_ARMED;
    n->flags &= (uint8_t)~SBO_FLAG_LAST_REJECT;

    return emit(n, f, SBO_MSG_SELECT_ACK, n->token, window, -1, out, cap);
}

static size_t on_operate(struct sbo_node *n, const struct sbo_frame *f,
                         uint32_t now_ms, uint8_t *out, size_t cap)
{
    if (!sbo_cmd_is_critical(f->cmd_code)) {
        /* Звичайний клас: ні замка, ні токена — просто виконуємо. */
        const uint8_t err = actuate(n, f);
        if (err) {
            return nack(n, f, SBO_MSG_OPERATE_NACK, err, out, cap);
        }
        return emit(n, f, SBO_MSG_OPERATE_ACK, 0, 0, -1, out, cap);
    }

    if (n->state == SBO_STATE_EXECUTING) {
        return nack(n, f, SBO_MSG_OPERATE_NACK, ERR_SBO_BUSY, out, cap);
    }
    if (n->state == SBO_STATE_IDLE) {
        /* Сценарій Б: токен пульта збігся зі згорілим — кажемо про час. */
        const uint8_t err = (f->sbo_token != 0 && f->sbo_token == n->expired_token)
                                ? ERR_SBO_TIMEOUT_EXPIRED
                                : ERR_SBO_NOT_ARMED;
        return nack(n, f, SBO_MSG_OPERATE_NACK, err, out, cap);
    }
    if (time_reached(now_ms, n->deadline_ms)) {
        /* Пояс на випадок, коли tick не встиг спрацювати між кадрами. */
        release(n, now_ms, true);
        return nack(n, f, SBO_MSG_OPERATE_NACK, ERR_SBO_TIMEOUT_EXPIRED, out, cap);
    }
    if (f->source_id != n->owner) {
        return nack(n, f, SBO_MSG_OPERATE_NACK, ERR_SBO_BUSY, out, cap);
    }
    if (f->sbo_token == 0 || f->sbo_token != n->token) {
        return nack(n, f, SBO_MSG_OPERATE_NACK, ERR_SBO_INVALID_TOKEN, out, cap);
    }
    if (f->cmd_code != n->cmd_code || f->target_comp != n->comp) {
        return nack(n, f, SBO_MSG_OPERATE_NACK, ERR_SBO_CMD_MISMATCH, out, cap);
    }
    if (f->cmd_code == CMD_FACTORY_RESET_PARAMS &&
        (f->payload_len < sizeof(n->password) ||
         memcmp(f->payload, n->password, sizeof(n->password)) != 0)) {
        return nack(n, f, SBO_MSG_OPERATE_NACK, ERR_SBO_CMD_MISMATCH, out, cap);
    }

    n->state = SBO_STATE_EXECUTING;      /* таймер знешкодження більше не діє */
    const uint8_t err = actuate(n, f);
    release(n, now_ms, false);           /* після дії автомат одразу в IDLE */

    if (err) {
        return nack(n, f, SBO_MSG_OPERATE_NACK, err, out, cap);
    }
    n->flags &= (uint8_t)~SBO_FLAG_LAST_REJECT;
    return emit(n, f, SBO_MSG_OPERATE_ACK, 0, 0, -1, out, cap);
}

static size_t on_cancel(struct sbo_node *n, const struct sbo_frame *f,
                        uint32_t now_ms, uint8_t *out, size_t cap)
{
    if (n->state == SBO_STATE_IDLE) {
        /* Скасування вільного вузла нешкідливе: пульт так лікує розсинхрон UI. */
        return emit(n, f, SBO_MSG_CANCEL_ACK, 0, 0, -1, out, cap);
    }
    if (n->state == SBO_STATE_EXECUTING || f->source_id != n->owner) {
        /* Чужий замок не знімаємо: квитанція є, але з причиною відмови. */
        n->flags |= SBO_FLAG_LAST_REJECT;
        n->rejects++;
        return emit(n, f, SBO_MSG_CANCEL_ACK, 0, 0, (int)ERR_SBO_BUSY, out, cap);
    }
    release(n, now_ms, false);
    return emit(n, f, SBO_MSG_CANCEL_ACK, 0, 0, -1, out, cap);
}

static size_t on_ping(struct sbo_node *n, const struct sbo_frame *f,
                      uint32_t now_ms, uint8_t *out, size_t cap)
{
    /* Токен бачить лише власник замка; решті — нуль. */
    const uint32_t token = (n->state == SBO_STATE_ARMED && f->source_id == n->owner)
                               ? n->token
                               : 0u;
    return emit(n, f, SBO_MSG_STATUS_PONG, token,
                sbo_node_remaining_ms(n, now_ms), (int)n->flags, out, cap);
}

size_t sbo_node_handle(struct sbo_node *n, const uint8_t *in, size_t in_len,
                       uint32_t now_ms, uint8_t *out, size_t out_cap)
{
    struct sbo_frame f;
    if (sbo_decode(in, in_len, &f) != SBO_DECODE_OK) {
        n->rx_errors++;      /* битий кадр — в ефір не відповідаємо */
        return 0;
    }

    /* Спершу зістарюємо замок, аж тоді судимо запит: інакше кадр, що прийшов
       на мілісекунду після спливання вікна, виглядав би дійсним. */
    sbo_node_tick(n, now_ms);

    if (f.target_id != n->node_id && f.target_id != SBO_ADDR_BROADCAST) {
        return 0;            /* кадр не нам */
    }

    if (f.target_id == SBO_ADDR_BROADCAST) {
        const bool forbidden = sbo_cmd_is_critical(f.cmd_code) ||
                               f.msg_type == SBO_MSG_SELECT_REQ ||
                               f.msg_type == SBO_MSG_CANCEL_REQ;
        if (forbidden) {
            /* Сценарій Г: причина — ERR_SBO_BROADCAST_FORBIDDEN, але в ефір
               відповіді немає: широкомовний NACK від кожного апарата — шторм. */
            n->security_drops++;
            n->flags |= SBO_FLAG_LAST_REJECT;
            return 0;
        }
    }

    switch (f.msg_type) {
    case SBO_MSG_SELECT_REQ:  return on_select(n, &f, now_ms, out, out_cap);
    case SBO_MSG_OPERATE_REQ: return on_operate(n, &f, now_ms, out, out_cap);
    case SBO_MSG_CANCEL_REQ:  return on_cancel(n, &f, now_ms, out, out_cap);
    case SBO_MSG_STATUS_PING: return on_ping(n, &f, now_ms, out, out_cap);
    default:
        return 0;            /* квитанції та невідомі типи вузол не обробляє */
    }
}
