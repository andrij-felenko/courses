#include "debounce.h"

#include "fm_time.h"

void fm_debounce_init(fm_debounce_t *d, bool initial)
{
    if (!d) {
        return;
    }
    d->state          = initial;
    d->candidate      = initial;
    d->cand_since_ms  = 0u;
    d->state_since_ms = 0u;
    d->primed         = false;
}

bool fm_debounce_update(fm_debounce_t *d, bool raw, uint32_t now_ms,
                        uint32_t rise_ms, uint32_t fall_ms)
{
    if (!d) {
        return raw;
    }

    if (!d->primed) {
        /* Перший такт після ввімкнення живлення: витримувати нема від чого —
           часової бази ще немає. Беремо сире значення як стійке. */
        d->primed         = true;
        d->state          = raw;
        d->candidate      = raw;
        d->cand_since_ms  = now_ms;
        d->state_since_ms = now_ms;
        return d->state;
    }

    if (raw == d->state) {
        /* Сире значення повернулося до стійкого — кандидат більше не потрібен,
           і накопичена ним витримка згоряє: саме це й гасить деренчання. */
        d->candidate     = raw;
        d->cand_since_ms = now_ms;
        return d->state;
    }

    if (raw != d->candidate) {
        d->candidate     = raw;
        d->cand_since_ms = now_ms;
    }

    /* Нульова витримка означає «того ж такту»: саме так знімається дозвіл, коли
       охоронець провалився. Перевірку робимо тут, а не наступним викликом. */
    const uint32_t need = raw ? rise_ms : fall_ms;

    if (fm_elapsed(now_ms, d->cand_since_ms, need)) {
        d->state          = raw;
        d->state_since_ms = now_ms;
    }
    return d->state;
}

uint32_t fm_debounce_held_ms(const fm_debounce_t *d, uint32_t now_ms)
{
    if (!d || !d->primed) {
        return 0u;
    }
    return fm_age_ms(now_ms, d->state_since_ms);
}
