/* Розмазування навантаження в часі: початковий джитер і повтори за
 * Decorrelated Jitter. Тут же сівба генератора — саме на ній кампанії й
 * ламаються, коли тисяча вузлів дістає однакову «випадкову» затримку. */
#ifndef JITTER_H
#define JITTER_H

#include <stdbool.h>
#include <stdint.h>

/* xoshiro128** — чотири слова стану, швидкий і без множення 64×64. */
typedef struct {
    uint32_t s[4];
} rng_t;

/* Сівба з апаратних джерел ентропії ПЛЮС унікальний ідентифікатор чипа.
 * Ідентифікатор тут не заради випадковості, а заради гарантії: навіть коли на
 * платі не працює жодне джерело, два вузли не підуть у мережу в одну мілісекунду. */
void rng_seed_from_hardware(rng_t *r, const uint8_t hw_id[16]);

uint32_t rng_next(rng_t *r);

/* Рівномірне число в [0, bound) без зсуву за модулем. */
uint32_t rng_below(rng_t *r, uint32_t bound);

/* Рівномірне число в [lo, hi]; якщо hi <= lo, повертає lo. */
uint32_t rng_range(rng_t *r, uint32_t lo, uint32_t hi);

/* Початкова затримка вузла в межах вікна фази: пік перетворюється на потік. */
uint32_t jitter_initial_ms(rng_t *r, uint32_t window_ms);

/* Повтор після обриву: t = min(T_max, Uniform(T_base, t_попередній · 3)). */
typedef struct {
    uint32_t base_ms;
    uint32_t max_ms;
    uint32_t prev_ms;
    uint32_t attempts;
} backoff_t;

void     backoff_init(backoff_t *b, uint32_t base_ms, uint32_t max_ms);
uint32_t backoff_next(backoff_t *b, rng_t *r);
void     backoff_reset(backoff_t *b);

#endif /* JITTER_H */
