#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define DEDUP_WIN_BITS    256u                      /* глибина історії, пакетів */
#define DEDUP_WIN_WORDS   (DEDUP_WIN_BITS / 64u)
#define DEDUP_MAX_SRC     8u
#define DEDUP_MAX_BEARER  4u
#define DEDUP_IDLE_MS     5000u                     /* коли слот джерела вільний */

typedef enum {
    DEDUP_FIRST,        /* перша копія — віддаємо застосунку */
    DEDUP_COPY,         /* копія вже баченого — гасимо */
    DEDUP_STALE,        /* старіше за глибину історії — гасимо й рахуємо */
    DEDUP_EPOCH_RESET,  /* джерело перезапустилося: історію скинуто, пакет віддано */
    DEDUP_NO_SLOT       /* таблиця джерел переповнена */
} dedup_verdict_t;

typedef struct {
    uint32_t src_id;
    uint16_t epoch;
    uint32_t top_seq;                    /* найбільший бачений номер */
    uint64_t win[DEDUP_WIN_WORDS];       /* біт k ↔ пакет top_seq - k */
    uint32_t last_ms;
    bool     used;
    bool     primed;
} dedup_src_t;

typedef struct {
    dedup_src_t src[DEDUP_MAX_SRC];
    uint32_t first_by_bearer[DEDUP_MAX_BEARER];
    uint32_t copy_by_bearer[DEDUP_MAX_BEARER];
} dedup_ctx_t;

static void win_clear(uint64_t *w) {
    memset(w, 0, sizeof(uint64_t) * DEDUP_WIN_WORDS);
}

/* Зсув історії вліво на k позицій. Зсув на >= 64 в C — невизначена поведінка,
   тому і слова, і біти рахуємо окремо, а нульовий зсув обробляємо явно. */
static void win_shift(uint64_t *w, uint32_t k) {
    if (k >= DEDUP_WIN_BITS) { win_clear(w); return; }

    const uint32_t words = k / 64u;
    const uint32_t bits  = k % 64u;

    for (int32_t i = (int32_t)DEDUP_WIN_WORDS - 1; i >= 0; --i) {
        const int32_t s = i - (int32_t)words;
        uint64_t v = 0;
        if (s >= 0) {
            v = w[s] << bits;
            if (bits != 0u && s > 0) {
                v |= w[s - 1] >> (64u - bits);
            }
        }
        w[i] = v;
    }
}

static bool win_test(const uint64_t *w, uint32_t k) {
    return ((w[k / 64u] >> (k % 64u)) & 1ULL) != 0ULL;
}

static void win_set(uint64_t *w, uint32_t k) {
    w[k / 64u] |= 1ULL << (k % 64u);
}

/* Пошук слота джерела: точний збіг, вільний слот або найстаріший мовчазний. */
static dedup_src_t *src_slot(dedup_ctx_t *ctx, uint32_t src_id, uint32_t now_ms) {
    dedup_src_t *spare = NULL;

    for (uint32_t i = 0; i < DEDUP_MAX_SRC; ++i) {
        dedup_src_t *s = &ctx->src[i];
        if (s->used && s->src_id == src_id) {
            return s;
        }
        if (!s->used) {
            if (spare == NULL) spare = s;
        } else if ((uint32_t)(now_ms - s->last_ms) > DEDUP_IDLE_MS) {
            spare = s;
        }
    }

    if (spare == NULL) return NULL;

    memset(spare, 0, sizeof(*spare));
    spare->src_id = src_id;
    spare->used   = true;
    return spare;
}

dedup_verdict_t dedup_check(dedup_ctx_t *ctx, uint32_t src_id, uint16_t epoch,
                            uint32_t seq, uint8_t bearer, uint32_t now_ms) {
    dedup_src_t *s = src_slot(ctx, src_id, now_ms);
    if (s == NULL) return DEDUP_NO_SLOT;

    s->last_ms = now_ms;

    /* Перший пакет джерела або нова епоха після рестарту борту. */
    if (!s->primed || s->epoch != epoch) {
        const bool was_primed = s->primed;
        s->epoch   = epoch;
        s->top_seq = seq;
        s->primed  = true;
        win_clear(s->win);
        win_set(s->win, 0);
        if (bearer < DEDUP_MAX_BEARER) ctx->first_by_bearer[bearer]++;
        return was_primed ? DEDUP_EPOCH_RESET : DEDUP_FIRST;
    }

    const int32_t delta = (int32_t)(seq - s->top_seq);

    if (delta > 0) {                       /* новий максимум: історія їде вліво */
        win_shift(s->win, (uint32_t)delta);
        win_set(s->win, 0);
        s->top_seq = seq;
        if (bearer < DEDUP_MAX_BEARER) ctx->first_by_bearer[bearer]++;
        return DEDUP_FIRST;
    }

    const uint32_t back = (uint32_t)(-delta);

    if (back >= DEDUP_WIN_BITS) {          /* глибше за історію — судити не можемо */
        if (bearer < DEDUP_MAX_BEARER) ctx->copy_by_bearer[bearer]++;
        return DEDUP_STALE;
    }

    if (win_test(s->win, back)) {          /* копію вже пропускали */
        if (bearer < DEDUP_MAX_BEARER) ctx->copy_by_bearer[bearer]++;
        return DEDUP_COPY;
    }

    win_set(s->win, back);                 /* запізніла, але перша копія */
    if (bearer < DEDUP_MAX_BEARER) ctx->first_by_bearer[bearer]++;
    return DEDUP_FIRST;
}
