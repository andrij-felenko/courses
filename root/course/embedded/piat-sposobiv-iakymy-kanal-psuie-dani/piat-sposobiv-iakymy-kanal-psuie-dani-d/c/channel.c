#include "channel.h"

#include <string.h>

static uint32_t xorshift32(uint32_t *state) {
    uint32_t x = *state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    *state = x;
    return x;
}

static bool roll(channel_t *ch, uint16_t permille) {
    return (xorshift32(&ch->rng) % 1000U) < permille;
}

// Завада тривалістю кількасот мікросекунд б'є не один біт, а пачку сусідніх.
static void corrupt_burst(channel_t *ch, uint8_t *data, size_t len) {
    const size_t total_bits = len * 8U;
    if (total_bits == 0U) {
        return;
    }
    const size_t start = xorshift32(&ch->rng) % total_bits;
    const unsigned width = 3U + xorshift32(&ch->rng) % 8U;   // 3..10 бітів поспіль

    for (unsigned i = 0; i < width; ++i) {
        const size_t bit = start + i;
        if (bit >= total_bits) {
            break;
        }
        data[bit / 8U] ^= (uint8_t)(0x80U >> (bit % 8U));
    }
}

static void push_bytes(channel_t *ch, const uint8_t *bytes, size_t len) {
    if (ch->stream_len + len > CHANNEL_STREAM_CAP) {
        ch->stats.overflow++;   // черга лінії переповнена — байти гинуть, як у FIFO UART
        return;
    }
    for (size_t i = 0; i < len; ++i) {
        ch->stream[(ch->stream_head + ch->stream_len + i) % CHANNEL_STREAM_CAP] = bytes[i];
    }
    ch->stream_len += len;
}

void channel_init(channel_t *ch, const channel_cfg_t *cfg, uint32_t seed) {
    memset(ch, 0, sizeof(*ch));
    ch->cfg = *cfg;
    ch->rng = (seed != 0U) ? seed : 1U;
}

void channel_send(channel_t *ch, const uint8_t *frame, size_t len) {
    ch->stats.offered++;
    if (len == 0U || len > CHANNEL_PKT_CAP) {
        return;
    }

    if (roll(ch, ch->cfg.drop_permille)) {
        ch->stats.dropped++;
    } else {
        uint8_t buf[CHANNEL_PKT_CAP];
        memcpy(buf, frame, len);

        if (roll(ch, ch->cfg.burst_permille)) {
            corrupt_burst(ch, buf, len);
            ch->stats.corrupted++;
        }

        if (!ch->has_held && roll(ch, ch->cfg.reorder_permille)) {
            // Кадр пішов довшим маршрутом: віддамо його після наступного.
            memcpy(ch->held, buf, len);
            ch->held_len = len;
            ch->has_held = true;
            ch->stats.reordered++;
            return;
        }

        push_bytes(ch, buf, len);
        if (roll(ch, ch->cfg.duplicate_permille)) {
            push_bytes(ch, buf, len);
            ch->stats.duplicated++;
        }
    }

    if (ch->has_held) {
        push_bytes(ch, ch->held, ch->held_len);
        ch->has_held = false;
    }
}

void channel_pump(channel_t *ch, channel_sink_fn sink, void *ctx) {
    if (ch->stream_len == 0U) {
        if (ch->has_held) {
            // Нових кадрів більше немає — випускаємо затриманий, щоб не завис назавжди.
            push_bytes(ch, ch->held, ch->held_len);
            ch->has_held = false;
        }
        return;
    }

    size_t chunk = 1U + xorshift32(&ch->rng) % CHANNEL_MAX_CHUNK;
    if (chunk > ch->stream_len) {
        chunk = ch->stream_len;
    }

    uint8_t tmp[CHANNEL_MAX_CHUNK];
    for (size_t i = 0; i < chunk; ++i) {
        tmp[i] = ch->stream[(ch->stream_head + i) % CHANNEL_STREAM_CAP];
    }
    ch->stream_head = (ch->stream_head + chunk) % CHANNEL_STREAM_CAP;
    ch->stream_len -= chunk;

    // Шматок може розрізати кадр посередині або принести півтора кадру відразу.
    sink(tmp, chunk, ctx);
}

bool channel_idle(const channel_t *ch) {
    return ch->stream_len == 0U && !ch->has_held;
}
