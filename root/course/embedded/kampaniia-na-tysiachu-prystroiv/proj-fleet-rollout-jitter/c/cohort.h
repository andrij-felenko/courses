/* Детерміноване розбиття парку на когорти 0..99.
 *
 * Вузол рахує свій номер сам: сервер не тримає списків, а номер міняється від
 * кампанії до кампанії разом із сіллю з маніфесту. */
#ifndef COHORT_H
#define COHORT_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define COHORT_BUCKETS 100u
#define COHORT_ID_LEN  16u

/* SHA-256(hw_id || salt) % 100 — основний варіант. */
uint8_t cohort_bucket_sha256(const uint8_t hw_id[COHORT_ID_LEN],
                             const uint8_t *salt, size_t salt_len);

/* FNV-1a — для кристалів без прискорювача криптографії. Дешевший на порядок,
 * але якість розподілу треба перевіряти на всьому парку (cohort_survey). */
uint8_t cohort_bucket_fnv1a(const uint8_t hw_id[COHORT_ID_LEN],
                            const uint8_t *salt, size_t salt_len);

typedef uint8_t (*cohort_hash_fn)(const uint8_t hw_id[COHORT_ID_LEN],
                                  const uint8_t *salt, size_t salt_len);

/* Вузол бере оновлення, коли його номер потрапив під поріг поточної фази:
 * фаза 1% — це кошики 0, фаза 25% — кошики 0..24. */
bool cohort_eligible(uint8_t bucket, uint8_t stage_percent);

/* Зріз розподілу по всьому парку — рахується на стенді перед кампанією. */
typedef struct {
    uint32_t counts[COHORT_BUCKETS];
    uint32_t total;
    uint32_t min_count;
    uint32_t max_count;
    double   chi_square;   /* 99 ступенів вільності */
} cohort_survey_t;

void cohort_survey(const uint8_t *ids, size_t count,
                   const uint8_t *salt, size_t salt_len,
                   cohort_hash_fn hash, cohort_survey_t *out);

/* Критичне значення хі-квадрат для 99 ступенів вільності на рівні 0.01 ≈ 134.6.
 * Більше — розподіл нерівномірний, таку хеш-функцію в кампанію не пускаємо. */
bool cohort_survey_acceptable(const cohort_survey_t *s);

#endif /* COHORT_H */
