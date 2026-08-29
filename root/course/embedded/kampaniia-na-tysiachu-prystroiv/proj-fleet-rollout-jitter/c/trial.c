#include "trial.h"

#include <string.h>

bool trial_arm(boot_bank_t target, uint32_t campaign_id,
               uint32_t image_len, uint32_t image_crc)
{
    ota_state_t st;
    ota_state_load(&st);

    /* Покажчик завантаження переставляємо ЛИШЕ після того, як образ у банку
     * зійшовся за контрольною сумою. */
    if (flash_bank_crc(target, image_len) != image_crc) {
        return false;
    }

    st.active_bank        = target;
    st.trial_pending      = true;
    st.boot_failures      = 0;
    st.campaign_id        = campaign_id;
    st.bank_len[target]   = image_len;
    st.bank_crc[target]   = image_crc;

    return ota_state_store(&st);
}

bool trial_begin(trial_t *t, uint32_t timeout_s)
{
    memset(t, 0, sizeof(*t));
    ota_state_load(&t->st);
    t->timeout_s = timeout_s;
    return t->st.trial_pending;
}

trial_result_t trial_step(trial_t *t, uint32_t dt_s,
                          trial_check_t selftest, trial_check_t backend)
{
    if (!t->st.trial_pending) {
        return TRIAL_NOT_PENDING;
    }

    /* Явний дефект не чекає таймауту: сенсорна шина, яка не відповідає, за
     * півгодини сама не полагодиться. */
    if (selftest == TRIAL_CHECK_FAIL || backend == TRIAL_CHECK_FAIL) {
        if (!trial_rollback(t)) {
            /* Відкочуватися нікуди: старий образ не цілий. Прапорець
             * випробування лишаємо — далі рішення за завантажувачем, який
             * перелічить аварійні старти. */
            return TRIAL_RUNNING;
        }
        return TRIAL_ROLLBACK;
    }

    if (selftest == TRIAL_CHECK_PASS) {
        t->selftest_passed = true;
    }
    if (backend == TRIAL_CHECK_PASS) {
        t->backend_confirmed = true;
    }

    /* Обидві умови разом — і тільки разом. */
    if (t->selftest_passed && t->backend_confirmed) {
        return trial_commit(t) ? TRIAL_COMMITTED : TRIAL_RUNNING;
    }

    t->elapsed_s += dt_s;
    if (t->elapsed_s >= t->timeout_s) {
        /* Вузол не впав, але й не довів життєздатності: відкат. */
        return trial_rollback(t) ? TRIAL_ROLLBACK : TRIAL_RUNNING;
    }

    return TRIAL_RUNNING;
}

bool trial_commit(trial_t *t)
{
    t->st.trial_pending = false;
    t->st.boot_failures = 0;
    return ota_state_store(&t->st);
}

bool trial_rollback(trial_t *t)
{
    const boot_bank_t previous = flash_other_bank(t->st.active_bank);

    /* Відкат має сенс лише тоді, коли старий образ на місці й цілий. */
    if (t->st.bank_len[previous] == 0u ||
        flash_bank_crc(previous, t->st.bank_len[previous]) != t->st.bank_crc[previous]) {
        return false;
    }

    t->st.active_bank   = previous;
    t->st.trial_pending = false;
    t->st.boot_failures = 0;
    return ota_state_store(&t->st);
}
