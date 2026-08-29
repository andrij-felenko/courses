#include "cohort.h"

#include "sha256.h"

#define CHI2_CRITICAL_DF99_P01 134.64

uint8_t cohort_bucket_sha256(const uint8_t hw_id[COHORT_ID_LEN],
                             const uint8_t *salt, size_t salt_len)
{
    uint8_t digest[SHA256_DIGEST_LEN];
    sha256_pair(hw_id, COHORT_ID_LEN, salt, salt_len, digest);

    /* Беремо 64 біти дайджесту: залишок від ділення 2^64 на 100 дає зсув
     * порядку 10^-17 на кошик — на тисячі пристроїв він не спостережний.
     * З 32 бітів зсув був би вже 10^-8, і теж прийнятний, але 64 дешевші за
     * розмову про це. */
    uint64_t value = 0;
    for (unsigned i = 0; i < 8; ++i) {
        value = (value << 8) | digest[i];
    }
    return (uint8_t)(value % COHORT_BUCKETS);
}

uint8_t cohort_bucket_fnv1a(const uint8_t hw_id[COHORT_ID_LEN],
                            const uint8_t *salt, size_t salt_len)
{
    uint32_t hash = 2166136261u;

    for (size_t i = 0; i < COHORT_ID_LEN; ++i) {
        hash ^= hw_id[i];
        hash *= 16777619u;
    }
    for (size_t i = 0; i < salt_len; ++i) {
        hash ^= salt[i];
        hash *= 16777619u;
    }

    /* Молодші біти FNV-1a лавинують гірше за старші, а `% 100` бере саме їх.
     * Тому спершу підмішуємо старшу половину в молодшу. */
    hash ^= hash >> 16;
    hash *= 2246822519u;
    hash ^= hash >> 13;

    return (uint8_t)(hash % COHORT_BUCKETS);
}

bool cohort_eligible(uint8_t bucket, uint8_t stage_percent)
{
    if (stage_percent >= COHORT_BUCKETS) {
        return true;    /* фаза 100%: увесь парк */
    }
    return bucket < stage_percent;
}

void cohort_survey(const uint8_t *ids, size_t count,
                   const uint8_t *salt, size_t salt_len,
                   cohort_hash_fn hash, cohort_survey_t *out)
{
    for (unsigned i = 0; i < COHORT_BUCKETS; ++i) {
        out->counts[i] = 0;
    }
    out->total = 0;
    out->chi_square = 0.0;
    out->min_count = 0;
    out->max_count = 0;

    if (ids == NULL || count == 0 || hash == NULL) {
        return;
    }

    for (size_t i = 0; i < count; ++i) {
        const uint8_t bucket = hash(&ids[i * COHORT_ID_LEN], salt, salt_len);
        out->counts[bucket]++;
    }
    out->total = (uint32_t)count;

    const double expected = (double)count / (double)COHORT_BUCKETS;
    out->min_count = out->counts[0];
    out->max_count = out->counts[0];

    for (unsigned i = 0; i < COHORT_BUCKETS; ++i) {
        const uint32_t n = out->counts[i];
        if (n < out->min_count) { out->min_count = n; }
        if (n > out->max_count) { out->max_count = n; }

        const double diff = (double)n - expected;
        out->chi_square += (diff * diff) / expected;
    }
}

bool cohort_survey_acceptable(const cohort_survey_t *s)
{
    /* Менш ніж по п'ять пристроїв на кошик — хі-квадрат уже не судить нічого. */
    if (s->total < 5u * COHORT_BUCKETS) {
        return false;
    }
    return s->chi_square <= CHI2_CRITICAL_DF99_P01;
}
