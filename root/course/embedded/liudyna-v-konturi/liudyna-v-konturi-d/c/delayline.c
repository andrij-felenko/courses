#include "delayline.h"

#include <stdlib.h>
#include <string.h>

static uint32_t xorshift32(uint32_t *s) {
    uint32_t x = *s;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    *s = x ? x : 0x1234567u;
    return *s;
}

/* Рівномірний розкид у межах [-1, +1). */
static float rand_sym(uint32_t *s) {
    return (float)(xorshift32(s) >> 8) / (float)(1u << 23) - 1.0f;
}

bool delay_init(DelayLine *dl, float base_delay, float jitter, bool buffered,
                float dt, uint32_t seed) {
    int need;

    if (!dl || dt <= 0.0f || base_delay < 0.0f || jitter < 0.0f) {
        return false;
    }
    memset(dl, 0, sizeof(*dl));

    /* Затримка не буває від'ємною: розкид не може бути більшим за саму сталу. */
    if (jitter > base_delay) {
        jitter = base_delay;
    }
    /* Кільце має вміщати найгірший випадок плюс запас на буфер джитера. */
    need = (int)((base_delay + 2.0f * jitter) / dt) + 8;
    dl->cap = need < 16 ? 16 : need;

    dl->slot = (LinkPacket *)calloc((size_t)dl->cap, sizeof(LinkPacket));
    dl->avail = (float *)calloc((size_t)dl->cap, sizeof(float));
    if (!dl->slot || !dl->avail) {
        delay_free(dl);
        return false;
    }

    dl->base_delay = base_delay;
    dl->jitter = jitter;
    dl->buffered = buffered;
    dl->rng = seed ? seed : 0x9e3779b9u;
    return true;
}

void delay_free(DelayLine *dl) {
    if (!dl) {
        return;
    }
    free(dl->slot);
    free(dl->avail);
    dl->slot = NULL;
    dl->avail = NULL;
    dl->cap = 0;
    dl->count = 0;
}

void delay_push(DelayLine *dl, LinkPacket pkt, float now) {
    float d;

    if (!dl || !dl->slot) {
        return;
    }
    if (dl->buffered) {
        /* Парадокс буфера джитера: розкид зникає, але платить за це КОЖЕН
           пакет — сталим лагом найгіршого випадку. */
        d = dl->base_delay + dl->jitter;
    } else {
        d = dl->base_delay + dl->jitter * rand_sym(&dl->rng);
        if (d < 0.0f) {
            d = 0.0f;
        }
    }
    if (dl->count == dl->cap) {
        /* Кільце переповнене — гине найстаріший пакет. У штатному режимі
           не трапляється, бо приймач забирає кадр щокроку. */
        dl->tail = (dl->tail + 1) % dl->cap;
        dl->count--;
        dl->drops++;
    }
    dl->slot[dl->head] = pkt;
    dl->avail[dl->head] = now + d;
    dl->head = (dl->head + 1) % dl->cap;
    dl->count++;
}

LinkPacket delay_pop(DelayLine *dl, float now) {
    int released = 0;

    if (!dl || !dl->slot) {
        LinkPacket zero = {{0.0f}};
        return zero;
    }
    /* Потік упорядкований: пакет, що спізнився, тримає за собою й ті, що
       встигли. Саме звідси беруться «застигання» й «ривки» картинки. */
    while (dl->count > 0 && dl->avail[dl->tail] <= now) {
        dl->last_out = dl->slot[dl->tail];
        dl->tail = (dl->tail + 1) % dl->cap;
        dl->count--;
        released++;
    }
    if (released == 0) {
        dl->freezes++;
    }
    return dl->last_out;
}

float delay_effective(const DelayLine *dl) {
    if (!dl) {
        return 0.0f;
    }
    return dl->buffered ? dl->base_delay + dl->jitter : dl->base_delay;
}

int delay_freezes(const DelayLine *dl) { return dl ? dl->freezes : 0; }

int delay_drops(const DelayLine *dl) { return dl ? dl->drops : 0; }
