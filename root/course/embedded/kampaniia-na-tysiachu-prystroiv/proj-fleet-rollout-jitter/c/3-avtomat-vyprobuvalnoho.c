#include <stdint.h>
#include <stdbool.h>

typedef enum {
    BOOT_BANK_A = 0,
    BOOT_BANK_B = 1
} boot_bank_t;

typedef struct {
    boot_bank_t active_bank;
    uint32_t    health_timeout_sec;
    uint32_t    elapsed_healthy_sec;
    uint8_t     reboot_failures_count;
    bool        is_confirmed_stable;
} trial_boot_controller_t;

#define MAX_ALLOWED_CRASHES 3

void trial_boot_init(trial_boot_controller_t *c, boot_bank_t bank, uint32_t timeout_sec) {
    c->active_bank = bank;
    c->health_timeout_sec = timeout_sec;
    c->elapsed_healthy_sec = 0;
    c->reboot_failures_count = 0;
    c->is_confirmed_stable = false;
}

/* Викликається періодично з головного циклу (наприклад, кожні 10 секунд) */
bool trial_boot_step(trial_boot_controller_t *c, uint32_t dt_sec, bool hardware_self_test_ok) {
    if (c->is_confirmed_stable) {
        return true; /* Образ уже остаточно прийнятий */
    }

    if (!hardware_self_test_ok) {
        /* Критичний дефект периферії -> негайний відкат */
        c->active_bank = (c->active_bank == BOOT_BANK_B) ? BOOT_BANK_A : BOOT_BANK_B;
        return false;
    }

    c->elapsed_healthy_sec += dt_sec;
    if (c->elapsed_healthy_sec >= c->health_timeout_sec) {
        c->is_confirmed_stable = true;
        c->reboot_failures_count = 0;
        return true;
    }

    return true;
}

boot_bank_t trial_boot_get_safe_bank(const trial_boot_controller_t *c) {
    return c->active_bank;
}
