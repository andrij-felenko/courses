#include "secure_frame.h"

#include <string.h>

/*
 * Поля читаємо побайтово, а не накладанням struct на буфер.
 *
 * Дві причини, і обидві коштують прошивці життя. Перша: буфер приїхав з DMA
 * і лежить за довільною адресою, а на Cortex-M0 звернення до 64-бітного
 * seq_num за невирівняною адресою — це HardFault, тобто перезавантаження
 * контролера з пульта зловмисника. Друга: порядок байтів у кадрі заданий
 * протоколом (молодший перший), а не тим, на якому ядрі зібрали прошивку.
 */
static uint16_t rd_u16le(const uint8_t *p)
{
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static uint32_t rd_u32le(const uint8_t *p)
{
    return (uint32_t)p[0]         | ((uint32_t)p[1] << 8)
         | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static uint64_t rd_u64le(const uint8_t *p)
{
    uint64_t v = 0;
    for (unsigned i = 0; i < 8U; ++i) {
        v |= (uint64_t)p[i] << (8U * i);
    }
    return v;
}

/*
 * Порівняння тегів за фіксовану кількість тактів: без раннього виходу на
 * першому розбіжному байті. Інакше зловмисник підбирає тег побайтово,
 * міряючи затримку відповіді, — 32·256 спроб замість 2^256.
 * volatile не дає компілятору "оптимізувати" цикл назад у ранній вихід.
 */
static int verify_tag(const uint8_t *a, const uint8_t *b, size_t len)
{
    volatile uint8_t diff = 0;
    for (size_t i = 0; i < len; ++i) {
        diff = (uint8_t)(diff | (a[i] ^ b[i]));
    }
    return (diff == 0) ? 0 : -1;
}

const char *secure_status_str(SecureStatus status)
{
    switch (status) {
    case SECURE_OK:                    return "OK";
    case SECURE_ERR_BUFFER_TOO_SMALL:  return "BUFFER_TOO_SMALL";
    case SECURE_ERR_INVALID_MAGIC:     return "INVALID_MAGIC";
    case SECURE_ERR_PAYLOAD_MISMATCH:  return "PAYLOAD_MISMATCH";
    case SECURE_ERR_AUTH_FAILED:       return "AUTH_FAILED";
    case SECURE_ERR_TIMESTAMP_EXPIRED: return "TIMESTAMP_EXPIRED";
    case SECURE_ERR_REPLAY_DETECTED:   return "REPLAY_DETECTED";
    default:                           return "UNKNOWN";
    }
}

void replay_window_init(ReplayWindow *win)
{
    win->max_seq = 0;
    win->bitmap  = 0;
}

bool replay_window_check(const ReplayWindow *win, uint64_t seq)
{
    if (seq == 0) {
        return false;               /* нуль зарезервовано під "вікно порожнє" */
    }
    if (seq > win->max_seq) {
        return true;                /* новий рекорд — точно ще не бачили */
    }

    uint64_t diff = win->max_seq - seq;
    if (diff >= REPLAY_WINDOW_SIZE) {
        return false;               /* старіший за все вікно: пам'яті вже немає */
    }
    return (win->bitmap & (1ULL << diff)) == 0;   /* біт стоїть — це дублікат */
}

void replay_window_commit(ReplayWindow *win, uint64_t seq)
{
    if (seq > win->max_seq) {
        uint64_t shift = seq - win->max_seq;
        if (shift >= REPLAY_WINDOW_SIZE) {
            win->bitmap = 1ULL;     /* стрибок довший за вікно — маска марна */
        } else {
            /* Зсув на 64 в C — невизначена поведінка, тому гілка вище. */
            win->bitmap = (win->bitmap << shift) | 1ULL;
        }
        win->max_seq = seq;
    } else {
        uint64_t diff = win->max_seq - seq;
        if (diff < REPLAY_WINDOW_SIZE) {
            win->bitmap |= (1ULL << diff);   /* запізнілий пакет усередині вікна */
        }
    }
}

void secure_channel_init(SecureChannel *ch, const uint8_t *key, size_t key_len,
                         uint32_t max_drift_s)
{
    ch->key         = key;
    ch->key_len     = key_len;
    ch->max_drift_s = max_drift_s;
    replay_window_init(&ch->window);
}

SecureStatus secure_frame_parse(SecureChannel *ch,
                                const uint8_t *frame, size_t frame_len,
                                uint32_t now_s,
                                SecureCommand *out)
{
    /* 0. Рамка. Поки в буфері немає навіть заголовка з тегом, читати нічого. */
    if (frame_len < SECURE_FRAME_OVERHEAD) {
        return SECURE_ERR_BUFFER_TOO_SMALL;
    }

    if (rd_u16le(frame) != SECURE_FRAME_MAGIC) {
        return SECURE_ERR_INVALID_MAGIC;
    }

    uint16_t payload_len = rd_u16le(frame + 16);
    size_t   signed_len  = (size_t)SECURE_HEADER_SIZE + payload_len;
    size_t   total_len   = signed_len + SECURE_TAG_SIZE;

    /* Оголошена довжина мусить уміщатися в те, що справді прийшло. Буфер
     * може бути й довшим (DMA віддає його блоком фіксованого розміру) —
     * зайвий хвіст просто не входить у кадр і під підпис не потрапляє. */
    if (total_len > frame_len) {
        return SECURE_ERR_PAYLOAD_MISMATCH;
    }

    /* 1. Автентифікація ПЕРШОЮ. Нижче ми ще не торкалися жодного поля
     *    корисного навантаження — тільки рамки, потрібної, щоб знайти тег. */
    uint8_t computed_tag[SECURE_TAG_SIZE];
    hmac_sha256(ch->key, ch->key_len, frame, signed_len, computed_tag);

    int tag_ok = verify_tag(frame + signed_len, computed_tag, SECURE_TAG_SIZE);
    crypto_wipe(computed_tag, sizeof computed_tag);
    if (tag_ok != 0) {
        return SECURE_ERR_AUTH_FAILED;
    }

    /* Далі поля вже підписані відправником — їм можна вірити. */
    uint64_t seq_num   = rd_u64le(frame + 4);
    uint32_t timestamp = rd_u32le(frame + 12);

    /* 2. Часові межі. Підписаний, але дворічної давнини кадр — так само
     *    атака повтору, просто на канал, де вікно вже зсунулося. */
    uint32_t drift = (now_s >= timestamp) ? (now_s - timestamp)
                                          : (timestamp - now_s);
    if (drift > ch->max_drift_s) {
        return SECURE_ERR_TIMESTAMP_EXPIRED;
    }

    /* 3. Ковзне вікно: дублікат чи безнадійно застарілий лічильник. */
    if (!replay_window_check(&ch->window, seq_num)) {
        return SECURE_ERR_REPLAY_DETECTED;
    }

    /* 4. Стан рухаємо лише тепер, коли кадр пройшов усі перевірки. */
    replay_window_commit(&ch->window, seq_num);

    /* 5. Віддаємо команду диспетчеру: навантаження без копіювання. */
    out->msg_type    = frame[2];
    out->seq_num     = seq_num;
    out->timestamp   = timestamp;
    out->payload     = frame + SECURE_HEADER_SIZE;
    out->payload_len = payload_len;

    return SECURE_OK;
}
