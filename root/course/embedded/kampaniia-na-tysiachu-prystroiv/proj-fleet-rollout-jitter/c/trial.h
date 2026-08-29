/* Випробувальний термін нового образу — сторона застосунку.
 *
 * Прошивка, яка щойно стартувала з нового банку, вважається непідтвердженою,
 * доки не пройде повний цикл самодіагностики Й не обміняється даними з
 * бекендом. Підтвердження одразу після входу в main() — найдорожча помилка
 * кампанії: вузол, який падає через двадцять секунд на TLS, лишається таким
 * назавжди. */
#ifndef TRIAL_H
#define TRIAL_H

#include <stdbool.h>
#include <stdint.h>

#include "flash.h"

typedef enum {
    TRIAL_CHECK_PENDING = 0,   /* перевірка ще триває           */
    TRIAL_CHECK_PASS    = 1,   /* пройдена повністю             */
    TRIAL_CHECK_FAIL    = -1   /* зафіксовано дефект            */
} trial_check_t;

typedef enum {
    TRIAL_RUNNING,      /* випробування триває                     */
    TRIAL_COMMITTED,    /* образ прийнято остаточно                */
    TRIAL_ROLLBACK,     /* стан переставлено на старий банк, треба перезавантаження */
    TRIAL_NOT_PENDING   /* цей старт не є випробуванням            */
} trial_result_t;

typedef struct {
    ota_state_t st;
    uint32_t    timeout_s;
    uint32_t    elapsed_s;
    bool        selftest_passed;
    bool        backend_confirmed;
} trial_t;

/* Записати образ у неактивний банк уже вдалося: переставляємо покажчик
 * завантаження й піднімаємо прапорець випробування. */
bool trial_arm(boot_bank_t target, uint32_t campaign_id,
               uint32_t image_len, uint32_t image_crc);

/* Старт застосунку: читаємо стан. Хибне значення — звичайний старт. */
bool trial_begin(trial_t *t, uint32_t timeout_s);

/* Крок випробування; викликається з головного циклу разом із годинником. */
trial_result_t trial_step(trial_t *t, uint32_t dt_s,
                          trial_check_t selftest, trial_check_t backend);

/* Ручні переходи — на випадок, коли рішення приймає сам застосунок. */
bool trial_commit(trial_t *t);
bool trial_rollback(trial_t *t);

#endif /* TRIAL_H */
