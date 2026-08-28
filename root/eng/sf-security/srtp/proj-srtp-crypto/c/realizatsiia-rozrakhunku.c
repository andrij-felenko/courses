#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t roc;      /* Лічильник переповнень (Rollover Counter) */
    uint16_t s_l;      /* Найвищий підтверджений номер послідовності */
    bool initialized;  /* Прапорець отримання першого пакета */
} srtp_roc_state_t;

/* Оцінка 48-бітного індексу без зміни внутрішнього стану */
uint64_t srtp_estimate_index(const srtp_roc_state_t *state, uint16_t seq, uint32_t *out_roc) {
    if (!state->initialized) {
        if (out_roc) *out_roc = 0;
        return (uint64_t)seq;
    }

    uint32_t roc_est = state->roc;
    if (state->s_l < 32768) {
        if ((uint16_t)(seq - state->s_l) > 32768) {
            roc_est = (state->roc > 0) ? state->roc - 1 : 0;
        }
    } else {
        if ((uint16_t)(state->s_l - seq) > 32768) {
            roc_est = state->roc + 1;
        }
    }

    if (out_roc) *out_roc = roc_est;
    return (((uint64_t)roc_est) << 16) | seq;
}

/* Фіксація нового підтвердженого номера після перевірки автентичності */
void srtp_update_roc_state(srtp_roc_state_t *state, uint16_t seq, uint32_t roc_est) {
    if (!state->initialized) {
        state->s_l = seq;
        state->roc = roc_est;
        state->initialized = true;
        return;
    }

    uint64_t new_idx = (((uint64_t)roc_est) << 16) | seq;
    uint64_t cur_idx = (((uint64_t)state->roc) << 16) | state->s_l;

    if (new_idx > cur_idx) {
        state->s_l = seq;
        state->roc = roc_est;
    }
}
