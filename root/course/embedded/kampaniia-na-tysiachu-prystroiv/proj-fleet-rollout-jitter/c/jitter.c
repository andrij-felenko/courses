#include "jitter.h"

#include "platform.h"

static uint32_t splitmix32(uint32_t *state)
{
    uint32_t z = (*state += 0x9E3779B9u);
    z = (z ^ (z >> 16)) * 0x21F0AAADu;
    z = (z ^ (z >> 15)) * 0x735A2D97u;
    return z ^ (z >> 15);
}

static uint32_t rotl(uint32_t x, unsigned n)
{
    return (x << n) | (x >> (32u - n));
}

void rng_seed_from_hardware(rng_t *r, const uint8_t hw_id[16])
{
    uint32_t mix = 0x811C9DC5u;

    /* Кожне джерело може бути відсутнє й повернути нуль — тому їх кілька, і
     * жодне не є єдиною опорою. */
    mix ^= plat_trng_word();          mix *= 16777619u;
    mix ^= plat_adc_noise_word();     mix *= 16777619u;
    mix ^= plat_timer_jitter_word();  mix *= 16777619u;
    mix ^= (uint32_t)plat_uptime_ms(); mix *= 16777619u;

    /* Ідентифікатор чипа: постійна складова, різна на кожному вузлі парку. */
    for (unsigned i = 0; i < 16; ++i) {
        mix ^= hw_id[i];
        mix *= 16777619u;
    }

    for (unsigned i = 0; i < 4; ++i) {
        r->s[i] = splitmix32(&mix);
    }

    /* Нульовий стан xoshiro не покидає нуля — це і є «сід нуль», з якого
     * тисяча вузлів вирушає в одну мілісекунду. */
    if ((r->s[0] | r->s[1] | r->s[2] | r->s[3]) == 0u) {
        r->s[0] = 0xA5A5A5A5u;
        r->s[1] = (uint32_t)hw_id[0] | 1u;
        r->s[2] = 0x5A5A5A5Au;
        r->s[3] = 0x12345679u;
    }

    /* Прокручуємо стан, щоб перші видачі не несли слідів сівби. */
    for (unsigned i = 0; i < 16; ++i) {
        (void)rng_next(r);
    }
}

uint32_t rng_next(rng_t *r)
{
    const uint32_t result = rotl(r->s[1] * 5u, 7) * 9u;
    const uint32_t t = r->s[1] << 9;

    r->s[2] ^= r->s[0];
    r->s[3] ^= r->s[1];
    r->s[1] ^= r->s[2];
    r->s[0] ^= r->s[3];
    r->s[2] ^= t;
    r->s[3] = rotl(r->s[3], 11);

    return result;
}

uint32_t rng_below(rng_t *r, uint32_t bound)
{
    if (bound == 0u) {
        return 0u;
    }
    /* Відкидаємо хвіст, який не ділиться на bound націло: інакше менші
     * значення трапляються частіше, і джитер тихо збивається до початку вікна. */
    const uint32_t limit = UINT32_MAX - (UINT32_MAX % bound);
    uint32_t v;
    do {
        v = rng_next(r);
    } while (v >= limit);
    return v % bound;
}

uint32_t rng_range(rng_t *r, uint32_t lo, uint32_t hi)
{
    if (hi <= lo) {
        return lo;
    }
    return lo + rng_below(r, hi - lo + 1u);
}

uint32_t jitter_initial_ms(rng_t *r, uint32_t window_ms)
{
    return rng_below(r, window_ms);
}

void backoff_init(backoff_t *b, uint32_t base_ms, uint32_t max_ms)
{
    b->base_ms = (base_ms == 0u) ? 1u : base_ms;
    b->max_ms  = (max_ms < b->base_ms) ? b->base_ms : max_ms;
    b->prev_ms = b->base_ms;
    b->attempts = 0u;
}

uint32_t backoff_next(backoff_t *b, rng_t *r)
{
    /* Верхня межа зростає втричі від ПОПЕРЕДНЬОЇ фактичної затримки, а не від
     * номера спроби: саме через це вузли не збираються назад в одну фазу. */
    uint32_t hi;
    if (b->prev_ms > b->max_ms / 3u) {
        hi = b->max_ms;
    } else {
        hi = b->prev_ms * 3u;
        if (hi > b->max_ms) {
            hi = b->max_ms;
        }
    }

    uint32_t delay = rng_range(r, b->base_ms, hi);
    if (delay > b->max_ms) {
        delay = b->max_ms;
    }

    b->prev_ms = delay;
    b->attempts++;
    return delay;
}

void backoff_reset(backoff_t *b)
{
    b->prev_ms = b->base_ms;
    b->attempts = 0u;
}
