/* rto.c — цілочисельний оцінювач таймауту повтору.
 *
 * Якобсон (RFC 6298) у фіксованій комі, без жодної операції з float:
 *   srtt_scaled   = SRTT · 8    → множення на 1/8 це зсув >> 3
 *   rttvar_scaled = RTTVAR · 4  → множення на 1/4 це зсув >> 2
 *   RTO = SRTT + 4·RTTVAR = (srtt_scaled >> 3) + rttvar_scaled
 */
#include "arq.h"

static void rto_recompute(arq_rto *e)
{
    uint32_t rto = (e->srtt_scaled >> 3) + e->rttvar_scaled;
    if (rto < ARQ_MIN_RTO_MS) {
        rto = ARQ_MIN_RTO_MS; /* нижче гранулярності системного тіку сенсу немає */
    }
    if (rto > ARQ_MAX_RTO_MS) {
        rto = ARQ_MAX_RTO_MS;
    }
    e->rto_ms = rto;
}

void arq_rto_init(arq_rto *e)
{
    e->srtt_scaled   = ARQ_INITIAL_RTO_MS << 3;
    e->rttvar_scaled = (ARQ_INITIAL_RTO_MS / 2u) << 2;
    e->rto_ms        = ARQ_INITIAL_RTO_MS;
    e->has_sample    = false;
}

void arq_rto_update(arq_rto *e, uint32_t sample_ms)
{
    if (sample_ms == 0) {
        sample_ms = 1; /* тік таймера 1 мс: нульового RTT не буває */
    }

    if (!e->has_sample) {
        /* Перший вимір задає оцінку цілком (RFC 6298 §2.2). */
        e->srtt_scaled   = sample_ms << 3;
        e->rttvar_scaled = (sample_ms / 2u) << 2;
        e->has_sample    = true;
    } else {
        const int32_t err = (int32_t)sample_ms - (int32_t)(e->srtt_scaled >> 3);
        e->srtt_scaled = (uint32_t)((int32_t)e->srtt_scaled + err);

        const int32_t abs_err = (err < 0) ? -err : err;
        int32_t var = (int32_t)e->rttvar_scaled + abs_err - (int32_t)(e->rttvar_scaled >> 2);
        if (var < 0) {
            var = 0; /* захист від від'ємного відхилення на різкому стрибку */
        }
        e->rttvar_scaled = (uint32_t)var;
    }

    /* Свіжий вимір перераховує RTO з нуля — і цим сам скидає накопичене
       подвоєння Карна. Окремої «команди відновлення» протоколу не треба. */
    rto_recompute(e);
}

void arq_rto_backoff(arq_rto *e)
{
    uint32_t doubled = e->rto_ms * 2u;
    if (doubled > ARQ_MAX_RTO_MS) {
        doubled = ARQ_MAX_RTO_MS;
    }
    e->rto_ms = doubled;
}

uint32_t arq_rto_get(const arq_rto *e)
{
    return e->rto_ms;
}

uint32_t arq_rto_srtt(const arq_rto *e)
{
    return e->srtt_scaled >> 3;
}
