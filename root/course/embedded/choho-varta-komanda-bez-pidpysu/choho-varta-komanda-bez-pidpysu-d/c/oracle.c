#include "oracle.h"

#include "ct.h"

#include <string.h>

/* Одна зчитана пара байтів коштує стільки умовних одиниць часу. */
#define COST_PER_BYTE 16u

/* Розкид вимірювання: 0..JITTER_SPAN одиниць на кожну відповідь.
   Дві одиниці байта — сигнал одного байта тоне в шумі, і одиничний
   постріл нічого не каже. Нападнику потрібне усереднення. */
#define JITTER_SPAN 32u

static uint32_t xorshift32(uint32_t *state)
{
    uint32_t x = *state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    *state = x;
    return x;
}

/*
 * Наївне звіряння — рівно те, що робить memcmp: іде зліва направо й
 * зупиняється на першому незбігу. Повертає кількість байтів, які приймач
 * ВСТИГ прочитати, перш ніж ухвалити рішення.
 */
static uint32_t naive_compare(const uint8_t *guess, const uint8_t *tag, int *equal)
{
    uint32_t read = 0;

    *equal = 1;
    while (read < TAG_LEN) {
        read++;
        if (guess[read - 1u] != tag[read - 1u]) {
            *equal = 0;
            break;
        }
    }
    return read;
}

void oracle_init(oracle *o, const uint8_t tag[TAG_LEN], oracle_mode mode, uint32_t seed)
{
    memcpy(o->tag, tag, TAG_LEN);
    o->mode = mode;
    o->queries = 0;
    /* xorshift не терпить нульового стану — застрягає на нулі назавжди. */
    o->noise_state = (seed != 0u) ? seed : 0x1234567u;
    o->last_cost = 0;
}

int oracle_ask(oracle *o, const uint8_t guess[TAG_LEN])
{
    uint32_t read_bytes;
    uint32_t jitter;
    int equal = 0;

    o->queries++;

    if (o->mode == ORACLE_NAIVE) {
        read_bytes = naive_compare(guess, o->tag, &equal);
    } else {
        equal = (ct_verify(guess, o->tag, TAG_LEN) == 0);
        read_bytes = TAG_LEN; /* прочитано все, хоч би де був незбіг */
    }

    jitter = xorshift32(&o->noise_state) % (JITTER_SPAN + 1u);
    o->last_cost = read_bytes * COST_PER_BYTE + jitter;

    return equal;
}

uint32_t oracle_last_cost(const oracle *o)
{
    return o->last_cost;
}

void oracle_destroy(oracle *o)
{
    ct_wipe(o->tag, TAG_LEN);
    o->last_cost = 0;
}
